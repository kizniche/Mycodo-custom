# coding=utf-8
#
# mycodo_custom_output_remote_gpio_pwm.py - PWM Remote GPIO Output
#
from flask_babel import lazy_gettext
from mycodo.outputs.base_output import AbstractOutput

# Measurements
measurements_dict = {
    0: {
        'measurement': 'duty_cycle',
        'unit': 'percent'
    }
}

# Output information
OUTPUT_INFORMATION = {
    'output_name_unique': 'remote_gpio_pwm',
    'output_name': lazy_gettext('PWM Remote GPIO (gpiozero)'),
    'measurements_dict': measurements_dict,
    'version': '0.1',

    'on_state_internally_handled': False,

    'output_types': ['pwm'],

    'message':
        'NOTE: This is a work in progress.'
        '<br>This output was developed to be able to operate from Mycodo installed on a Raspberry Pi '
        'or from Mycodo running within a docker container on a PC and control GPIO pins of a remote host, '
        'be it an IP address or a Pi Zero connected via USB '
        '(<a href="https://github.com/gpiozero/gpiozero" target="_blank">more info</a>). Set up '
        'dependencies manually, then restart the Mycodo daemon, before using the output. '
        'The method of installing dependencies may differ depending on the host device and operating '
        'system and the client device (see '
        '<a href="https://gpiozero.readthedocs.io/en/stable/installing.html" target="_blank">this</a> and '
        '<a href="https://gpiozero.readthedocs.io/en/stable/pi_zero_otg.html" target="_blank">this</a>).',

    'options_enabled': [
        'gpio_pin',
        'pwm_frequency',
        'pwm_invert_signal',
        'pwm_state_startup',
        'pwm_state_shutdown',
        'trigger_functions_startup',
        'button_send_duty_cycle'
    ],
    'options_disabled': [
        'interface'
    ],

    'dependencies_module': [
        ('pip-pypi', 'gpiozero', 'gpiozero'),
    ],

    'interfaces': ['GPIO'],

    # 'custom_options_message': 'This is a message displayed for custom options.',
    'custom_options': [
        {
            'id': 'host',
            'type': 'text',
            'default_value': '192.168.0.10',
            'name': lazy_gettext('Host'),
            'phrase': lazy_gettext('The host to connect and control a remote GPIO pin')
        }
    ],
}


class OutputModule(AbstractOutput):
    """
    An output support class that operates an output
    """
    def __init__(self, output, testing=False):
        super(OutputModule, self).__init__(output, testing=testing, name=__name__)

        self.output_setup = None
        self.output_device = None

        self.host = None
        self.setup_custom_options(
            OUTPUT_INFORMATION['custom_options'], output)

        if not testing:
            self.output_setup = None
            self.gpio_pin = output.pin
            self.pwm_hertz = output.pwm_hertz

    def output_switch(self, state, amount=None, duty_cycle=None):
        """Switch the output on or off"""
        if state == 'on' and duty_cycle != 0:
            self.output_device.value = duty_cycle / 100.0
            self.logger.debug("Output turned on")
        elif state == 'off' or duty_cycle == 0:
            self.output_device.value = 0
            self.logger.debug("Output turned off")

    def is_on(self):
        """Return the state of the output"""
        if self.is_setup():
            try:
                return self.output_device.value * 100.0
            except Exception as e:
                self.logger.error(
                    "Status check error: {}".format(e))

    def is_setup(self):
        """Return whether the output has successfully been set up"""
        return self.output_setup

    def setup_output(self):
        """Code executed when Mycodo starts up to initialize the output"""
        if not self.gpio_pin or not self.host:
            self.logger.error("Need GPIO pin and host to set up remote GPIO")
            return

        try:
            from gpiozero.pins.pigpio import PiGPIOFactory
            from gpiozero import PWMOutputDevice
            factory = PiGPIOFactory(host=self.host)
            self.logger.debug("Setting up remote GPIO pin {pin} on host {host}".format(
                pin=self.gpio_pin, host=self.host))
            self.output_device = PWMOutputDevice(
                pin=self.gpio_pin,
                frequency=self.pwm_hertz,
                pin_factory=factory)
            self.logger.debug("Output set up")
            self.output_setup = True
        except Exception:
            self.logger.exception("Output Setup")
            self.output_setup = False
