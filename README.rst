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

Custom Outputs
==============

On/Off Remote GPIO (gpiozero)
-----------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_inputs/geiger counter/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_outputs/remote%20GPIO%20on-off>`__

Remotely control GPIO pin states over a network with the use of [gpiozero](https://github.com/gpiozero/gpiozero).

--------------

PWM Remote GPIO (gpiozero)
--------------------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_inputs/geiger counter/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_outputs/remote%20GPIO%20PWM>`__

Remotely control GPIO pin duty cycles over a network with the use of [gpiozero](https://github.com/gpiozero/gpiozero).

--------------

Custom Controllers
==================

CoolBot Clone
-------------

By `Kyle Gabriel <https://kylegabriel.com/>`__

Details and code: `Mycodo-custom/custom_controllers/coolbot clone/ <https://github.com/kizniche/Mycodo-custom/blob/master/custom_controllers/coolbot%20clone>`__

This Controller mimics the functionality of a `CoolBot <https://storeitcold.com>`__, allowing a walking cool room or freezer to be created using an inexpensive air conditioner unit.
