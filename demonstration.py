import csv
import datetime
import serial
import random

# Lecture des données GPS depuis le capteur USB
def read_gps_data():
    try:
        with serial.Serial('/dev/ttyUSB0', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            if line.startswith('$GPGGA'):
                parts = line.split(',')
                latitude = convert_to_degrees(parts[2])
                longitude = convert_to_degrees(parts[4])
                return {'gps': True, 'latitude': latitude, 'longitude': longitude}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données du capteur GPS")
    # Données simulées
    simulated_lat = round(random.uniform(47.7, 48.0), 6)
    simulated_lon = round(random.uniform(-3.5, -3.0), 6)
    print("🛰️ Données GPS simulées utilisées.")
    return {'gps': False, 'latitude': simulated_lat, 'longitude': simulated_lon}

def convert_to_degrees(value):
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
            if line.startswith('$SDDBT'):
                parts = line.split(',')
                depth = float(parts[1])
                return {'depth': depth}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données de la sonde de profondeur")
    # Donnée simulée
    simulated_depth = round(random.uniform(1.0, 10.0), 2)
    print("🌊 Donnée de profondeur simulée utilisée.")
    return {'depth': simulated_depth}

# Lecture des données de la girouette-anémomètre
def read_anemometer_data():
    try:
        with serial.Serial('/dev/ttyUSB2', baudrate=4800, timeout=1) as ser:
            line = ser.readline().decode('ascii', errors='replace')
            if line.startswith('$WIMWV'):
                parts = line.split(',')
                wind_speed = float(parts[3])
                wind_direction = float(parts[1])
                return {'wind_speed': wind_speed, 'wind_direction': wind_direction}
    except serial.SerialException:
        print("Erreur: Impossible de lire les données de l’anémomètre")
    # Données simulées
    simulated_speed = round(random.uniform(2.0, 15.0), 2)
    simulated_dir = round(random.uniform(0, 360), 1)
    print("💨 Données vent simulées utilisées.")
    return {'wind_speed': simulated_speed, 'wind_direction': simulated_dir}

# Vérifier si les capteurs sont opérationnels
def check_sensors(gps_data, depth_data, anemometer_data):
    operational = True
    if not gps_data['gps']:
        print("⚠️ Capteur GPS non opérationnel (données simulées)")
        operational = False
    if 'depth' in depth_data and depth_data['depth'] is None:
        print("⚠️ Capteur de profondeur non opérationnel (donnée simulée)")
        operational = False
    if 'wind_speed' in anemometer_data and (anemometer_data['wind_speed'] is None or anemometer_data['wind_direction'] is None):
        print("⚠️ Anémomètre non opérationnel (données simulées)")
        operational = False
    return operational

# Archiver les données de navigation
def archive_navigation_data(gps_data, depth_data, anemometer_data, filename='navigation_data.csv'):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'latitude', 'longitude', 'depth', 'wind_speed', 'wind_direction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
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
        print("✅ Tous les capteurs sont opérationnels.")
    else:
        print("⚠️ Données partiellement simulées utilisées.")

    archive_navigation_data(gps_data, depth_data, anemometer_data)

if __name__ == "__main__":
    main()
