fais un programme de test similaire pour verifier que ce programme fonctionne : 
import time
from datetime import datetime
import os
import serial

class WaterSensorSystem:
    def __init__(self):
        self.CRITICAL_LEVEL_METERS = 0.3
        self.MAX_LEVEL_METERS = 1.30
        self.current_user = "CabonM"
        
        try:
            # Connection directe au port USB pour le ch341 (Dev 17)
            self.sensor = serial.Serial(
                port='/dev/ttyUSB0',  # Essayez aussi ttyUSB1 si ça ne fonctionne pas
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            print(f"Connexion établie sur {self.sensor.port}")
        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            raise

        self.log_dir = "/home/pi/water_sensor_logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def read_sensor_data(self):
        """Lit les données brutes du capteur."""
        try:
            if self.sensor.in_waiting:  # Vérifie s'il y a des données à lire
                raw_data = self.sensor.readline().decode('utf-8').strip()
                print(f"Données brutes reçues: {raw_data}")  # Debug
                return raw_data
        except Exception as e:
            print(f"Erreur de lecture: {str(e)}")
        return None

    def run(self):
        print("\nDémarrage de la lecture du capteur...")
        print(f"Port: {self.sensor.port}")
        print("Appuyez sur Ctrl+C pour arrêter\n")

        try:
            while True:
                # Affichage de l'en-tête
                print("\n" + "=" * 60)
                current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                print(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {current_time}")
                print(f"Current User's Login: {self.current_user}")
                
                # Lecture du capteur
                data = self.read_sensor_data()
                if data:
                    print(f"Mesure: {data}")
                    self.log_data(data)
                else:
                    print("Attente de données...")
                
                print("=" * 60)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nArrêt du programme")
        finally:
            self.cleanup()

    def log_data(self, data):
        """Enregistre les données dans un fichier log."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_file = os.path.join(self.log_dir, f"sensor_log_{datetime.now().strftime('%Y%m%d')}.txt")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {self.current_user}: {data}\n")

    def cleanup(self):
        """Ferme proprement le port série."""
        try:
            if hasattr(self, 'sensor') and self.sensor.is_open:
                self.sensor.close()
            print("\nPort série fermé")
        except Exception as e:
            print(f"Erreur lors de la fermeture: {str(e)}")

if __name__ == "__main__":
    # Essaie d'abord avec ttyUSB0
    try:
        system = WaterSensorSystem()
        system.run()
    except Exception as e:
        print(f"Erreur sur ttyUSB0: {str(e)}")
        print("Tentative avec ttyUSB1...")
        
        # Si ttyUSB0 échoue, essaie avec ttyUSB1
        try:
            class WaterSensorSystemUSB1(WaterSensorSystem):
                def __init__(self):
                    self.CRITICAL_LEVEL_METERS = 0.3
                    self.MAX_LEVEL_METERS = 1.30
                    self.current_user = "CabonM"
                    
                    self.sensor = serial.Serial(
                        port='/dev/ttyUSB1',
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1
                    )
                    print(f"Connexion établie sur {self.sensor.port}")
                    
                    self.log_dir = "/home/pi/water_sensor_logs"
                    if not os.path.exists(self.log_dir):
                        os.makedirs(self.log_dir)

            system = WaterSensorSystemUSB1()
            system.run()
        except Exception as e:
            print(f"Erreur sur ttyUSB1: {str(e)}")
            print("\nVérifiez que:")
            print("1. Le capteur est bien branché")
            print("2. Les permissions sont correctes (sudo chmod 666 /dev/ttyUSB*)")
            print("3. L'utilisateur est dans le groupe dialout (sudo usermod -a -G dialout $USER)")
