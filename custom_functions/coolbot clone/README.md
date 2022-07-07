#### Custom Function: CoolBot Clone

[Version 1.1](https://github.com/kizniche/Mycodo-custom/blob/master/custom_functions/coolbot%20clone/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

This Function mimics the [CoolBot](https://storeitcold.com), allowing a walk-in cool room or freezer to be created using an inexpensive window air conditioner unit.

Briefly, using an air conditioner (AC), remove the temperature sensor (that monitors the condenser for freezing) from the condenser and attach a small heater to it (Output: Heater). A separate temperature sensor is attached to the condenser to monitor it for freezing (Input: Condenser Temperature). A temperature sensor is hung in the room, away from the AC airflow, to monitor the room temperature (Input: Room Temperature). The AC is turned to as low as it can go, typically around 60 F. The heater attached to the AC's temperature sensor is used to "trick" the AC into thinking it's warmer than it actually is, causing the AC to run below the temperature set on the AC. While the room temperature is greater than the set temperature (e.g. 40 F), and the condenser temperature is greater than freezing, the small heater is turned on and the AC runs. If the room temperature is equal or less than the set temperature or the condenser is below freezing, the small heater is turned off and the AC is permitted to stop cooling and defrost its condenser.

#### Requirements

* Mycodo >= 8.13.10
* Air conditioner
* 2 temperature sensors
* Small heater

#### Setup

* Disconnect the temperature sensor of the air conditioner and afix it to the small heater using aluminum foil or heat-shrink tubing.
* Connect one temperature sensor to the fins of the AC where the AC temperature sensor was removed.
* Let the other temperature sensor hang freely in the room to measure the air temperature (prevent the AC blowing directly on it).
* In Mycodo, on the Data page, add and activate the temperature sensors.
* In Mycodo, on the Setup -> Output page, add and configure the relay that controls the heater.
* In Mycodo, upload the [Custom Controller](https://raw.githubusercontent.com/kizniche/Mycodo-custom/master/custom_functions/coolbot%20clone/mycodo_custom_function_coolbot_clone.py) file under Config -> Custom Functions.
* In Mycodo, on the Function page, use the dropdown to select and add the new Function "CoolBot Clone".
* Configure the temperature sensors, heater output, and other options, then activate the Function.
