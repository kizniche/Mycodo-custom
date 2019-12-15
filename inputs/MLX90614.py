# coding=utf-8
from flask_babel import lazy_gettext

from mycodo.inputs.base_input import AbstractInput

# Measurements
measurements_dict = {
    0: {
        'measurement': 'temperature',
        'unit': 'C'
    },
    1: {
        'measurement': 'temperature',
        'unit': 'C'
    }
}

# Input information
INPUT_INFORMATION = {
    #
    # Required options
    #

    # Unique name (must be unique from all other inputs)
    'input_name_unique': 'MLX90614',

    # Descriptive information
    'input_manufacturer': 'MELEXIS',
    'input_name': 'MLX90614',

    # Measurement information
    'measurements_name': 'Temperature (Ambient/Object)',
    'measurements_dict': measurements_dict,

    # Add a message that the user can see when they view the options of the Input.
    # This will be displayed at the top of the options when the user expands the input with the "+" icon.
    'message': "Note: Don't forget to enable I2C before activating this Input",

    # Web User Interface display options
    # Options that are enabled will be editable from the input options page.
    # Options that are disabled will appear on the input options page but not be editable.
    # There are several location options available for use:
    # 'location', 'gpio_location', 'i2c_location', 'bt_location', 'ftdi_location', and 'uart_location'
    'options_enabled': [
        'i2c_location',
        'measurements_select',
        'period',
        'pre_output',
        'log_level_debug'
    ],
    'options_disabled': ['interface'],


    #
    # Non-required options
    #

    # Python module dependencies
    # This must be a module that is able to be installed with pip or apt (pypi, git, and apt examples below)
    # Leave the list empty if there are no dependencies
    'dependencies_module': [  # List of tuples
        ('pip-pypi', 'smbus2', 'smbus2')
    ],

    'interfaces': ['I2C'],
    'i2c_location': ['0x5a'],
    'i2c_address_editable': False,

    # Miscellaneous options
    'period': 15,  # Float

}


class InputModule(AbstractInput):
    """ 
    A sensor support class that measure the MLX90614's ambient and object temperature.
    """

    def __init__(self, input_dev, testing=False):
        super(InputModule, self).__init__(input_dev, testing=testing, name=__name__)

        #
        # Set variables to custom options
        #

        self.MLX90614_RAWIR1=0x04
        self.MLX90614_RAWIR2=0x05
        self.MLX90614_TA=0x06
        self.MLX90614_TOBJ1=0x07
        self.MLX90614_TOBJ2=0x08
        
        self.MLX90614_TOMAX=0x20
        self.MLX90614_TOMIN=0x21
        self.MLX90614_PWMCTRL=0x22
        self.MLX90614_TARANGE=0x23
        self.MLX90614_EMISS=0x24
        self.MLX90614_CONFIG=0x25
        self.MLX90614_ADDR=0x0E
        self.MLX90614_ID1=0x3C
        self.MLX90614_ID2=0x3D
        self.MLX90614_ID3=0x3E
        self.MLX90614_ID4=0x3F

        if not testing:
            from smbus2 import SMBus

            self.i2c_address = int(str(input_dev.i2c_location), 16)
            self.i2c_bus = input_dev.i2c_bus

            self.bus = SMBus(self.i2c_bus)

    def read_reg(self, reg_addr):
        return self.bus.read_word_data(self.i2c_address, reg_addr)
 
    def data_to_temp(self, data):
        temp = (data*0.02) - 273.15
        return temp
 
    def get_amb_temp(self):
        data = self.read_reg(self.MLX90614_TA)
        return self.data_to_temp(data)
 
    def get_obj_temp(self):
        data = self.read_reg(self.MLX90614_TOBJ1)
        return self.data_to_temp(data)

    def get_measurement(self):
        """ Gets the ambient (ch0) and object (ch1) temperature"""
        #
        # Copy measurements dictionary
        #

        self.return_dict = measurements_dict.copy()

        #
        # Begin sensor measurement code
        #

        if self.is_enabled(0):
            self.value_set(0, self.get_amb_temp())

        if self.is_enabled(1):
            self.value_set(1, self.get_obj_temp())

        #
        # End sensor measurement code
        #

        self.logger.info("MLX90614 measurement taken.")

        return self.return_dict
