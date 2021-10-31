# coding=utf-8
import datetime
import json
import time
import urllib.request

import requests
from flask_babel import lazy_gettext

from mycodo.config import SQL_DATABASE_MYCODO
from mycodo.databases.models import Conversion
from mycodo.databases.models import Input
from mycodo.databases.utils import session_scope
from mycodo.inputs.base_input import AbstractInput
from mycodo.utils.database import db_retrieve_table_daemon
from mycodo.utils.influx import add_measurements_influxdb
from mycodo.utils.influx import parse_measurement

MYCODO_DB_PATH = 'sqlite:///' + SQL_DATABASE_MYCODO


def constraints_pass_positive_value(mod_input, value):
    """
    Check if the user input is acceptable
    :param mod_input: SQL object with user-saved Input options
    :param value: float or int
    :return: tuple: (bool, list of strings)
    """
    errors = []
    all_passed = True
    # Ensure value is positive
    if value <= 0:
        all_passed = False
        errors.append("Must be a positive value")
    if value > 100:
        all_passed = False
        errors.append("Number of measurements cannot exceed 100")
    return all_passed, errors, mod_input


# Measurements
measurements_dict = {
    0: {
        'measurement': 'radiation_dose_rate',
        'unit': 'cpm',
        'name': 'cpm'
    },
    1: {
        'measurement': 'radiation_dose_rate',
        'unit': 'uSv_hr',
        'name': 'usv_h'
    }
}


# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'TTN_DATA_STORAGE_GEIGER_TTN_V3',
    'input_manufacturer': 'Moteino Mega/MightOhm',
    'input_name': 'Geiger Counter (TTN/Safecast/GMCMap) (TTN v3)',
    'measurements_name': 'CPM and μSv/hr',
    'measurements_dict': measurements_dict,
    'measurements_use_same_timestamp': False,

    'message': """Requires: Mycodo >= 7.7.0. This Input was designed for use with the Moteino Mega with a LoRaWAN transceiver connected to a MightyOwn Geiger Counter (v1.0). Radiation measurements (CPM and μSv/hr) are transmitted to The Things Network (TTN). Mycodo uses this Input to download the measurements from TTN and transmit them to Safecast and GMC Map. More info at https://github.com/kizniche/Mycodo-custom/tree/master/custom_inputs/geiger%20counter""",

    'options_enabled': [
        'custom_options',
        'measurements_select',
        'period',
        'pre_output',
        'log_level_debug'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'SafecastPy', 'SafecastPy')
    ],

    'interfaces': ['Mycodo'],

    'custom_options': [
        {
            'id': 'application_id',
            'type': 'text',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('TTN Application ID'),
            'phrase': lazy_gettext('The Things Network Application ID')
        },
        {
            'id': 'app_api_key',
            'type': 'text',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('TTN App API Key'),
            'phrase': lazy_gettext('The Things Network Application API Key')
        },
        {
            'id': 'device_id',
            'type': 'text',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('TTN Device ID'),
            'phrase': lazy_gettext('The Things Network Device ID')
        },
        {
            'id': 'send_safecast',
            'type': 'bool',
            'default_value': True,
            'name': lazy_gettext('Send to Safecast'),
            'phrase': lazy_gettext('Send Geiger counter data to Safecast')
        },
        {
            'id': 'safecast_api_key',
            'type': 'text',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('Safecast API Key'),
            'phrase': lazy_gettext('Safecast API Key')
        },
        {
            'id': 'safecast_latitude',
            'type': 'float',
            'default_value': '30.127462',
            'required': True,
            'name': lazy_gettext('Safecast Latitude'),
            'phrase': lazy_gettext('Safecast Latitude in decimal format')
        },
        {
            'id': 'safecast_longitude',
            'type': 'float',
            'default_value': '-79.346743',
            'required': True,
            'name': lazy_gettext('Safecast Longitude'),
            'phrase': lazy_gettext('Safecast Longitude in decimal format')
        },
        {
            'id': 'safecast_device_id',
            'type': 'integer',
            'default_value': '1',
            'required': True,
            'name': lazy_gettext('Safecast Device ID'),
            'phrase': lazy_gettext('Safecast device ID of the geiger counter')
        },
        {
            'id': 'safecast_location_name',
            'type': 'text',
            'default_value': 'Location, USA',
            'required': True,
            'name': lazy_gettext('Safecast Location'),
            'phrase': lazy_gettext('Safecast location name of the Geiger counter')
        },
        {
            'id': 'send_gmcmap',
            'type': 'bool',
            'default_value': True,
            'name': lazy_gettext('Send to GMC Map'),
            'phrase': lazy_gettext('Send Geiger counter data to GMC Map')
        },
        {
            'id': 'gmcmap_account_id',
            'type': 'integer',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('GMC Map Account ID'),
            'phrase': lazy_gettext('GMC Map ID of the user account')
        },
        {
            'id': 'gmcmap_geiger_counter_id',
            'type': 'integer',
            'default_value': '',
            'required': True,
            'name': lazy_gettext('GMC Map Geiger Counter ID'),
            'phrase': lazy_gettext('GMC Map ID of the geiger counter')
        },
    ]
}


class InputModule(AbstractInput):
    """ A sensor support class that retrieves stored data from The Things Network """

    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        self.safecastpy = None
        self.interface = None
        self.period = None
        self.latest_datetime = None
        self.first_run = True

        # Initialize custom options
        self.send_safecast = None
        self.send_gmcmap = None
        self.application_id = None
        self.app_api_key = None
        self.device_id = None
        self.send_safecast = None
        self.safecast_api_key = None
        self.safecast_latitude = None
        self.safecast_longitude = None
        self.safecast_device_id = None
        self.safecast_location_name = None
        self.send_gmcmap = None
        self.gmcmap_account_id = None
        self.gmcmap_geiger_counter_id = None
        # Set custom_options
        self.setup_custom_options(
            INPUT_INFORMATION['custom_options'], input_dev)

        if not testing:
            self.initialize_input()

    def initialize_input(self):
        import SafecastPy

        self.safecastpy = SafecastPy

        self.interface = self.input_dev.interface
        self.period = self.input_dev.period
        self.latest_datetime = self.input_dev.datetime

    def get_new_data(self, past_seconds):
        # Basic implementation. Future development may use more complex library to access API
        endpoint = "https://nam1.cloud.thethings.network/api/v3/as/applications/{app}/devices/{dev}/packages/storage/uplink_message?last={time}&field_mask=up.uplink_message.decoded_payload".format(
            app=self.application_id, dev=self.device_id, time="{}s".format(int(past_seconds)))
        headers = {
            "Authorization": "Bearer {k}".format(k=self.app_api_key),
            'Content-Type': 'application/json'
        }
        timestamp_format = '%Y-%m-%dT%H:%M:%S.%f'

        response = requests.get(endpoint, headers=headers)
        if response.status_code != 200:
            self.logger.info("response.status_code != 200: {}".format(response.reason))
        self.logger.debug("response.content: {}".format(response.content))

        list_dicts = response.content.decode().split("\n")
        self.logger.debug("list_dicts: {}".format(list_dicts))

        cpm_value = None
        cpm_ts = None
        usv_h_value = None
        usv_h_ts = None

        for each_resp in list_dicts:
            if not each_resp:
                continue
            self.logger.debug("each_resp: {}".format(each_resp))

            cpm_value = None
            usv_h_value = None

            try:
                resp_json = json.loads(each_resp)
            except:
                resp_json = {}
            self.logger.debug("resp_json: {}".format(resp_json))

            self.return_dict = measurements_dict.copy()

            try:
                datetime_utc = datetime.datetime.strptime(
                    resp_json['result']['received_at'][:-7], timestamp_format)
            except:
                # Sometimes the original timestamp is in milliseconds
                # instead of nanoseconds. Therefore, remove 3 less digits
                # past the decimal and try again to parse.
                try:
                    datetime_utc = datetime.datetime.strptime(
                        resp_json['result']['received_at'][:-4], timestamp_format)
                except:
                    self.logger.error("Could not parse timestamp: {}".format(
                        resp_json['result']['received_at']))
                    return

            if (not self.latest_datetime or
                    self.latest_datetime < datetime_utc):
                self.latest_datetime = datetime_utc

            for channel in self.return_dict:
                if (self.is_enabled(channel) and
                        self.return_dict[channel]['name'] in resp_json['result']['uplink_message']['decoded_payload'] and
                        resp_json['result']['uplink_message']['decoded_payload'][self.return_dict[channel]['name']] is not None):

                    self.return_dict[channel]['value'] = resp_json['result']['uplink_message']['decoded_payload'][self.return_dict[channel]['name']]
                    self.return_dict[channel]['timestamp_utc'] = datetime_utc

                    if self.return_dict[channel]['unit'] == 'cpm':
                        cpm_value = float(self.return_dict[channel]['value'])
                        cpm_ts = self.return_dict[channel]['timestamp_utc']
                    elif self.return_dict[channel]['unit'] == 'uSv_hr':
                        usv_h_value = float(self.return_dict[channel]['value'])
                        usv_h_ts = self.return_dict[channel]['timestamp_utc']


                    # Convert value/unit if conversion_id present and valid
                    if self.channels_conversion[channel]:
                        conversion = db_retrieve_table_daemon(
                            Conversion, unique_id=self.channels_measurement[channel].conversion_id)
                        if conversion:
                            meas = parse_measurement(
                                self.channels_conversion[channel],
                                self.channels_measurement[channel],
                                self.return_dict,
                                channel,
                                self.return_dict[channel],
                                timestamp=datetime_utc)

                            self.return_dict[channel]['unit'] = meas[channel]['unit']
                            self.return_dict[channel]['value'] = meas[channel]['value']

            if 'value' in self.return_dict[0] and 'value' in self.return_dict[1]:
                self.logger.debug("Adding measurements to influxdb: {}".format(self.return_dict))
                add_measurements_influxdb(
                    self.unique_id, self.return_dict,
                    use_same_timestamp=INPUT_INFORMATION['measurements_use_same_timestamp'])
            else:
                self.logger.debug("No measurements to add to influxdb.")

            # Send uSv/hr to Safecast
            if self.send_safecast and cpm_value and usv_h_value:
                try:
                    safecast = self.safecastpy.SafecastPy(api_key=self.safecast_api_key)
                    measurement_usv = safecast.add_measurement(json={
                        'latitude': self.safecast_latitude,
                        'longitude': self.safecast_longitude,
                        'value': usv_h_value,
                        'unit': self.safecastpy.UNIT_USV,
                        'captured_at': usv_h_ts.isoformat() + '+00:00',
                        'device_id': self.safecast_device_id,
                        'location_name': self.safecast_location_name
                    })
                    measurement_cpm = safecast.add_measurement(json={
                        'latitude': self.safecast_latitude,
                        'longitude': self.safecast_longitude,
                        'value': cpm_value,
                        'unit': self.safecastpy.UNIT_CPM,
                        'captured_at': cpm_ts.isoformat() + '+00:00',
                        'device_id': self.safecast_device_id,
                        'location_name': self.safecast_location_name
                    })
                    self.logger.debug('uSv/hr measurement id: {0}'.format(measurement_usv['id']))
                    self.logger.debug('CPM measurement id: {0}'.format(measurement_cpm['id']))
                except Exception as e:
                    self.logger.error("Error adding data to Safecast: {}".format(e))

        # Send to GMC Map (doesn't accept time, so can only send the latest measurement)
        if (self.send_gmcmap and
                cpm_value and
                usv_h_value):
            try:
                gmcmap = 'http://www.GMCmap.com/log2.asp?AID=02376&GID=22044260632&CPM={cpm:.0f}&uSV={usv:.3f}'.format(
                    aid=self.gmcmap_account_id,
                    gcid=self.gmcmap_geiger_counter_id,
                    cpm=cpm_value,
                    usv=usv_h_value)
                contents = urllib.request.urlopen(gmcmap).read()
                self.logger.debug("GMCMap: {}".format(contents))
            except Exception as e:
                self.logger.error("Error adding data to GMC Map: {}".format(e))

        # set datetime to latest timestamp
        if self.running:
            with session_scope(MYCODO_DB_PATH) as new_session:
                mod_input = new_session.query(Input).filter(
                    Input.unique_id == self.unique_id).first()
                if not mod_input.datetime or mod_input.datetime < self.latest_datetime:
                    mod_input.datetime = self.latest_datetime
                    new_session.commit()

    def get_measurement(self):
        """ Gets the data """
        if self.first_run:
            # Get data for up to 7 days (longest Data Storage Integration
            # stores data) in the past or until last_datetime.
            seconds_seven_days = 604800  # 604800 seconds = 7 days
            seconds_download = seconds_seven_days
            start = time.time()
            self.first_run = False

            if self.latest_datetime:
                utc_now = datetime.datetime.utcnow()
                seconds_since_last = (utc_now - self.latest_datetime).total_seconds()
                if seconds_since_last < seconds_seven_days:
                    seconds_download = seconds_since_last

            if seconds_download == seconds_seven_days:
                self.logger.info(
                    "This appears to be the first data download. "
                    "Downloading and parsing past 7 days of data...".format(
                        seconds_download))
            else:
                self.logger.info(
                    "Downloading and parsing past {} seconds of data...".format(
                        int(seconds_download)))

            self.get_new_data(seconds_download)

            if seconds_download == seconds_seven_days:
                elapsed = time.time() - start
                self.logger.info(
                    "Download and parsing completed in {} seconds.".format(
                        int(elapsed)))
        else:
            self.get_new_data(self.period)

        return {}
