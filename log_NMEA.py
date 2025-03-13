import serial
import logging

# Configuration du logging
logging.basicConfig(filename='nmea_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def read_nmea(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        while True:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$'):
                logging.info(f"NMEA Sentence: {line}")
                print(f"Logged: {line}")
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    port = 'COM3'  # Remplacez par le port série approprié
    baudrate = 4800  # Vitesse de transmission NMEA 0183 standard
    read_nmea(port, baudrate)