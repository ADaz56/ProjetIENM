#define WATER_SENSOR_PIN A0
#define BUZZER_PIN 9    

const int CRITICAL_LEVEL = 300; // Seuil critique pour le niveau d'eau (à ajuster)
int waterLevel = 0;

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

  // Vérification du seuil critique
  if (waterLevel < CRITICAL_LEVEL) {
    tone(BUZZER_PIN, 2000); // Génère une fréquence de 2 kHz sur le buzzer
    Serial.println("ALERTE : Niveau d'eau critique !");
  } else {
    noTone(BUZZER_PIN); // Arrête le buzzer si le niveau est normal
  }

  delay(600); // Pause pour éviter des lectures trop fréquentes
}
