#### Custom Input: BME280 Serial to The Things Network

[Version 1.1](https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/bme280%20serial%20to%20ttn/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

This Input was designed for use with a microcontroller with LoRaWAN support, which receives measurements via 
USB/serial and sends those measurements to The Things Network with the MCU/LoRaWAN device. The string written to the 
serial device is in the format "B,VAL1,VAL2,VAL3", where VAL1 is the humidity measurement, VAL2 pressure, and VAL3 
temperature. "B" is used to denote the measurement is from the BME280 sensor, as I send multiple different 
measurements to the MCU, hence the need to differentiate the string being received by the MCU. 

#### Requirements

* Your own LoRaWAN Gateway or use a public gateway
* A microcontroller with a LoRaWAN device
* An account with [The Things Network](https://www.thethingsnetwork.org/)

#### Setup

* Use your MCU/LoRaWAN device of choice and develop code to parse the "K,VAL" string received by serial and send the value to TTN.
* Connect the USB interface of the MCU to the Raspberry Pi running Mycodo.
* On TTN, create a new application and add a device.
* On TTN, enable the Data Storage Integration in the application and copy the [Payload Decoder code](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_inputs/bme280%20serial%20to%20ttn/payload_decoder_the_things_network_app.java).
* In Mycodo, upload the [Custom Input](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_inputs/bme280%20serial%20to%20ttn/mycodo_custom_input_bme280_ttn.py) file under Config -> Inputs.
* In Mycodo, on the Data page, use the dropdown to select and add the new Input.
* Configure the USB device and activate the Input.
