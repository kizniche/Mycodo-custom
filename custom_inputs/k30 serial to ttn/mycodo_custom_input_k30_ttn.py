# coding=utf-8
#
# Example module for measuring with the K30 and sending
# the measurement to a serial device. For accompaniment with
# the The Things Network (TTN) Data Storage Input module
#
# Use this module to send measurements via serial to a
# LoRaWAN-enabled device, which transmits the data to TTN.
#
# Comment will be updated with other code to go along with this module
#
import time

from flask_babel import lazy_gettext

from mycodo.inputs.base_input import AbstractInput
from mycodo.inputs.sensorutils import is_device

airtime_seconds = 0.0515  # 51.5 ms
ttn_max_seconds_transmit_per_day = 30
max_transmissions_per_day = ttn_max_seconds_transmit_per_day / airtime_seconds
min_seconds_between_transmissions = 86400 / max_transmissions_per_day

# Measurements
measurements_dict = {
    0: {
        'measurement': 'co2',
        'unit': 'ppm'
    }
}

# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'K30_TTN',
    'input_manufacturer': 'CO2Meter',
    'input_name': 'K30 (->Serial->TTN)',
    'input_library': 'serial',
    'measurements_name': 'CO2',
    'measurements_dict': measurements_dict,
    'measurements_use_same_timestamp': True,
    'url_manufacturer': 'https://www.co2meter.com/products/k-30-co2-sensor-module',
    'url_datasheet': 'http://co2meters.com/Documentation/Datasheets/DS_SE_0118_CM_0024_Revised9%20(1).pdf',

    'message': "WARNING: This sensor doesn't have reverse-polarity protection, so if you accidentally reverse the "
               "voltage, you will damage the sensor.",

    'options_enabled': [
        'uart_location',
        'uart_baud_rate',
        'period',
        'pre_output'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'serial', 'pyserial')
    ],

    'interfaces': ['UART'],
    'uart_location': '/dev/ttyAMA0',
    'uart_baud_rate': 9600,

    'custom_options': [
        {
            'id': 'serial_device',
            'type': 'text',
            'default_value': '/dev/ttyUSB0',
            'name': lazy_gettext('Serial Device'),
            'phrase': lazy_gettext('The serial device to write to')
        }
    ]
}


class InputModule(AbstractInput):
    """ A sensor support class that monitors the K30's CO2 concentration """

    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        self.timer = 0

        # Initialize custom options
        self.serial_device = None
        # Set custom options
        self.setup_custom_options(
            INPUT_INFORMATION['custom_options'], input_dev)

        if not testing:
            import serial

            self.uart_location = input_dev.uart_location
            self.baud_rate = input_dev.baud_rate
            # Check if device is valid
            self.uart_location = is_device(self.uart_location)
            if self.uart_location:
                try:
                    self.ser = serial.Serial(self.uart_location,
                                             baudrate=self.baud_rate,
                                             timeout=1)
                except serial.SerialException:
                    self.logger.exception('Opening serial')
            else:
                self.logger.error(
                    'Could not open "{dev}". '
                    'Check the device location is correct.'.format(
                        dev=self.uart_location))

            self.serial = serial
            self.serial_send = None
            self.lock_file = "/var/lock/mycodo_ttn.lock"
            self.ttn_serial_error = False
            self.logger.debug(
                "Min time between transmissions: {} seconds".format(
                    min_seconds_between_transmissions))

    def get_measurement(self):
        """ Gets the K30's CO2 concentration in ppmv via UART"""
        if not self.uart_location:  # Don't measure if device isn't validated
            return None

        self.return_dict = measurements_dict.copy()

        co2 = None

        self.ser.flushInput()
        time.sleep(1)
        self.ser.write(bytearray([0xfe, 0x44, 0x00, 0x08, 0x02, 0x9f, 0x25]))
        time.sleep(.01)
        resp = self.ser.read(7)
        if len(resp) != 0:
            high = resp[3]
            low = resp[4]
            co2 = (high * 256) + low

        self.value_set(0, co2)

        try:
            now = time.time()
            if now > self.timer:
                self.timer = now + min_seconds_between_transmissions
                # "K" designates this data belonging to the K30
                string_send = 'K,{}'.format(self.value_get(0))
                self.lock_acquire(self.lock_file, timeout=10)
                if self.locked[self.lock_file]:
                    try:
                        self.serial_send = self.serial.Serial(self.serial_device, 9600)
                        self.serial_send.write(string_send.encode())
                        time.sleep(4)
                    finally:
                        self.lock_release(self.lock_file)
                self.ttn_serial_error = False
        except Exception as e:
            if not self.ttn_serial_error:
                # Only send this error once if it continually occurs
                self.logger.error("TTN: Could not send serial: {}".format(e))
                self.ttn_serial_error = True

        return self.return_dict
