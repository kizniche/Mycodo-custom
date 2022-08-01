# coding=utf-8
#
#  custom_function_coolbot_clone_v1_1.py - Coolbot clone function
#
#  Copyright (C) 2022  Kyle T. Gabriel
#
#  This file is part of Mycodo
#
#  Mycodo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Mycodo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
#
#  Contact at kylegabriel.com
#
import threading
import time
import timeit
from flask_babel import lazy_gettext
from mycodo.databases.models import Conversion
from mycodo.databases.models import CustomController
from mycodo.functions.base_function import AbstractFunction
from mycodo.inputs.sensorutils import convert_from_x_to_y_unit
from mycodo.mycodo_client import DaemonControl
from mycodo.utils.constraints_pass import constraints_pass_positive_or_zero_value
from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.utils.database import db_retrieve_table_daemon
from mycodo.utils.system_pi import get_measurement
from mycodo.utils.system_pi import return_measurement_info


FUNCTION_INFORMATION = {
    'function_name_unique': 'COOLBOT_CLONE_V1_1',
    'function_name': 'CoolBot Clone (v1.1)',

    'message': 'This controller is a CoolBot cone, which will provide the functionality of a CoolBot. '
               'Requirements: Output to power a heater attached to the AC temperature sensor '
               '(disconnected from the AC airway), a temperature sensor to measure the room, '
               'and a temperature sensor attached to the condenser to detect freezing.',

    'options_enabled': [
        'custom_options'
    ],
    'options_disabled': [
        'measurements_select',
        'measurements_configure'
    ],

    'custom_options': [
        {
            'id': 'start_offset',
            'type': 'integer',
            'default_value': 30,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Start Offset (seconds)'),
            'phrase': lazy_gettext('Wait before starting the controller')
        },
        {
            'id': 'period',
            'type': 'integer',
            'default_value': 120,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Period (seconds)'),
            'phrase': lazy_gettext('How often to check the temperature and adjust AC')
        },
        {
            'type': 'new_line'
        },
        {
            'id': 'in_temp_condenser',
            'type': 'select_measurement',
            'default_value': '',
            'options_select': [
                'Input',
                'Function'
            ],
            'name': lazy_gettext('Input: Condenser Temperature'),
            'phrase': lazy_gettext('The temperature sensor attached to the AC condenser')
        },
        {
            'id': 'in_temp_condenser_max_age',
            'type': 'integer',
            'default_value': 120,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Condenser Temperature Max Age (seconds)'),
            'phrase': lazy_gettext('The maximum allowed age of the condenser temperature measurement. '
                                   'If older than this value, the system shuts down.')
        },
        {
            'type': 'new_line'
        },
        {
            'id': 'in_temp_room',
            'type': 'select_measurement',
            'default_value': '',
            'options_select': [
                'Input',
                'Function'
            ],
            'name': lazy_gettext('Input: Room Temperature'),
            'phrase': lazy_gettext('The temperature sensor measuring the temperature in the room')
        },
        {
            'id': 'in_temp_room_max_age',
            'type': 'integer',
            'default_value': 120,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Room Temperature Max Age (seconds)'),
            'phrase': lazy_gettext('The maximum allowed age of the room temperature measurement. '
                                   'If older than this value, the system shuts down.')
        },
        {
            'type': 'new_line'
        },
        {
            'id': 'out_ac_heater',
            'type': 'select_measurement_channel',
            'default_value': '',
            'required': True,
            'options_select': [
                'Output_Channels_Measurements',
            ],
            'name': lazy_gettext('Output: Heater'),
            'phrase': lazy_gettext('The output that heats the AC temperature sensor')
        },
        {
            'type': 'new_line'
        },
        {
            'id': 'setpoint_temperature',
            'type': 'float',
            'default_value': 10.5,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Temperature Setpoint (°C)'),
            'phrase': lazy_gettext('The desired temperature')
        },
        {
            'id': 'temperature_hysteresis',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_or_zero_value,
            'name': lazy_gettext('Temperature Hysteresis (°C)'),
            'phrase': lazy_gettext('How much above and below the setpoint to allow the temperature to oscillate')
        },
        {
            'id': 'temperature_freeze',
            'type': 'float',
            'default_value': 4.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_or_zero_value,
            'name': lazy_gettext('Freeze Temperature (°C)'),
            'phrase': lazy_gettext('The temperature of the condenser to shut off the AC to allow to thaw')
        }
    ]
}


class CustomModule(AbstractFunction):
    """
    Class to operate custom controller
    """
    def __init__(self, function, testing=False):
        threading.Thread.__init__(self)
        super(CustomModule, self).__init__(function, testing=testing, name=__name__)

        self.is_setup = False
        self.timer_loop = time.time()
        self.control = DaemonControl()

        # Initialize custom options
        self.start_offset = None
        self.period = None
        self.in_temp_condenser_device_id = None
        self.in_temp_condenser_measurement_id = None
        self.in_temp_condenser_max_age = None
        self.in_temp_room_device_id = None
        self.in_temp_room_measurement_id = None
        self.in_temp_room_max_age = None
        self.out_ac_heater_device_id = None
        self.out_ac_heater_measurement_id = None
        self.out_ac_heater_channel_id = None
        self.output_ac_heater_channel = None
        self.setpoint_temperature = None
        self.temperature_hysteresis = None
        self.temperature_freeze = None

        self.temp_direction = None
        self.temp_upper = None
        self.temp_lower = None

        custom_function = db_retrieve_table_daemon(
            CustomController, unique_id=self.unique_id)
        self.setup_custom_options(
            FUNCTION_INFORMATION['custom_options'], custom_function)

        if not testing:
            self.try_initialize()

    def initialize(self):
        self.temp_upper = self.setpoint_temperature + self.temperature_hysteresis
        self.temp_lower = self.setpoint_temperature - self.temperature_hysteresis
        self.output_ac_heater_channel = self.get_output_channel_from_channel_id(
            self.out_ac_heater_channel_id)
        self.timer_loop = time.time() + self.start_offset
        self.is_setup = True

    def loop(self):
        if self.timer_loop > time.time():
            return

        while self.timer_loop < time.time():
            self.timer_loop += self.period

        temperature_condenser = self.get_ac_condenser_temperature()
        temperature_room = self.get_room_temperature()

        if not temperature_condenser or not temperature_room:
            self.logger.error("Could not get condenser or room temperature. Turning off AC")
            self.control.output_off(self.out_ac_heater_device_id, output_channel=self.output_ac_heater_channel)
            return

        self.logger.debug(f"Temperatures: Room = {temperature_room} C, Condenser = {temperature_condenser} C")

        if temperature_condenser <= self.temperature_freeze:
            # condenser too cold, stop cooling
            self.logger.debug(
                f"{temperature_condenser} C < {self.temperature_freeze} C (Freezing): "
                f"Turning heater output ({self.out_ac_heater_device_id}) off")
            self.control.output_off(self.out_ac_heater_device_id, output_channel=self.output_ac_heater_channel
            )
        elif temperature_room > self.temp_upper and (not self.temp_direction or self.temp_direction == "heat"):
            # Temperature is too high, start cooling
            self.temp_direction = "cool"
            self.logger.debug(
                f"{temperature_room} C > {self.temp_upper} C: "
                f"Turning heater output ({self.out_ac_heater_device_id}) on")
            self.control.output_on(self.out_ac_heater_device_id, output_channel=self.output_ac_heater_channel)
        elif temperature_room < self.temp_lower and (not self.temp_direction or self.temp_direction == "cool"):
            # Temperature is too low, stop cooling
            self.temp_direction = "heat"
            self.logger.debug(
                f"{temperature_room} C < {self.temp_lower} C: "
                f"Turning heater output ({self.out_ac_heater_device_id}) off")
            self.control.output_off(
              self.out_ac_heater_device_id, output_channel=self.output_ac_heater_channel)

    def get_ac_condenser_temperature(self):
        """Get condenser temperature"""
        last_measurement = self.get_last_measurement(
            self.in_temp_condenser_device_id,
            self.in_temp_condenser_measurement_id,
            max_age=self.in_temp_condenser_max_age)

        if last_measurement:
            self.logger.debug(
                "Most recent timestamp and measurement for "
                f"in_temp_condenser: {last_measurement[0]}, {last_measurement[1]}")
            device_measurement = get_measurement(
                self.in_temp_condenser_measurement_id)
            conversion = db_retrieve_table_daemon(
                Conversion, unique_id=device_measurement.conversion_id)
            channel, unit, measurement = return_measurement_info(
                device_measurement, conversion)
            temp_c = convert_from_x_to_y_unit(unit, 'C', last_measurement[1])
            return temp_c
        else:
            self.logger.debug(
                "Could not find a measurement in the database for in_temp_condenser "
                f"device ID {self.in_temp_condenser_device_id} and "
                f"measurement ID {self.in_temp_condenser_measurement_id}")

    def get_room_temperature(self):
        """Get condenser temperature"""
        last_measurement = self.get_last_measurement(
            self.in_temp_room_device_id,
            self.in_temp_room_measurement_id,
            max_age=self.in_temp_room_max_age)

        if last_measurement:
            self.logger.debug(
                "Most recent timestamp and measurement for "
                f"in_temp_room: {last_measurement[0]}, {last_measurement[1]}")
            device_measurement = get_measurement(
                self.in_temp_room_measurement_id)
            conversion = db_retrieve_table_daemon(
                Conversion, unique_id=device_measurement.conversion_id)
            channel, unit, measurement = return_measurement_info(
                device_measurement, conversion)
            temp_c = convert_from_x_to_y_unit(unit, 'C', last_measurement[1])
            return temp_c
        else:
            self.logger.debug(
                "Could not find a measurement in the database for in_temp_room "
                f"device ID {self.in_temp_room_device_id} and "
                f"measurement ID {self.in_temp_room_measurement_id}")

    def stop_function(self):
        self.logger.debug(f"Turning heater output ({self.out_ac_heater_device_id}) off")
        self.control.output_off(self.out_ac_heater_device_id, output_channel=self.output_ac_heater_channel)