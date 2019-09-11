#### LoRaWAN-enabled Geiger Counter

[Version 1.1](https://github.com/kizniche/Mycodo-custom-inputs/blob/master/geiger%20counter/CHANGELOG.md)

By [Kyle Gabriel](https://kylegabriel.com/)

Blog Post: [Remote Radiation Monitoring](https://kylegabriel.com/projects/2019/08/remote-radiation-monitoring.html)

#### About

This Input was designed for use with the Moteino Mega with a LoRaWAN transceiver, connected to a MightyOhm Geiger Counter (v1.0), powered by three AA batteries, for long-term remote radiation monitoring.

Every hour, the Moteino Mega powers the Geiger counter for 1 minute to acquire radiation measurements. The Moteino Mega then records the counts per minute (CPM) and μSv/hr measurement data over the Geiger Counter's serial connection. The Geiger counter power is turned off and the data is transmitted via LoRaWAN to The Things Network (TTN). Mycodo uses this custom Input to download the measurements from TTN and transmit them to Safecast and GMC Map.

#### Requirements

* Mycodo >= 7.7.0
* [Moteino Mega](https://lowpowerlab.com/shop/product/119) with a LoRaWAN Transceiver (choose the proper frequency for your region)
* [MightyOhm Geiger Counter 1.0](https://mightyohm.com/blog/products/geiger-counter/)
* Your own LoRaWAN Gateway or use a public gateway
* An account with [The Things Network](https://www.thethingsnetwork.org/)
* An account with [Safecast](https://api.safecast.org)
* An account with [GMC Map](https://www.gmcmap.com/)

### Required Arduino Libraries

* [mcci-catena/arduino-lmic](https://github.com/mcci-catena/arduino-lmic)
* [rocketscream/Low-Power](https://github.com/rocketscream/Low-Power)

### Optional libraries (for OLED display)

* [adafruit/Adafruit_SSD1306](https://github.com/adafruit/Adafruit_SSD1306)
* [adafruit/Adafruit-GFX-Library](https://github.com/adafruit/Adafruit-GFX-Library)

#### Setup

* Add the required libraries listed at the top of the [arduino sketch](https://github.com/kizniche/Mycodo-custom-inputs/blob/master/geiger%20counter/arduino_sketch_geiger_counter_moteino_mega_lora/arduino_sketch_geiger_counter_moteino_mega_lora.ino) to the Arduino IDE.
* Fill in the credentials created on TTN (below) at the top of the Arduino code at the heading "TTN Credentials".
* If using a 128x64 I2C SD1306 OLED display, connect the display SDA and SCL pins to the SDA/SCL pins of the Moteino Mega and uncomment "#define USE_SSD1306_OLED 1" at the top of the Arduino code.
* Using the Arduino IDE, upload the code to the Moteino Mega.
* Connect the TX pin of the Geiger counter to the RX pin of the Moteino Mega.
* Connect pin 0 of the Moteino Mega to the positive terminal of the Geiger counter battery case (do not put batteries in the Geiger counter's battery case).
* Connect the ground pin of the Moteino Mega to the ground pin of the Geiger counter. 
* Put the Geiger counter power switch into the ON position.
* On TTN, create a new application and add a device.
* On TTN, enable the Data Storage Integration in the application and copy the [Payload Decoder code](https://github.com/kizniche/Mycodo-custom-inputs/blob/master/geiger%20counter/payload_decoder_the_things_network_app.java).
* Power the Moteino Mega and verify data is being transmitted to TTN.
* In Mycodo, upload the [custom Input](https://github.com/kizniche/Mycodo-custom-inputs/blob/master/geiger%20counter/mycodo_custom_input_ttn_data_storage_geiger_counter.py) file under Config -> Inputs.
* In Mycodo, on the Data page, use the dropdown to select and add the new Input "Geiger Counter (TTN/Safecast/GMCMap)".
* Configure and activate the new Input. Data can be sent to Safecast (api.safecast.org) and GMC Map (gmcmap.com). For each service, set up an account, add a device, enter credentials, and check the checkbox to enable each.

#### Notes

I use 3x AAA batteries to power the Moteino Mega via the VIN pin (which has its own voltage regulator). In the images, below, the battery pack is housed underneath the Geiger counter.

#### Images

![GC System 01](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/GC_System_01.jpg)

![GC System 02](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/GC_System_02.jpg)

![GC System 03](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/GC_System_03.jpg)

---

![Screenshot_Safecast_map](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/Screenshot_Safecast_map.png)

![Screenshot_Safecast_data](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/Screenshot_Safecast_data.png)

---

![Screenshot_GMC_Map](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/Screenshot_GMC_Map.png)

![Screenshot_GMC_Map_data](https://raw.githubusercontent.com/kizniche/Mycodo-custom-inputs/master/geiger%20counter/images/Screenshot_GMC_Map_data.png)
