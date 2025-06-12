import serial
import time
import RPi.GPIO as GPIO

# --- Configuration ---
CRITICAL_DEPTH = 0.8  # Seuil critique en mètres
BUZZER_PIN = 17       # GPIO du buzzer

# Initialisation GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# Lecture de la sonde DST800
def read_depth():
    try:
        with serial.Serial('/dev/ttyUSB1', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            if line.startswith('$SDDBT'):
                parts = line.split(',')
                depth = float(parts[1])
                return depth
    except Exception as e:
        print(f"[ERREUR] Lecture de la sonde : {e}")
    return None

def trigger_alert():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def stop_alert():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def main():
    alert_active = False

    try:
        while True:
            depth = read_depth()
            if depth is not None:
                print(f"[INFO] Profondeur détectée : {depth:.2f} m")

                if depth < CRITICAL_DEPTH and not alert_active:
                    print("[ALERTE] Niveau critique atteint ! Déclenchement du buzzer.")
                    trigger_alert()
                    alert_active = True

                elif depth >= CRITICAL_DEPTH and alert_active:
                    print("[INFO] Retour à la normale. Arrêt de l'alerte.")
                    stop_alert()
                    alert_active = False

            else:
                print("[ATTENTION] Donnée non reçue ou invalide.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArrêt du programme par l'utilisateur.")
    finally:
        stop_alert()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
