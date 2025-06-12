#define WATER_SENSOR_PIN A0
#define BUZZER_PIN 9    

const int CRITICAL_LEVEL = 300; // Seuil critique pour le niveau d'eau (à ajuster)
int waterLevel = 0;
bool alertActive = false; // État de l’alerte

void setup() {
  pinMode(WATER_SENSOR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600); // Pour afficher les données sur le moniteur série
}

void loop() {
  // Lecture du niveau d'eau
  waterLevel = analogRead(WATER_SENSOR_PIN);
  Serial.print("Niveau d'eau : ");
  Serial.println(waterLevel);

  // Cas : seuil critique atteint
  if (waterLevel < CRITICAL_LEVEL && !alertActive) {
    tone(BUZZER_PIN, 2000); // Active buzzer (2 kHz)
    Serial.println("🔴 ALERTE : Niveau d'eau critique !");
    alertActive = true;

  // Cas : retour à la normale
  } else if (waterLevel >= CRITICAL_LEVEL && alertActive) {
    noTone(BUZZER_PIN);     // Désactive buzzer
    Serial.println("✅ INFO : Retour à un niveau normal.");
    alertActive = false;
  }

  delay(600); // Pause pour éviter des lectures trop fréquentes
}
