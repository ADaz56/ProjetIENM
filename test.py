import time
from datetime import datetime
import os
import serial
import subprocess

class DST800Decoder:
    def __init__(self):
        self.current_user = "CabonM"
        self.connected = False
        self.last_data_time = None
        
        # Trouver le bon port
        self.port = self.find_port()
        if not self.port:
            raise Exception("Port série non trouvé")

        # Configuration du capteur DST800
        try:
            self.sensor = serial.Serial(
                port=self.port,
                baudrate=4800,        # Vitesse standard DST800
                bytesize=serial.EIGHTBITS,
                parity=serial.NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Configuration des lignes de contrôle
            self.sensor.setRTS(True)
            self.sensor.setDTR(True)
            
            # Reset des buffers
            self.sensor.reset_input_buffer()
            self.sensor.reset_output_buffer()
            
            self.connected = True
            print(f"Connexion établie au DST800 sur {self.port}")
            
        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            raise

    def find_port(self):
        """Trouve le port série approprié."""
        try:
            # Vérification des ports disponibles
            print("\nRecherche des ports série disponibles...")
            
            # Liste tous les ports ttyUSB
            cmd = "ls /dev/ttyUSB*"
            output = subprocess.check_output(cmd, shell=True, text=True)
            ports = output.strip().split('\n')
            
            print("Ports trouvés:", ports)
            
            # Vérifie chaque port
            for port in ports:
                print(f"\nTest du port {port}...")
                try:
                    test_serial = serial.Serial(
                        port=port,
                        baudrate=4800,
                        timeout=1
                    )
                    test_serial.close()
                    print(f"Port {port} disponible")
                    return port
                except:
                    print(f"Port {port} non disponible")
                    continue
                    
            return '/dev/ttyUSB1'  # Port par défaut
            
        except Exception as e:
            print(f"Erreur lors de la recherche du port: {str(e)}")
            return '/dev/ttyUSB1'  # Port par défaut

    def check_connection(self):
        """Vérifie l'état de la connexion."""
        if not self.connected:
            return False
            
        if self.last_data_time and time.time() - self.last_data_time > 5:
            print("Pas de données reçues depuis 5 secondes, tentative de reconnexion...")
            self.reconnect()
            
        return self.connected

    def reconnect(self):
        """Tente de rétablir la connexion."""
        try:
            if self.sensor.is_open:
                self.sensor.close()
            
            time.sleep(1)
            
            self.sensor.open()
            self.sensor.reset_input_buffer()
            self.sensor.reset_output_buffer()
            self.sensor.setRTS(True)
            self.sensor.setDTR(True)
            
            print("Reconnexion réussie")
            self.connected = True
            
        except Exception as e:
            print(f"Échec de la reconnexion: {str(e)}")
            self.connected = False

    def read_raw_data(self):
        """Lit les données brutes du capteur."""
        try:
            if not self.sensor.is_open:
                self.sensor.open()
                
            if self.sensor.in_waiting:
                data = self.sensor.read(self.sensor.in_waiting)
                self.last_data_time = time.time()
                return data
            
            # Si pas de données, on essaie d'envoyer une requête
            self.sensor.write(b'\r\n')
            time.sleep(0.1)
            
            if self.sensor.in_waiting:
                data = self.sensor.read(self.sensor.in_waiting)
                self.last_data_time = time.time()
                return data
                
            return None
            
        except Exception as e:
            print(f"Erreur de lecture: {str(e)}")
            self.connected = False
            return None

    def decode_data(self, data):
        """Décode les données reçues."""
        if not data:
            return None
            
        try:
            # Affichage des données brutes pour debug
            print("\nDonnées brutes reçues:")
            print(f"Hex: {' '.join([hex(b) for b in data])}")
            print(f"ASCII: {data}")
            
            # Essai de décodage en différents formats
            try:
                ascii_data = data.decode('ascii').strip()
                print(f"Décodage ASCII: {ascii_data}")
                return ascii_data
            except:
                pass
                
            try:
                utf8_data = data.decode('utf-8').strip()
                print(f"Décodage UTF-8: {utf8_data}")
                return utf8_data
            except:
                pass
                
            return f"Données brutes: {' '.join([hex(b) for b in data])}"
            
        except Exception as e:
            print(f"Erreur de décodage: {str(e)}")
            return None

    def run(self):
        print("\nDémarrage du décodeur DST800")
        print(f"Port: {self.port}")
        print(f"Vitesse: {self.sensor.baudrate} bauds")
        print("Appuyez sur Ctrl+C pour arrêter\n")

        try:
            while True:
                print("\n" + "=" * 60)
                current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                print(f"Date/Heure (UTC): {current_time}")
                print(f"Utilisateur: {self.current_user}")
                
                if self.check_connection():
                    raw_data = self.read_raw_data()
                    if raw_data:
                        decoded = self.decode_data(raw_data)
                        if decoded:
                            print(f"\nDonnées décodées: {decoded}")
                    else:
                        print("\nAucune donnée reçue")
                else:
                    print("\nPas de connexion au capteur")
                
                print("=" * 60)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nArrêt du programme")
        finally:
            if hasattr(self, 'sensor') and self.sensor.is_open:
                self.sensor.close()
                print("Port série fermé")

if __name__ == "__main__":
    try:
        print("\nVérification des ports série...")
        os.system("ls -l /dev/ttyUSB*")
        
        print("\nVérification des permissions...")
        os.system("sudo chmod 666 /dev/ttyUSB*")
        
        print("\nInformations sur le périphérique CH341...")
        os.system("dmesg | grep ch341")
        
        decoder = DST800Decoder()
        decoder.run()
        
    except Exception as e:
        print(f"\nErreur fatale: {str(e)}")
        print("\nVérifications à faire:")
        print("1. Le capteur DST800 est bien branché")
        print("2. Le convertisseur USB est reconnu:")
        print("   dmesg | grep ch341")
        print("3. Les ports série sont disponibles:")
        print("   ls -l /dev/ttyUSB*")
        print("4. Les permissions sont correctes:")
        print("   sudo chmod 666 /dev/ttyUSB*")
