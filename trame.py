import serial

def parse_nmea(sentence):
    if not sentence.startswith('$') or '*' not in sentence:
        return None

    data, checksum = sentence.strip().split('*')
    fields = data.split(',')

    sentence_type = fields[0][3:]  # Enlève le '$GP' ou '$GN'

    if sentence_type == 'GGA':
        return {
            "Type": "GGA - Fix GPS",
            "Heure": fields[1],
            "Latitude": fields[2] + " " + fields[3],
            "Longitude": fields[4] + " " + fields[5],
            "Qualité du fix": fields[6],
            "Nombre de satellites": fields[7],
            "Altitude": fields[9] + " " + fields[10],
        }

    elif sentence_type == 'RMC':
        return {
            "Type": "RMC - Position minimale",
            "Heure": fields[1],
            "Statut": fields[2],
            "Latitude": fields[3] + " " + fields[4],
            "Longitude": fields[5] + " " + fields[6],
            "Vitesse (noeuds)": fields[7],
            "Cap vrai": fields[8],
            "Date": fields[9],
        }

    else:
        return {"Type inconnu": sentence}


# Remplace par ton port série (ex : /dev/ttyUSB0)
PORT = "/dev/ttyUSB0"
BAUD = 4800

try:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print(f"Lecture sur {PORT} à {BAUD} bauds...\n")
        while True:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line:
                info = parse_nmea(line)
                if info:
                    print("\n--- Trame NMEA décodée ---")
                    for k, v in info.items():
                        print(f"{k} : {v}")
except Exception as e:
    print("Erreur :", e)
