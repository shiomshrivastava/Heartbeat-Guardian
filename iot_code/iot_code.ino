#include <Arduino.h>
#include <ArduinoJson.h>

// ---------- HEART RATE SENSOR SETUP ----------
int sensorPin = A0;
const int samples = 20;
int readings[samples];
int index = 0;
long sum = 0;

bool beatDetected = false;
unsigned long lastBeatTime = 0;
float bpm = 0;
float bpmAvg = 0;
int bpmCount = 0;
int accurateReadings = 0;
float bpmReadings15[15];  // to store 15 valid readings

// ---------- BUZZER + LED SETUP ----------
int buzzer = 8;
int led1 = 4;
int led2 = 2;

// ---------- BUTTON SETUP ----------
int buttonPin = 6;
bool heartMonitorActive = false;   // start when button pressed
bool buttonPressed = false;

// ---------- SETUP ----------
void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);  // internal pull-up

  for (int i = 0; i < samples; i++) readings[i] = 0;

  Serial.println("💓 System Ready! Press the button to start measuring...");
}

// ----------- SEND JSON FUNCTION (no encryption) -----------
void sendPlainJSON() {
  StaticJsonDocument<512> doc;
  for (int i = 0; i < 15; i++) {
    doc["readings"][i] = bpmReadings15[i];
  }
  String jsonStr;
  serializeJson(doc, jsonStr);

  Serial.println("📤 Sending Data to Streamlit...");
  Serial.println(jsonStr);
  Serial.println("✅ JSON Sent Successfully!");
}

// ----------- RESET MEASUREMENT -----------
void resetMeasurement() {
  beatDetected = false;
  bpm = bpmAvg = 0;
  bpmCount = 0;
  accurateReadings = 0;
  index = 0;
  sum = 0;
  for (int i = 0; i < 15; i++) bpmReadings15[i] = 0;
  for (int i = 0; i < samples; i++) readings[i] = 0;

  digitalWrite(buzzer, LOW);
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);

  Serial.println("🔁 Restarted Heartbeat Measurement!");
}

// ----------- MAIN LOOP -----------
void loop() {
  int buttonState = digitalRead(buttonPin);

  // ---- Button Press Logic ----
  if (buttonState == LOW && !buttonPressed) {
    buttonPressed = true;

    heartMonitorActive = true;
    resetMeasurement();  // restart from beginning
    Serial.println("🫀 Button Pressed → Starting 15 Heartbeat Readings!");
  }

  if (buttonState == HIGH) {
    buttonPressed = false;
  }

  // ---- Heartbeat Measurement Logic ----
  if (heartMonitorActive) {
    int sensorValue = analogRead(sensorPin);

    sum -= readings[index];
    readings[index] = sensorValue;
    sum += readings[index];
    index = (index + 1) % samples;
    int avg = sum / samples;

    if (!beatDetected && sensorValue > avg + 20) {
      beatDetected = true;
      unsigned long now = millis();

      if (lastBeatTime > 0) {
        unsigned long delta = now - lastBeatTime;
        if (delta > 300 && delta < 2000) {
          bpm = 60000.0 / delta;
          bpmAvg = ((bpmAvg * bpmCount) + bpm) / (bpmCount + 1);
          if (bpmCount < 4) bpmCount++;

          if (accurateReadings < 15) {
            bpmReadings15[accurateReadings] = bpmAvg;
            accurateReadings++;
            Serial.print("Heartbeat #");
            Serial.print(accurateReadings);
            Serial.print(" | BPM: ");
            Serial.println(bpmAvg, 1);
          }
        }
      }
      lastBeatTime = now;
    }

    if (beatDetected && sensorValue < avg + 5) {
      beatDetected = false;
    }

    if (accurateReadings >= 15) {
      heartMonitorActive = false;
      Serial.println("✅ 15 Heartbeats Recorded! Sending JSON...");
      sendPlainJSON();

      // Buzzer + LED Sequence
      for (int i = 0; i < 15; i++) {
        digitalWrite(buzzer, HIGH);
        digitalWrite(led1, HIGH);
        delay(200);
        digitalWrite(buzzer, LOW);
        digitalWrite(led1, LOW);
        delay(300);
      }

      digitalWrite(led2, HIGH);
      Serial.println("🔔 Buzzer Done! LED2 ON (Process Complete)");
    }

    delay(10);
  }
}
