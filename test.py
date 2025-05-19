import serial
import pynmea2
import RPi.GPIO as GPIO
from time import sleep

# Configuration du buzzer
BUZZER_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Configuration du port série (adaptez à votre setup)
ser = serial.Serial('/dev/ttyUSB2', 4800, timeout=1)

def declencher_buzzer(duree_ms=500):
    """Active le buzzer pendant une durée spécifiée"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    sleep(duree_ms / 1000)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

try:
    while True:
        data = ser.readline().decode('ascii', errors='replace').strip()
        
        if data.startswith('$SDDBT'):  # Trame de profondeur DST800
            try:
                msg = pynmea2.parse(data)
                profondeur = msg.depth_meters  # Valeur en mètres
                print(f"Profondeur: {profondeur}m")

                # Exemple: Alarme si profondeur < 2m
                if profondeur < 2:
                    declencher_buzzer(1000)  # Bip long de 1 seconde
                    sleep(0.5)  # Anti-rebond

            except pynmea2.ParseError:
                print("Erreur de parsing NMEA")

except KeyboardInterrupt:
    GPIO.cleanup()
    ser.close()
