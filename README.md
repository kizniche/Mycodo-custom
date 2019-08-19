# Mycodo Custom Inputs

These are custom Inputs I created for [Mycodo](https://github.com/kizniche/Mycodo) that don't quite fit with the built-in set. This could be for a number of reasons: they're experimental/unreliable, they wil lbe rarely used, they're too complex for the average user, etc. As such, I've created this repository to share them publicly in case anyone wants to build the devices and use them.

* [LoRaWAN-enabled Geiger Counter](#lorawan-enabled-geiger-counter) - Long-term remote radiation monitoring

---

#### LoRaWAN-enabled Geiger Counter

By [Kyle Gabriel](https://kylegabriel.com/)

Code: [kizniche/Mycodo-custom-inputs/geiger_counter](https://github.com/kizniche/Mycodo-custom-Inputs/tree/master/databases)

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

1. Add the required libraries listed at the top of the arduino sketch to the Arduino IDE, then upload the sketch to the Moteino Mega and set up the credentials based on the applications and device created on TTN, below.
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

I use 3x AAA batteries to power the Moteino Mega via VIN (which has its own voltage regulator).
