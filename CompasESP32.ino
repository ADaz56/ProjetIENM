#include <HardwareSerial.h>

#define RXD2 16
#define TXD2 17

HardwareSerial SerialCompas(2);
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  Serial.println("Initialisation de la liaison série avec le compas NKE 9X");
  SerialCompas.begin(4800, SERIAL_8N1, RXD2, TXD2);
  Serial.println("Liaison série avec le compas NKE 9X initialisée");
}
void loop() {
  if (SerialCompas.available()) {
    String compasData = SerialCompas.readStringUntil('\n');
    Serial.println("Données reçues du compas NKE 9X : " + compasData);
  }
  delay(100);
}