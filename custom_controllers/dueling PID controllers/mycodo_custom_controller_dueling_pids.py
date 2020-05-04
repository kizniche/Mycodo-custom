# coding=utf-8
#
#  mycodo_custom_controller_dueling_pids.py - Custom controller to logically handle dueling PIDs
#
#  Copyright (C) 2017  Kyle T. Gabriel
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

from mycodo.controllers.base_controller import AbstractController
from mycodo.databases.models import CustomController
from mycodo.mycodo_client import DaemonControl
from mycodo.utils.database import db_retrieve_table_daemon


def constraints_pass_positive_value(mod_controller, value):
    """
    Check if the user controller is acceptable
    :param mod_controller: SQL object with user-saved Input options
    :param value: float or int
    :return: tuple: (bool, list of strings)
    """
    errors = []
    all_passed = True
    # Ensure value is positive
    if value <= 0:
        all_passed = False
        errors.append("Must be a positive value")
    return all_passed, errors, mod_controller


CONTROLLER_INFORMATION = {
    'controller_name_unique': 'PID_NON_CONFLICT_CONTROLLER_1_0',
    'controller_name': 'Dueling PIDs (v1.0)',

    'message': 'This Controller will operate two PID controllers that utilize the same output, '
               'allowing rules to define how the shared output is handled when both controllers '
               'desire to modulate it at the same time. Specifically, PID 1 raise output is the '
               'same as PID 2 lower output. Example: The Output is to raise humidity, and PID 1 '
               'raises humidity while PID 2 lowers temperature. Notes: Not designed for PWM outputs, '
               'only duration outputs.',

    'options_enabled': [
        'custom_options'
    ],

    'custom_options': [
        {
            'id': 'period',
            'type': 'float',
            'default_value': 30.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('Period (seconds)'),
            'phrase': lazy_gettext('How often to calculate PID values and modulate outputs')
        },

        # PID 1 options
        {
            'id': 'pid_1_measurement',
            'type': 'select_measurement',
            'default_value': '',
            'options_select': [
                'Input',
                'Math'
            ],
            'name': lazy_gettext('PID 1 Measurement'),
            'phrase': lazy_gettext('Select a measurement for PID 1')
        },
        {
            'id': 'pid_1_max_age',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Max Age'),
            'phrase': lazy_gettext('Max age for PID 1 measurement')
        },
        {
            'id': 'pid_1_direction',
            'type': 'select',
            'default_value': 'raise',
            'options_select': [
                ('raise', 'Raise'),
                ('lower', 'Lower'),
                ('both', 'Both'),
            ],
            'name': lazy_gettext('PID 1 Direction'),
            'phrase': lazy_gettext('Direction to move measured condition for PID 1')
        },
        {
            'id': 'pid_1_setpoint',
            'type': 'float',
            'default_value': 20.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Setpoint'),
            'phrase': lazy_gettext('Setpoint for PID 1')
        },
        {
            'id': 'pid_1_band',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Band'),
            'phrase': lazy_gettext('Band for PID 1')
        },
        {
            'id': 'pid_1_p',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Kp Gain'),
            'phrase': lazy_gettext('Kp gain for PID 1')
        },
        {
            'id': 'pid_1_i',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Ki Gain'),
            'phrase': lazy_gettext('Ki gain for PID 1')
        },
        {
            'id': 'pid_1_d',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 1 Kd Gain'),
            'phrase': lazy_gettext('Kd gain for PID 1')
        },
        {
            'id': 'pid_1_output_raise',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Output'
            ],
            'name': lazy_gettext('PID 1 Output Raise'),
            'phrase': lazy_gettext('Select the output to raise the condition for PID 1. Make this the same output as PID 2 Output Lower.')
        },
        {
            'id': 'pid_1_output_lower',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Output'
            ],
            'name': lazy_gettext('PID 1 Output Lower'),
            'phrase': lazy_gettext('Select the output to lower the condition for PID 1')
        },

        # PID 2 options
        {
            'id': 'pid_2_measurement',
            'type': 'select_measurement',
            'default_value': '',
            'options_select': [
                'Input',
                'Math'
            ],
            'name': lazy_gettext('PID 2 Measurement'),
            'phrase': lazy_gettext('Select a measurement for PID 2')
        },
        {
            'id': 'pid_2_max_age',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Max Age'),
            'phrase': lazy_gettext('Max age for PID 2 measurement')
        },
        {
            'id': 'pid_2_direction',
            'type': 'select',
            'default_value': 'raise',
            'options_select': [
                ('raise', 'Raise'),
                ('lower', 'Lower'),
                ('both', 'Both'),
            ],
            'name': lazy_gettext('PID 2 Direction'),
            'phrase': lazy_gettext('Direction to move measured condition for PID 2')
        },
        {
            'id': 'pid_2_setpoint',
            'type': 'float',
            'default_value': 20.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Setpoint'),
            'phrase': lazy_gettext('Setpoint for PID 2')
        },
        {
            'id': 'pid_2_band',
            'type': 'float',
            'default_value': 0.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Band'),
            'phrase': lazy_gettext('Band for PID 2')
        },
        {
            'id': 'pid_2_p',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Kp Gain'),
            'phrase': lazy_gettext('Kp gain for PID 2')
        },
        {
            'id': 'pid_2_i',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Ki Gain'),
            'phrase': lazy_gettext('Ki gain for PID 2')
        },
        {
            'id': 'pid_2_d',
            'type': 'float',
            'default_value': 1.0,
            'required': True,
            'constraints_pass': constraints_pass_positive_value,
            'name': lazy_gettext('PID 2 Kd Gain'),
            'phrase': lazy_gettext('Kd gain for PID 2')
        },
        {
            'id': 'pid_2_output_raise',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Output'
            ],
            'name': lazy_gettext('PID 2 Output Raise'),
            'phrase': lazy_gettext('Select the output to raise the condition for PID 2')
        },
        {
            'id': 'pid_2_output_lower',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Output'
            ],
            'name': lazy_gettext('PID 2 Output Lower'),
            'phrase': lazy_gettext('Select the output to lower the condition for PID 2. Make this the same output as PID 1 Output Raise.')
        }
    ]
}


class CustomModule(AbstractController, threading.Thread):
    """
    Class to operate custom controller
    """
    def __init__(self, ready, unique_id, testing=False):
        threading.Thread.__init__(self)
        super(CustomModule, self).__init__(ready, unique_id=unique_id, name=__name__)

        self.unique_id = unique_id
        self.log_level_debug = None

        self.control = DaemonControl()

        # Initialize custom options
        self.period = None

        self.pid_1_measurement_device_id = None
        self.pid_1_measurement_measurement_id = None
        self.pid_1_max_age = None
        self.pid_1_direction = None
        self.pid_1_setpoint = None
        self.pid_1_band = None
        self.pid_1_p = None
        self.pid_1_i = None
        self.pid_1_d = None
        self.pid_1_output_raise_id = None  # PID 1 Raise is the same output as PID 2 Lower
        self.pid_1_output_lower_id = None

        self.pid_2_measurement_device_id = None
        self.pid_2_measurement_measurement_id = None
        self.pid_2_max_age = None
        self.pid_2_direction = None
        self.pid_2_setpoint = None
        self.pid_2_band = None
        self.pid_2_p = None
        self.pid_2_i = None
        self.pid_2_d = None
        self.pid_2_output_raise_id = None
        self.pid_2_output_lower_id = None  # PID 1 Raise is the same output as PID 2 Lower

        # General variables
        self.last_measurement_1 = None
        self.last_measurement_2 = None
        self.pid_1_control_variable = None
        self.pid_2_control_variable = None
        self.period_timer = 0

        # Set custom options
        custom_controller = db_retrieve_table_daemon(
            CustomController, unique_id=unique_id)
        self.setup_custom_options(
            CONTROLLER_INFORMATION['custom_options'], custom_controller)

        if not testing:
            # Initialize PID Controllers
            self.PID_Controller_1 = PIDController(
                self.logger,
                self.pid_1_p,
                self.pid_1_i ,
                self.pid_1_d,
                -100,
                100,
                self.pid_1_direction,
                self.pid_1_band,
                self.pid_1_setpoint)

            self.PID_Controller_2 = PIDController(
                self.logger,
                self.pid_1_p,
                self.pid_1_i,
                self.pid_1_d,
                -100,
                100,
                self.pid_1_direction,
                self.pid_1_band,
                self.pid_1_setpoint)

    def run(self):
        try:
            self.logger.info("Activated in {:.1f} ms".format(
                (timeit.default_timer() - self.thread_startup_timer) * 1000))

            self.ready.set()
            self.running = True

            # Start a loop
            while self.running:
                self.loop()
        except:
            self.logger.exception("Run Error")
        finally:
            self.run_finally()
            self.running = False
            if self.thread_shutdown_timer:
                self.logger.info("Deactivated in {:.1f} ms".format(
                    (timeit.default_timer() - self.thread_shutdown_timer) * 1000))
            else:
                self.logger.error("Deactivated unexpectedly")

    def loop(self):
        if time.time() > self.period_timer:
            while time.time() > self.period_timer:
                self.period_timer = self.period_timer + self.period

            # Get PID 1 measurement and calculate PID control variable
            self.last_measurement_1 = self.get_last_measurement(
                self.pid_1_measurement_device_id,
                self.pid_1_measurement_measurement_id,
                max_age=self.pid_1_max_age)
            self.pid_1_control_variable = self.PID_Controller_1.update_pid_output(
                self.last_measurement_1)

            # Get PID 2 measurement and calculate PID control variable
            self.last_measurement_2 = self.get_last_measurement(
                self.pid_1_measurement_device_id,
                self.pid_1_measurement_measurement_id,
                max_age=self.pid_2_max_age)
            self.pid_2_control_variable = self.PID_Controller_2.update_pid_output(
                self.last_measurement_2)

            # Manipulate output(s) based on control variables
            self.manipulate_output2()

    def initialize_variables(self):
        pass

    def manipulate_output2(self):
        """
        Activate output based on PID control variable and whether
        the manipulation directive is to raise, lower, or both.

        :rtype: None
        """
        # Determine which outputs should be turned off in no measurement is received
        # Note: PID 1 Raise is the same output as PID 2 Lower
        if self.last_measurement_1 is None and self.last_measurement_2 is None:
            # Turn all outputs off if both PIDs don't have measurements
            self.logger.debug("PID 1 and PID 2 last measurements unsuccessful. Turning outputs off.")

            # Turn both outputs for PID 1 off
            if self.pid_1_direction in ['raise', 'both'] and self.pid_1_output_raise_id:
                self.control.output_off(self.pid_1_output_raise_id)
            if self.pid_1_direction in ['lower', 'both'] and self.pid_1_output_lower_id:
                self.control.output_off(self.pid_1_output_lower_id)

            # Turn both outputs for PID 2 off
            if self.pid_2_direction in ['raise', 'both'] and self.pid_2_output_raise_id:
                self.control.output_off(self.pid_2_output_raise_id)
            if self.pid_2_direction in ['lower', 'both'] and self.pid_2_output_lower_id:
                self.control.output_off(self.pid_2_output_lower_id)
        else:
            # Only one PID received a measurement
            # Note: PID 1 Raise is the same output as PID 2 Lower

            if self.last_measurement_1 is None:  # No measurement for PID 1
                if self.pid_2_control_variable < 0:  # PID 2 will lower, so only turn off PID 1 lower
                    if self.pid_1_direction in ['lower', 'both'] and self.pid_1_output_lower_id:
                        self.logger.debug("PID 1 Last measurement unsuccessful, and PID 2 will raise. "
                                          "Turning only PID 1 Lower off.")
                        self.control.output_off(self.pid_1_output_lower_id)
                else:
                    # PID 2 will raise, so turning both PID 1 outputs off
                    if self.pid_1_direction in ['lower', 'both'] and self.pid_1_output_lower_id:
                        self.logger.debug("PID 1 Last measurement unsuccessful, and PID 2 will raise. "
                                          "Turning PID 1 lower off.")
                        self.control.output_off(self.pid_1_output_lower_id)
                    if self.pid_1_direction in ['raise', 'both'] and self.pid_1_output_raise_id:
                        self.logger.debug("PID 1 Last measurement unsuccessful, and PID 2 will raise. "
                                          "Turning PID 1 raise off.")
                        self.control.output_off(self.pid_1_output_raise_id)
            
            if self.last_measurement_2 is None:  # No measurement for PID 2
                if self.pid_1_control_variable > 0:  # PID 1 will raise, so only turn off PID 2 raise
                    if self.pid_2_direction in ['raise', 'both'] and self.pid_2_output_raise_id:
                        self.logger.debug("PID 2 Last measurement unsuccessful, and PID 1 will raise. "
                                          "Turning only PID 2 Raise off.")
                        self.control.output_off(self.pid_2_output_raise_id)
                else:
                    # PID 1 will lower, so turning both PID 2 outputs off
                    if self.pid_2_direction in ['lower', 'both'] and self.pid_2_output_lower_id:
                        self.logger.debug("PID 2 Last measurement unsuccessful, and PID 1 will lower. "
                                          "Turning PID 2 lower off.")
                        self.control.output_off(self.pid_2_output_lower_id)
                    if self.pid_2_direction in ['raise', 'both'] and self.pid_2_output_raise_id:
                        self.logger.debug("PID 2 Last measurement unsuccessful, and PID 1 will lower. "
                                          "Turning PID 2 raise off.")
                        self.control.output_off(self.pid_2_output_raise_id)

        # Now determine which PID output(s) should be turned on
        # Note: PID 1 Raise is the same output as PID 2 Lower
        if (
                (self.pid_1_direction in ['raise', 'both'] and self.pid_1_output_raise_id)
                and
                (self.pid_2_direction in ['lower', 'both'] and self.pid_2_output_lower_id)
                and
                (self.pid_1_control_variable > 0 and self.pid_2_control_variable < 0)
                ):
            # PID conflict detected! PID 1 wants to raise and PID 2 wants to lower.
            # This is where the code will go to handle what happens when both PIDs want to turn the same
            # output on. Currently, the output will not be turned on when this happens, and the follwing
            # debug message will be logged.
            self.logger.debug("PID 1 wants to raise and PID 2 wants to lower. "
                              "Don't turn PID 1 Raise or PID 2 Lower output on.")
        else:
            # No PID conflicts, both PIDs can operate normally

            # Turn PID 1 output on for a duration
            if self.pid_1_direction in ['lower', 'both'] and self.pid_1_output_lower_id:
                if self.pid_1_control_variable < 0:
                    self.logger.debug("PID 1 Lower output on for {} seconds".format(abs(self.pid_1_control_variable)))
                    self.control.output_on(self.pid_1_output_raise_id, amount=abs(self.pid_1_control_variable))
            elif self.pid_1_direction in ['raise', 'both'] and self.pid_1_output_lower_id:
                if self.pid_1_control_variable > 0:
                    self.logger.debug("PID 1 Raise output on for {} seconds".format(self.pid_1_control_variable))
                    self.control.output_on(self.pid_1_output_lower_id, amount=self.pid_1_control_variable)

            # Turn PID 2 output on for a duration
            if self.pid_2_direction in ['lower', 'both'] and self.pid_2_output_lower_id:
                if self.pid_2_control_variable < 0:
                    self.logger.debug("PID 2 Lower output on for {} seconds".format(abs(self.pid_2_control_variable)))
                    self.control.output_on(self.pid_2_output_raise_id, amount=abs(self.pid_2_control_variable))
            elif self.pid_2_direction in ['raise', 'both'] and self.pid_2_output_lower_id:
                if self.pid_2_control_variable > 0:
                    self.logger.debug("PID 2 Raise output on for {} seconds".format(self.pid_2_control_variable))
                    self.control.output_on(self.pid_2_output_lower_id, amount=self.pid_2_control_variable)


class PIDController:
    def __init__(self, logger, p, i , d, integrator_min, integrator_max, direction, band, setpoint):
        self.logger = logger
        self.Kp = p
        self.Ki = i
        self.Kd = d
        self.integrator_min = integrator_min
        self.integrator_max = integrator_max
        self.direction = direction
        self.band = band
        self.setpoint = setpoint

    def update_pid_output(self, current_value):
        """
        Calculate PID output value from reference input and feedback

        :return: Manipulated, or control, variable. This is the PID output.
        :rtype: float

        :param current_value: The input, or process, variable (the actual
            measured condition by the input)
        :type current_value: float
        """
        # Determine if hysteresis is enabled and if the PID should be applied
        setpoint = self.check_hysteresis(current_value)

        if setpoint != self.setpoint:
            self.setpoint_band = setpoint
        else:
            self.setpoint_band = None

        if setpoint is None:
            # Prevent PID variables form being manipulated and
            # restrict PID from operating.
            return 0

        self.error = setpoint - current_value

        # Calculate P-value
        self.P_value = self.Kp * self.error

        # Calculate I-value
        self.integrator += self.error

        # First method for managing integrator
        if self.integrator > self.integrator_max:
            self.integrator = self.integrator_max
        elif self.integrator < self.integrator_min:
            self.integrator = self.integrator_min

        # Second method for regulating integrator
        # if self.period is not None:
        #     if self.integrator * self.Ki > self.period:
        #         self.integrator = self.period / self.Ki
        #     elif self.integrator * self.Ki < -self.period:
        #         self.integrator = -self.period / self.Ki

        self.I_value = self.integrator * self.Ki

        # Prevent large initial D-value
        if self.first_start:
            self.derivator = self.error
            self.first_start = False

        # Calculate D-value
        self.D_value = self.Kd * (self.error - self.derivator)
        self.derivator = self.error

        # Produce output form P, I, and D values
        pid_value = self.P_value + self.I_value + self.D_value

        self.logger.debug(
            "PID: Input: {inp}, "
            "Output: P: {p}, I: {i}, D: {d}, Out: {o}".format(
            inp=current_value, p=self.P_value, i=self.I_value, d=self.D_value, o=pid_value))

        return pid_value

    def check_hysteresis(self, measure):
        """
        Determine if hysteresis is enabled and if the PID should be applied

        :return: float if the setpoint if the PID should be applied, None to
            restrict the PID
        :rtype: float or None

        :param measure: The PID input (or process) variable
        :type measure: float
        """
        if self.band == 0:
            # If band is disabled, return setpoint
            self.setpoint_band = None
            return self.setpoint

        band_min = self.setpoint - self.band
        band_max = self.setpoint + self.band

        if self.direction == 'raise':
            if (measure < band_min or
                    (band_min < measure < band_max and self.allow_raising)):
                self.allow_raising = True
                setpoint = band_max  # New setpoint
                return setpoint  # Apply the PID
            elif measure > band_max:
                self.allow_raising = False
            return None  # Restrict the PID

        elif self.direction == 'lower':
            if (measure > band_max or
                    (band_min < measure < band_max and self.allow_lowering)):
                self.allow_lowering = True
                setpoint = band_min  # New setpoint
                return setpoint  # Apply the PID
            elif measure < band_min:
                self.allow_lowering = False
            return None  # Restrict the PID

        elif self.direction == 'both':
            if measure < band_min:
                setpoint = band_min  # New setpoint
                if not self.allow_raising:
                    # Reset integrator and derivator upon direction switch
                    self.integrator = 0.0
                    self.derivator = 0.0
                    self.allow_raising = True
                    self.allow_lowering = False
            elif measure > band_max:
                setpoint = band_max  # New setpoint
                if not self.allow_lowering:
                    # Reset integrator and derivator upon direction switch
                    self.integrator = 0.0
                    self.derivator = 0.0
                    self.allow_raising = False
                    self.allow_lowering = True
            else:
                return None  # Restrict the PID
            return setpoint  # Apply the PID
