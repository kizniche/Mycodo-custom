#### Custom Output: PWM Remote GPIO (gpiozero)

[Version 0.1](https://github.com/kizniche/Mycodo-custom/blob/master/custom_outputs/remote%20GPIO%20PWM/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

Remotely control GPIO pin duty cycles over a network with the use of [gpiozero](https://github.com/gpiozero/gpiozero).

#### Requirements

* Mycodo >= 8.5.0

#### Setup

Read [this](https://gpiozero.readthedocs.io/en/stable/installing.html) and [this](https://gpiozero.readthedocs.io/en/stable/pi_zero_otg.html) for information about setting up your systems to use this Output.

* In Mycodo, upload the [Custom Output](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_outputs/remote%20GPIO%20PWM/mycodo_custom_output_remote_gpio_pwm.py) file under Configure -> Outputs.
* In Mycodo, on the Output page, use the dropdown to select and add the new Output "PWM Remote GPIO (gpiozero) (GPIO)".
* Read the notes above the Output settings to configure your systems to use the Output.
