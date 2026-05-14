#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm =
Adafruit_PWMServoDriver();

#define SERVOMIN 150
#define SERVOMAX 600

#define TOTAL_SERVOS 6

String data = "";

int currentAngles[TOTAL_SERVOS] =
{90,90,90,90,90,90};

int targetAngles[TOTAL_SERVOS] =
{90,90,90,90,90,90};

int servoMin[TOTAL_SERVOS] =
{0,10,10,0,0,0};

int servoMax[TOTAL_SERVOS] =
{180,170,170,180,180,180};

int servoSpeed = 1;

int angleToPulse(int ang) {

  return map(
    ang,
    0,
    180,
    SERVOMIN,
    SERVOMAX
  );
}

void moveServoSmooth(
  int channel,
  int current,
  int target
) {

  if(current < target) {

    current += servoSpeed;

    if(current > target)
      current = target;
  }

  else if(current > target) {

    current -= servoSpeed;

    if(current < target)
      current = target;
  }

  pwm.setPWM(
    channel,
    0,
    angleToPulse(current)
  );

  currentAngles[channel] = current;
}

void setup() {

  Serial.begin(115200);

  pwm.begin();

  pwm.setPWMFreq(50);

  for(int i=0; i<TOTAL_SERVOS; i++) {

    pwm.setPWM(
      i,
      0,
      angleToPulse(currentAngles[i])
    );
  }

  Serial.println("ROBOT_READY");
}

void loop() {

  readSerialData();

  updateAllServos();

  delay(8);
}

void readSerialData() {

  while(Serial.available()) {

    char c = Serial.read();

    if(c == '\n') {

      processData(data);

      data = "";
    }

    else {

      data += c;
    }
  }
}

void processData(String packet) {

  int values[TOTAL_SERVOS];

  int parsed = sscanf(
    packet.c_str(),
    "%d,%d,%d,%d,%d,%d",
    &values[0],
    &values[1],
    &values[2],
    &values[3],
    &values[4],
    &values[5]
  );

  if(parsed == TOTAL_SERVOS) {

    for(int i=0; i<TOTAL_SERVOS; i++) {

      targetAngles[i] =
      constrain(
        values[i],
        servoMin[i],
        servoMax[i]
      );
    }

    Serial.println("OK");
  }

  else {

    Serial.println("INVALID_PACKET");
  }
}

void updateAllServos() {

  for(int i=0; i<TOTAL_SERVOS; i++) {

    moveServoSmooth(
      i,
      currentAngles[i],
      targetAngles[i]
    );
  }
}