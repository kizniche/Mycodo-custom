# coding=utf-8
import copy

from mycodo.inputs.base_input import AbstractInput
from mycodo.inputs.sensorutils import calculate_dewpoint
from mycodo.inputs.sensorutils import calculate_vapor_pressure_deficit

# Measurements
measurements_dict = {
    0: {
        'measurement': 'visible_light',
        'unit': 'unitless'
    },
    1: {
        'measurement': 'uv_index',
        'unit': 'unitless'
    },
    2: {
        'measurement': 'infrared',
        'unit': 'unitless'
    }
}

# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'SI114x',
    'input_manufacturer': 'Seeedstudio',
    'input_name': 'Sunlight Sensor',
    'input_library': 'seeed_si114x',
    'measurements_name': 'Visible/UV/IR Light',
    'measurements_dict': measurements_dict,
    'url_manufacturer': 'https://wiki.seeedstudio.com/Grove-Sunlight_Sensor/',
    'url_product_purchase': 'https://www.seeedstudio.com/Grove-Sunlight-Sensor.html',

    'options_enabled': [
        'i2c_location',
        'measurements_select',
        'period',
        'pre_output'
    ],
    'options_disabled': ['interface'],

    'dependencies_module': [
        ('pip-pypi', 'seeed_si114x', 'seeed-python-si114x==1.0.1'),
    ],

    'interfaces': ['I2C'],
    'i2c_location': ['0x60'],
    'i2c_address_editable': True
}


class InputModule(AbstractInput):
    """ A sensor support class that measures soil moisture using adafruit's i2c soil sensor """
    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        self.sensor = None

        if not testing:
            self.initialize_input()

    def initialize_input(self):
        import seeed_si114x

        try:
            self.sensor = seeed_si114x.grove_si114x(address=int(str(self.input_dev.i2c_location), 16))
        except:
            self.logger.exception("Setting up sensor")

    def get_measurement(self):
        if not self.sensor:
            self.logger.error("Input not set up")
            return

        self.return_dict = copy.deepcopy(measurements_dict)

        if self.is_enabled(0):
            self.value_set(0, self.sensor.ReadVisible)

        if self.is_enabled(1):
            self.value_set(1, self.sensor.ReadUV / 100)

        if self.is_enabled(2):
            self.value_set(2, self.sensor.ReadIR)

        return self.return_dict
