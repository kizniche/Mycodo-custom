#### LoRaWAN-enabled Geiger Counter

By [Kyle Gabriel](https://kylegabriel.com/)

#### About

This Input was designed for use with the Moteino Mega with a LoRaWAN transceiver, connected to a MightyOhm Geiger Counter (v1.0), powered by three AAA batteries, for long-term remote radiation monitoring.

Every hour, the Moteino Mega powers the Geiger counter for 1 minute to acquire radiation measurements. The Moteino Mega then records the counts per minute (CPM) and μSv/hr measurement data over the Geiger Counter's serial connection. The Geiger counter power is turned off and the data is transmitted via LoRaWAN to The Things Network (TTN). Mycodo uses this custom Input to download the measurements from TTN and transmit them to Safecast and GMC Map.

#### Requirements

* [Moteino Mega](https://lowpowerlab.com/shop/product/119) with a LoRaWAN Transceiver (choose the proper frequency for your region)
* [MightyOhm Geiger Counter 1.0](https://mightyohm.com/blog/products/geiger-counter/)
* Your own LoRaWAN Gateway or use a public gateway
* An account with [The Things Network](https://www.thethingsnetwork.org/)
* An account with [Safecast](https://api.safecast.org)
* An account with [GMC Map](https://www.gmcmap.com/)

 #### Setup

1. Add the required libraries listed at the top of the arduino sketch to the Arduino IDE, fill in the credentials (at the top of the ino file) created on TTN (below), then upload the sketch to the Moteino Mega.
2. Connect the TX pin of the Geiger counter to the RX pin of the Moteino Mega.
3. Connect pin 0 of the Moteino Mega to the positive terminal of the Geiger counter battery case (do not put batteries in the Geiger counter's battery case).
4. Connect the ground pin of the Moteino Mega to the ground pin of the Geiger counter.
5. Put the Geiger counter power switch into the ON position.
6. On TTN, create a new application and add a device.
7. On TTN, enable the Data Storage Integration in the application and copy the Payload Decoder code.
8. Power the Moteino Mega and verify data is being transmitted to TTN.
9. In Mycodo, upload the custom Input file under Config -> Inputs.
10. In Mycodo, on the Data page, use the dropdown to select and add the new Input "Geiger Counter (TTN/Safecast/GMCMap)".
11. Configure and activate the new Input. Data can be sent to Safecast (api.safecast.org) and GMC Map (gmcmap.com). For each service, set up an account, add a device, enter credentials, and check the checkbox to enable each.

#### Notes

I use 3x AAA batteries to power the Moteino Mega via VIN (which has its own voltage regulator). The battery pack is housed underneath the Geiger counter.

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
