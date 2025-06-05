import serial
import time

# Configuration du port série
ser = serial.Serial(
    port='/dev/ttyUSB2',   # Port série à adapter si besoin
    baudrate=4800,         # À adapter selon ton matériel
    timeout=1
)

def buzzer_on():
    # Commande à adapter selon ton matériel
    # Exemple : envoyer "BEEP_ON" pour démarrer le buzzer
    ser.write(b'BEEP_ON 4800\n')

def buzzer_off():
    # Commande à adapter selon ton matériel
    # Exemple : envoyer "BEEP_OFF" pour arrêter le buzzer
    ser.write(b'BEEP_OFF\n')

try:
    while True:
        buzzer_on()
        print("Buzzer ON à 4800Hz")
        time.sleep(2)  # Buzzer allumé pendant 2 secondes
        buzzer_off()
        print("Buzzer OFF")
        time.sleep(3)  # Pause de 3 secondes (pour un cycle total de 5s)
except KeyboardInterrupt:
    buzzer_off()
    ser.close()
    print("Arrêté proprement.")
