import time
from datetime import datetime
import winsound  # Pour simuler le buzzer sous Windows
import os

class WaterSensorSystem:
    def __init__(self):
        self.CRITICAL_LEVEL = 300
        self.current_user = "CabonM"  # Utilisateur actuel
        self.water_level = 0
        self.alarm_active = False
        
        # Paramètres du buzzer
        self.FREQUENCY = 2000  # Fréquence en Hz
        self.DURATION = 500    # Durée en ms
        
        # Créer un dossier pour les logs s'il n'existe pas
        self.log_dir = "water_sensor_logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def clear_screen(self):
        """Nettoie l'écran du terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def sound_alarm(self):
        """Émet un son d'alarme."""
        try:
            winsound.Beep(self.FREQUENCY, self.DURATION)
        except:
            print('\a')  # Alternative pour les systèmes non-Windows

    def log_event(self, message):
        """Enregistre un événement dans le fichier de log."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_file = os.path.join(self.log_dir, f"water_sensor_log_{datetime.now().strftime('%Y%m%d')}.txt")
        
        with open(log_file,
