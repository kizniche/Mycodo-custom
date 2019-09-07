/*
* Mycodo Custom Input: Moteino Mega Geiger Counter
* Version: 1.1
*
* https://github.com/kizniche/Mycodo-custom-inputs/tree/master/geiger%20counter
*
* Libraries required:
* https://github.com/mcci-catena/arduino-lmic
* https://github.com/rocketscream/Low-Power
*/

#include <lmic.h>
#include <hal/hal.h>
#include "LowPower.h"

#define POWER_PIN 0

uint8_t txBuffer[6];
byte TX_COMPLETE = 0;
byte TX_TIMEOUT = 0;

char readBuffer[64];
String readString;
int commaLocations[6];
int sense_cpm;
float sense_usv_h;
int sense_mode;
uint32_t timer_millis;

// Measure radiation for this many seconds before transmitting measurements
// Higher durations will increase accuracy but diminish battery life
uint32_t sample_time_sec = 90;

// Schedule transmission every this many seconds (approximately, since there is no real time clock)
uint32_t TX_INTERVAL = 3600; // 1 hour

static const PROGMEM u1_t NWKSKEY[16] = { CHANGE TO YOUR KEY };
static const u1_t PROGMEM APPSKEY[16] = { CHANGE TO YOUR KEY };
static const u4_t DEVADDR = 0x00000000;  // CHANGE TO YOUR DEVICE ADDRESS

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static osjob_t sendjob;

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
            TX_COMPLETE = 1;
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

void FindCommaLocations() {
    commaLocations[0] = readString.indexOf(',');
    commaLocations[1] = readString.indexOf(',',commaLocations[0] + 1);
    commaLocations[2] = readString.indexOf(',',commaLocations[1] + 1);
    commaLocations[3] = readString.indexOf(',',commaLocations[2] + 1);
    commaLocations[4] = readString.indexOf(',',commaLocations[3] + 1);
    commaLocations[5] = readString.indexOf(',',commaLocations[4] + 1);
}

void store_data() {
    String line = "CPS: ";
    line += readString.substring(commaLocations[0] + 1, commaLocations[1]);
    line += ", CPM: ";
    line += readString.substring(commaLocations[2] + 1, commaLocations[3]);
    line += ", uSv/hr: ";
    line += readString.substring(commaLocations[4] + 1, commaLocations[5]);
    line +=  ", Mode: " + readString.substring(commaLocations[5] + 1, commaLocations[5] + 3);
    Serial.println(line);

    if (readString.substring(commaLocations[2] + 1, commaLocations[3]).toInt() > 0) {
        sense_cpm = readString.substring(commaLocations[2] + 1, commaLocations[3]).toInt();
    }

    if (readString.substring(commaLocations[4] + 1, commaLocations[5]).toFloat() > 0) {
        sense_usv_h = readString.substring(commaLocations[4] + 1, commaLocations[5]).toFloat();
    }

    String tmp_sense_mode = readString.substring(commaLocations[5] + 1, commaLocations[5] + 3);
    tmp_sense_mode.trim();
    if (tmp_sense_mode == 'S') sense_mode = 1;
    else if (tmp_sense_mode == 'F') sense_mode = 2;
    else if (tmp_sense_mode == 'I') sense_mode = 3;
    else sense_mode = 4;
}

void get_meas() {
  Serial.print("Send: CPM: ");
  Serial.print(sense_cpm);
  Serial.print(", uSv/hr: ");
  Serial.print(sense_usv_h);
  Serial.print(", Mode: ");
  Serial.println(sense_mode);

  // Max CPM value from Geiger counter is 65535
  txBuffer[0] = lowByte(sense_cpm);
  txBuffer[1] = highByte(sense_cpm);

  uint16_t payload_uSv_h = LMIC_f2sflt16(sense_usv_h / 10.0);
  txBuffer[2] = lowByte(payload_uSv_h);
  txBuffer[3] = highByte(payload_uSv_h);

  txBuffer[4] = lowByte(sense_mode);
  txBuffer[5] = highByte(sense_mode);
}

void setup() {
    Serial.begin(115200);
    while (!Serial);

    delay(100);

    Serial1.begin(9600);  // Serial for Geiger counter

    delay(100);

    pinMode(POWER_PIN, OUTPUT);
    digitalWrite(POWER_PIN, HIGH);

    timer_millis = millis();

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

    os_runloop_once();

    Serial.println("Start");
}

void loop() {
    if (Serial1.available()) {
        Serial1.readBytesUntil('\n', readBuffer, 64);
        readString = readBuffer;
        FindCommaLocations();
        store_data();

        if ((millis() - timer_millis) > sample_time_sec * 1000) {
            digitalWrite(POWER_PIN, LOW);
            get_meas();
            do_send(&sendjob);

            while(TX_COMPLETE != 1) {
                os_runloop_once();
                if (++TX_TIMEOUT > 20000) {
                    Serial.println("Event TO");
                    break;
                }
            }

            TX_COMPLETE = 0;
            TX_TIMEOUT = 0;

            for (int i = 0; i < TX_INTERVAL; i+=8) {  // watchdog can sleep max 8 sec
                LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
            }
            digitalWrite(POWER_PIN, HIGH);

            timer_millis = millis();
        }
    }
}
