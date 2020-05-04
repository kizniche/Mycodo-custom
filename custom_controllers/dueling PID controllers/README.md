#### Dueling PIDs

[Version 1.0](https://github.com/kizniche/Mycodo-custom/blob/master/custom_controllers/dueling%20PID%20controllers/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

This Controller is an example of how to logically handle a scenario where two PIDs utilize the same output so there are no conflicts with how the output is modulated.

This custom Controller will logically handle two dueling PID controllers that utilize the same output, allowing rules to define how the shared output is handled when both controllers desire to modulate it at the same time. Specifically, PID 1 raise output is the same as PID 2 lower output. Example: The Output is to raise humidity, and PID 1 raises humidity while PID 2 lowers temperature. Notes: Not designed for PWM outputs, only duration outputs.

#### Requirements

* Mycodo >= 8.4.0

#### Setup

* In Mycodo, upload the [Custom Controller](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_controllers/dueling%20PID%20controllers/mycodo_custom_controller_dueling_pids.py) file under Config -> Controllers.
* In Mycodo, on the Function page, use the dropdown to select and add the new Controller "Dueling PIDs".
* Configure the options, then activate the Controller.
