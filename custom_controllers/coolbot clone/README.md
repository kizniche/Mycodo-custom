#### Custom Controller: CoolBot Clone

[Version 1.0](https://github.com/kizniche/Mycodo-custom/blob/master/custom_controllers/coolbot%20clone/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

This Controller mimics the functionality of a [CoolBot](https://storeitcold.com), allowing a walking cool room or freezer to be created using an inexpensive air conditioner unit.

Briefly, there is an air conditioner (AC), typically a window unit, that has the temperature sensor that monitors the condenser for freezing removed from the condenser and has a small heater attached to it (Output: Heater). A temperature sensor is attached to the condenser to monitor condenser freezing (Input: Condenser Temperature). An output controls power to the AC (Output: AC). A temperature sensor is hung in the room, away from the AC airflow, to monitor the room temperature (Input: Room Temperature). The AC is turned to as low as it can go, typically around 60 F. The heater attached to the AC's temperature sensor is used to "trick" the AC into thinking it's warmer than it actually is, and run the AC as the room temperature drops below the temperature set on the AC. While the room temperature is greater than the set temperature (e.g. 40 F), and the condenser temperature is greater than freezing, the small heater is turned on and the AC runs. If the room temperature is equal or less than the set temperature or the condenser is below freezing, the small heater is turned off and the AC is permitted to stop cooling and defrost its condenser.

#### Requirements

* Mycodo >= 8.4.0
* Air conditioner
* Temperature sensor
* Small heater

#### Setup

* Disconnect the temperature sensor of the air conditioner and afix it to the small heater using heat-shrink tubing.
* Connect the temperature sensor measured by Mycodo to the fins of the AC where the AC temperature sensor was removed.
* In Mycodo, on the Data page, add and activate the temperature sensor.
* In Mycodo, on the Setup -> Output page, add and configure the relay that controls the heater.
* In Mycodo, upload the [Custom Controller](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_controllers/coolbot%20clone/mycodo_custom_controller_coolbot_clone.py) file under Config -> Controllers.
* In Mycodo, on the Function page, use the dropdown to select and add the new Controller "CoolBot Clone".
* Configure the temperature sensor, heater output, and other options, then activate the Controller.
