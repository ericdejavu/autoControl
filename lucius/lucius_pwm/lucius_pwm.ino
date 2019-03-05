#include <SoftPWM.h>
#include <SoftPWM_timer.h>

unsigned long time = 0;

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(5);
    //60Hz refresh
    SoftPWMBegin();
}

int value = 0;

void loop() {
    if(Serial.available()) {
        send();
        value = Serial.parseInt();
        delay(5);
        if (value <= 100) {
          run_out(value);
        } else if(value == 1000) {
          delay(10);
          Serial.println("test");
          delay(1);
        }
        time = millis();
    }
    locked_send();
    // 33Hz refresh
    delay(15);
}

void locked_send() {
    if (millis() - time > 500) {
        send();
    }
}

void send() {
    int angle = analogRead(A1);
    if (angle > 700) {
      angle = 700;
    }
    angle = map(angle,0,700,0,180);
    Serial.print(angle);
    Serial.print(",");
    Serial.println(value);
}

void run_out(int value) {
    if (value < 0) {
        outL(abs(value));
    } else {
        outR(value);
    }
}

void out(int valueL,int valueR) {
    SoftPWMSetPercent(A3,valueL);
    SoftPWMSetPercent(A4,valueR);
}

void outL(int value) {
    out(0,value);
}

void outR(int value) {
    out(value,0);
}
