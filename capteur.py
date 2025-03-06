import csv
import datetime
import serial

# Lecture des données GPS depuis le capteur USB
def read_gps_data():
    try:
        with serial.Serial('/dev/ttyUSB0', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            if line.startswith('$GPGGA'):  # Exemple pour une ligne NMEA GGA
                parts = line.split(',')
                latitude = convert_to_degrees(parts[2])
                longitude = convert_to_degrees(parts[4])
                return {'gps': True, 'latitude': latitude, 'longitude': longitude}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données du capteur GPS")
    return {'gps': False, 'latitude': None, 'longitude': None}

def convert_to_degrees(value):
    # Convertir les valeurs NMEA en degrés décimaux
    if not value:
        return None
    degrees = float(value[:2])
    minutes = float(value[2:])
    return degrees + minutes / 60

# Lecture des données de la sonde de profondeur
def read_depth_sensor_data():
    try:
        with serial.Serial('/dev/ttyUSB1', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            # Exemple de lecture de profondeur (à adapter selon le capteur réel)
            if line.startswith('$SDDBT'):
                parts = line.split(',')
                depth = float(parts[1])  # Profondeur en mètres
                return {'depth': depth}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données de la sonde de profondeur")
    return {'depth': None}

# Lecture des données de la girouette-anémomètre
def read_anemometer_data():
    try:
        with serial.Serial('/dev/ttyUSB2', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            # Exemple de lecture des données (à adapter selon le capteur réel)
            if line.startswith('$WIMWV'):
                parts = line.split(',')
                wind_speed = float(parts[3])  # Vitesse du vent en m/s
                wind_direction = float(parts[1])  # Direction du vent en degrés
                return {'wind_speed': wind_speed, 'wind_direction': wind_direction}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données de la girouette-anémomètre")
    return {'wind_speed': None, 'wind_direction': None}

# Vérifier si les capteurs sont opérationnels
def check_sensors(gps_data, depth_data, anemometer_data):
    operational = True
    if not gps_data['gps']:
        print("Erreur: Capteur GPS non opérationnel")
        operational = False
    if depth_data['depth'] is None:
        print("Erreur: Capteur de profondeur non opérationnel")
        operational = False
    if anemometer_data['wind_speed'] is None or anemometer_data['wind_direction'] is None:
        print("Erreur: Anémomètre non opérationnel")
        operational = False
    return operational

# Archiver les données de navigation
def archive_navigation_data(gps_data, depth_data, anemometer_data, filename='navigation_data.csv'):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'latitude', 'longitude', 'depth', 'wind_speed', 'wind_direction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Écrire l'en-tête si le fichier est vide
        if csvfile.tell() == 0:
            writer.writeheader()
        # Écrire les données des capteurs avec un horodatage
        writer.writerow({
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'latitude': gps_data['latitude'],
            'longitude': gps_data['longitude'],
            'depth': depth_data['depth'],
            'wind_speed': anemometer_data['wind_speed'],
            'wind_direction': anemometer_data['wind_direction']
        })

def main():
    gps_data = read_gps_data()
    depth_data = read_depth_sensor_data()
    anemometer_data = read_anemometer_data()
    if check_sensors(gps_data, depth_data, anemometer_data):
        print("Tous les capteurs sont opérationnels.")
    else:
        print("Certains capteurs ne sont pas opérationnels.")
    archive_navigation_data(gps_data, depth_data, anemometer_data)

if __name__ == "__main__":
    main()