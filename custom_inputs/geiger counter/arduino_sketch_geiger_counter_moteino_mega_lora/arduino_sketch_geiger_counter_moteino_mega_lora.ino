/*
*  Mycodo Custom Input: Moteino Mega Geiger Counter
*  Version: 1.3
*
*  https://github.com/kizniche/Mycodo-custom-inputs/tree/master/geiger%20counter
*
*  Libraries required:
*  https://github.com/mcci-catena/arduino-lmic
*  https://github.com/rocketscream/Low-Power
*/

#include <lmic.h>
#include <hal/hal.h>
#include "LowPower.h"

#define VERSION "1.3"

/*
 *  There are two modes to be operated in:
 *
 *  1. Measure radiation for sample_time_sec seconds and transmit, then
 *     sleep for tx_interval_sec seconds
 *
 *  2. Display radiation measurements on an OLED display and transmit every
 *     lcd_tx_interval_sec seconds
 *
 *  The first mode uses less power due to the lack of an LCD and the use of
 *  deep sleep.
 *
 *  The second mode is useful for viewing the radiation level on an LCD, and
 *  is intended for a wired power connection.
 */

// Uncomment the next line to enable the SD1306 OLED Display
#define USE_SSD1306_OLED 1

/* Note that this display draws between 5 and 10 mA and will deplete your batteries
*  quicker if it's on than if it is not. Therefore, it is recommended to add a
*  switch to turn it on or off or modify the code to do something similar.
*/

//
// Mode 1 options
//

// Measure radiation for this many seconds before transmitting measurements
// Higher durations will increase accuracy but diminish battery life
uint32_t sample_time_sec = 90;  // 1.5 minutes

// Schedule transmission every this many seconds (approximately, since there is no real time clock)
uint32_t tx_interval_sec = 3600;  // 1 hour

//
//  Mode 2 options
//

bool prevent_sleep_when_lcd_detected = true;  // If LCD enabled, don't sleep and use alternate TX interval
uint32_t lcd_tx_interval_sec = 600;  // 10 minutes

//
// End mode options
//

#ifdef USE_SSD1306_OLED
#define OLED_I2C_ADDRESS 0x3c
#include <Adafruit_GFX.h>  // Include core graphics library for the display
#include <Adafruit_SSD1306.h>  // Include Adafruit_SSD1306 library to drive the display
Adafruit_SSD1306 display(128, 64);  // Create display
#include <Fonts/FreeMono9pt7b.h>  // Add a custom font
#endif

#define POWER_PIN 0

bool i2c_error = true;
uint8_t txBuffer[6];
byte TX_COMPLETE = 0;
byte TX_TIMEOUT = 0;

char readBuffer[64];
String readString;
int comma_locations[6];
int sense_cpm;
float sense_usv_h;
int sense_mode;
uint32_t timer_millis;
bool first_run = true;

// TTN Credentials
static const PROGMEM u1_t NWKSKEY[16] = { CHANGE TO YOUR KEY };
static const u1_t PROGMEM APPSKEY[16] = { CHANGE TO YOUR KEY };
static const u4_t DEVADDR = 0x00000000;  // CHANGE TO YOUR DEVICE ADDRESS

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static osjob_t sendjob;

// Pin map for Moteino Mega
const lmic_pinmap lmic_pins = {
  .nss = 4,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 3,
  .dio = {2, 22, 21}, // DIO0, 1, 2
};

void onEvent (ev_t ev) {
//    Serial.print(os_getTime());
//    Serial.print(": ");
    switch(ev) {
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE (inc. RX win. wait)"));
            if (LMIC.txrxFlags & TXRX_ACK)
//                Serial.println(F("Received ack"));
            if (LMIC.dataLen) {
                // data received in rx slot after tx
//                Serial.print(F("Data Received: "));
//                Serial.write(LMIC.frame+LMIC.dataBeg, LMIC.dataLen);
//                Serial.println();
            }
            if (prevent_sleep_when_lcd_detected and !i2c_error);
            else {
                for (int i = 0; i < tx_interval_sec; i+=8) {  // watchdog can sleep max 8 sec
                    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
                }
            }
            loop_measure();
            do_send(&sendjob);
            break;
        default:
//            Serial.print(F("Unknown event: ev: "));
//            Serial.println(ev);
            break;
    }
}

void do_send(osjob_t* j){
    // Check if there is not a current TX/RX job running
    if (LMIC.opmode & OP_TXRXPEND) {
//        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        LMIC_setTxData2(1, txBuffer, sizeof(txBuffer), 0);
        Serial.println(F("Packet queued"));
    }
}

void loop_measure() {
    timer_millis = millis();
    digitalWrite(POWER_PIN, HIGH);
    Serial.println("Measure");
    while (true) {
        if (Serial1.available()) {
            Serial1.readBytesUntil('\n', readBuffer, 64);
            readString = readBuffer;
            find_comma_locations();
            store_data();

            if (prevent_sleep_when_lcd_detected and !i2c_error) {
                if ((millis() - timer_millis) > lcd_tx_interval_sec * 1000) {
                    build_payload();
                    print_measurements();
                    break;
                }
            } else {
                if ((millis() - timer_millis) > sample_time_sec * 1000) {
                    build_payload();
                    print_measurements();
                    break;
                }
            }
        }
    }

    // Only turn off Geiger counter if in Mode 1 for deep sleep
    // If in mode 2, don't turn off because this will reset the speaker state
    if (prevent_sleep_when_lcd_detected and !i2c_error);
    else digitalWrite(POWER_PIN, LOW);
}

void find_comma_locations() {
    comma_locations[0] = readString.indexOf(',');
    comma_locations[1] = readString.indexOf(',',comma_locations[0] + 1);
    comma_locations[2] = readString.indexOf(',',comma_locations[1] + 1);
    comma_locations[3] = readString.indexOf(',',comma_locations[2] + 1);
    comma_locations[4] = readString.indexOf(',',comma_locations[3] + 1);
    comma_locations[5] = readString.indexOf(',',comma_locations[4] + 1);
}

void store_data() {
    String line = "CPS: ";
    line += readString.substring(comma_locations[0] + 1, comma_locations[1]);
    line += ", CPM: ";
    line += readString.substring(comma_locations[2] + 1, comma_locations[3]);
    line += ", uSv/hr: ";
    line += readString.substring(comma_locations[4] + 1, comma_locations[5]);
    line +=  ", Mode: " + readString.substring(comma_locations[5] + 1, comma_locations[5] + 3);
    Serial.println(line);

    if (readString.substring(comma_locations[2] + 1, comma_locations[3]).toInt() > 0) {
        sense_cpm = readString.substring(comma_locations[2] + 1, comma_locations[3]).toInt();
    }

    if (readString.substring(comma_locations[4] + 1, comma_locations[5]).toFloat() > 0) {
        sense_usv_h = readString.substring(comma_locations[4] + 1, comma_locations[5]).toFloat();
    }

    String tmp_sense_mode = readString.substring(comma_locations[5] + 1, comma_locations[5] + 3);
    tmp_sense_mode.trim();
    if (tmp_sense_mode == "S") sense_mode = 1;
    else if (tmp_sense_mode == "F") sense_mode = 2;
    else if (tmp_sense_mode == "I") sense_mode = 3;
    else sense_mode = 4;

    #ifdef USE_SSD1306_OLED
    if (!i2c_error) {
        display.clearDisplay();
        display_header();

        display_text(28, 27, String("CPM: ") + String(sense_cpm));
        display_text(28, 40, String("uSv/hr: ") + String(sense_usv_h));
        String mode;
        if (sense_mode == 1) mode = "Slow";
        else if (sense_mode == 2) mode = "Fast";
        else if (sense_mode == 3) mode = "Instant";
        else mode = "ERR";
        display_text(28, 53, String("Mode: ") + mode);

        display.display();
    }
    #endif
}

void build_payload() {
  // Max CPM value from Geiger counter is 65535
  txBuffer[0] = lowByte(sense_cpm);
  txBuffer[1] = highByte(sense_cpm);

  uint16_t payload_uSv_h = LMIC_f2sflt16(sense_usv_h / 10.0);
  txBuffer[2] = lowByte(payload_uSv_h);
  txBuffer[3] = highByte(payload_uSv_h);

  txBuffer[4] = lowByte(sense_mode);
  txBuffer[5] = highByte(sense_mode);
}

void print_measurements() {
    Serial.print("Send: CPM: ");
    Serial.print(sense_cpm);
    Serial.print(", uSv/hr: ");
    Serial.print(sense_usv_h);
    Serial.print(", Mode: ");
    Serial.println(sense_mode);
}

#ifdef USE_SSD1306_OLED
void display_header() {
    display_text(12, 0, String("Geiger Counter ") + VERSION);
    display_text(23, 9, F("Radiation Level"));
}

void display_text(int x, int y, String text) {
    display.setCursor(x, y);
    display.print(text);
    display.display();
}
#endif

void setup() {
    Serial.begin(115200);
    while (!Serial);

    delay(100);
    Serial.print("Geiger Counter v");
    Serial.println(VERSION);

    Serial1.begin(9600);  // Serial for Geiger counter

    #ifdef USE_SSD1306_OLED
    Serial.println(F("OLED Enabled"));
    Wire.begin();
    Wire.beginTransmission(OLED_I2C_ADDRESS);
    i2c_error = Wire.endTransmission();
    if (i2c_error) {
        Serial.println(F("Cound not find OLED. Not attempting initialization."));
    } else {
        Serial.println(F("OLED Found"));
        display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS);
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(WHITE);
        display.setRotation(0);
        display.setTextWrap(false);
        display_header();
    }
    #endif

    delay(100);

    pinMode(POWER_PIN, OUTPUT);

    os_init();
    LMIC_reset();
    #ifdef PROGMEM
        uint8_t appskey[sizeof(APPSKEY)];
        uint8_t nwkskey[sizeof(NWKSKEY)];
        memcpy_P(appskey, APPSKEY, sizeof(APPSKEY));
        memcpy_P(nwkskey, NWKSKEY, sizeof(NWKSKEY));
        LMIC_setSession (0x1, DEVADDR, nwkskey, appskey);
    #else
        LMIC_setSession (0x1, DEVADDR, NWKSKEY, APPSKEY);
    #endif

    LMIC_selectSubBand(1);
    LMIC_setLinkCheckMode(0);
    LMIC_setDrTxpow(DR_SF7, 14);    // SF7 and max power from module = 14
    LMIC_setClockError(MAX_CLOCK_ERROR * 1 / 100);
    LMIC.dn2Dr = DR_SF9;

    loop_measure();  // First measure
    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}