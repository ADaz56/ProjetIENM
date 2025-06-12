import csv
import datetime
import random

# Génère une trame NMEA complète de profondeur SDDBT
def generate_sddbtr_nmea():
    depth_m = round(random.uniform(1.0, 25.0), 1)  # profondeur simulée en mètres
    depth_ft = round(depth_m * 3.28084, 1)         # conversion en pieds
    depth_fa = round(depth_m / 1.8288, 1)          # conversion en brasses (fathoms)

    # Trame NMEA : $SDDBT,xx.x,f,yy.y,M,zz.z,F*hh
    nmea_body = f"SDDBT,{depth_ft},f,{depth_m},M,{depth_fa},F"
    checksum = calculate_nmea_checksum(nmea_body)
    full_trame = f"${nmea_body}*{checksum}"
    return full_trame

# Calcule le checksum NMEA
def calculate_nmea_checksum(sentence):
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

# Simule la lecture d'une trame et extrait la profondeur
def read_depth_sensor_data():
    try:
        trame = generate_sddbtr_nmea()
        print(f"📡 Trame NMEA simulée : {trame}")
        if trame.startswith('$SDDBT'):
            parts = trame.split(',')
            depth = float(parts[3])  # profondeur en mètres (champ 4)
            return {'depth': depth, 'trame': trame}
    except Exception as e:
        print(f"Erreur de décodage de la trame simulée : {e}")
    return {'depth': None, 'trame': None}

# Enregistre les données
def archive_navigation_data(depth_data, filename='navigation_data.csv'):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'depth_m', 'nmea_trame']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S'),
            'depth_m': depth_data['depth'],
            'nmea_trame': depth_data['trame']
        })

def main():
    depth_data = read_depth_sensor_data()
    if depth_data['depth'] is not None:
        print(f"✅ Profondeur extraite : {depth_data['depth']} m")
    else:
        print("❌ Erreur de lecture de profondeur.")
    archive_navigation_data(depth_data)

if __name__ == "__main__":
    main()
