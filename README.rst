----------------------------------------------
Mycodo Custom Inputs, Outputs, and Controllers
----------------------------------------------

.. contents::
    :depth: 3

About
=====

These are custom Inputs, Outputs, and Controllers created for `Mycodo <https://github.com/kizniche/Mycodo>`__ that don't quite fit with the built-in set. This could be for a number of reasons: they're experimental/unreliable/untested, they will be rarely used, they're too complex for the average user, etc. If any of these custom modules become included in Mycodo's built-in set, they will be removed from this repository.

These modules can be imported from the Configuration submenus titled Inputs, Outputs, and Controllers.

--------------

Custom Inputs
=============

LoRaWAN-enabled Geiger Counter
------------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Blog Post: `Remote Radiation Monitoring <https://kylegabriel.com/projects/2019/08/remote-radiation-monitoring.html>`__

Details and code: `Mycodo-custom/custom_inputs/geiger counter/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/geiger%20counter>`__

This Input was designed for use with the Moteino Mega with a LoRaWAN transceiver, connected to a MightyOhm Geiger Counter (v1.0), powered by three AA batteries, for long-term remote radiation monitoring.

--------------

BME680 (Temperature Error Fix)
------------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Forum Post: `BME680 shows wrong temperature <https://kylegabriel.com/forum/general-discussion/sensor-bme680-occasionally-locks-up-and-shows-wrong-temperature-but-correct-humidity-until-deactivated-and-reactivated/>`__

Details and code: `Mycodo-custom/custom_inputs/bme680 temperature error fix/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/bme680%20temperature%20error%20fix>`__

A user with the BME680 sensor experienced an issue where the temperature would erroneously and continuously measure 34.54 C until the Input was deactivated and activated again. Since We don't know if this is an isolated incident because we only have one sensor to test, this module was created to fix the issue. If there are more reports of this occurring with other BME680 sensors, this module may move into the built-in set for Mycodo.

--------------

BME280 Serial to TTN
--------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_inputs/bme280 serial to ttn/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/bme280%20serial%20to%20ttn>`__

This Input will write the measured values from the BME280 sensor to a serial device. For my application, I have a MCU with a
LoRaWAN transceiver that then receives those measurements and transmits them to The Things Network.

--------------

K30 Serial to TTN
-----------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_inputs/k30 serial to ttn/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/k30%20serial%20to%20ttn>`__

This Input will write the measured values from the K30 sensor to a serial device. For my application, I have a MCU with a
LoRaWAN transceiver that then receives those measurements and transmits them to The Things Network.

--------------

SI114x I2C Sunlight Sensor
--------------------------

By `Pascal Krahmer <https://github.com/pkrahmer>`__

Details and code: `Mycodo-custom/custom_inputs/si114x/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_inputs/si114x>`__

This input supports the SI114X light sensor. It provides information about Visible Light, Infrared Light and an UV Index based on the former readings.

--------------


Custom Outputs
==============

On/Off Remote GPIO (gpiozero)
-----------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_outputs/remote GPIO on-off/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_outputs/remote%20GPIO%20on-off>`__

Remotely control GPIO pin states over a network with the use of [gpiozero](https://github.com/gpiozero/gpiozero).

--------------

PWM Remote GPIO (gpiozero)
--------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_outputs/remote GPIO PWM/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_outputs/remote%20GPIO%20PWM>`__

Remotely control GPIO pin duty cycles over a network with the use of [gpiozero](https://github.com/gpiozero/gpiozero).

--------------

Custom Controllers
==================

CoolBot Clone
-------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_controllers/coolbot clone/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_controllers/coolbot%20clone>`__

This Controller mimics the functionality of a `CoolBot <https://storeitcold.com>`__, allowing a walking cool room or freezer to be created using an inexpensive air conditioner unit.
