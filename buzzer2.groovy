#define BUZZER_PIN 9

const int CRITICAL_LEVEL = 300; // Seuil critique pour le niveau d'eau (à ajuster)
int waterLevel = 0;
String inputString = "";      // String pour stocker les données entrantes
boolean stringComplete = false;  // Indique si une ligne complète a été reçue

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);  // Communication série principale
  inputString.reserve(200);  // Réserve de l'espace pour la chaîne entrante
}

void loop() {
  // Si une ligne complète a été reçue via USB
  if (stringComplete) {
    // Convertit la chaîne en entier
    waterLevel = inputString.toInt();
    
    Serial.print("Niveau d'eau reçu : ");
    Serial.println(waterLevel);

    // Vérification du seuil critique
    if (waterLevel < CRITICAL_LEVEL) {
      tone(BUZZER_PIN, 2000); // Génère une fréquence de 2 kHz sur le buzzer
      Serial.println("ALERTE : Niveau d'eau critique !");
    } else {
      noTone(BUZZER_PIN); // Arrête le buzzer si le niveau est normal
    }

    // Réinitialise la chaîne pour la prochaine lecture
    inputString = "";
    stringComplete = false;
  }

  delay(100); // Petit délai pour éviter de surcharger le processeur
}

// Fonction appelée à chaque réception de données sur le port série
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    // Si on reçoit un retour à la ligne, on marque la chaîne comme complète
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      // Sinon on ajoute le caractère à la chaîne
      inputString += inChar;
    }
  }
}