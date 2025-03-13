import serial

class NMEAMultiplexer:
    def __init__(self, input_ports, output_port, baudrate=4800):
        self.input_ports = input_ports
        self.output_port = output_port
        self.baudrate = baudrate
        self.serial_connections = []

    def setup_connections(self):
        for port in self.input_ports:
            try:
                ser = serial.Serial(port, self.baudrate, timeout=1)
                self.serial_connections.append(ser)
            except serial.SerialException as e:
                print(f"Error connecting to {port}: {e}")

        try:
            self.output_connection = serial.Serial(self.output_port, self.baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error connecting to output port {self.output_port}: {e}")

    def multiplex_data(self):
        while True:
            for ser in self.serial_connections:
                if ser.in_waiting:
                    line = ser.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('$'):
                        print(f"Received: {line}")
                        self.output_connection.write(line.encode('ascii') + b'\r\n')

    def close_connections(self):
        for ser in self.serial_connections:
            ser.close()
        self.output_connection.close()

if __name__ == "__main__":
    input_ports = ['COM3', 'COM4']  # Remplacez par les ports série appropriés
    output_port = 'COM5'  # Port série de sortie
    multiplexer = NMEAMultiplexer(input_ports, output_port)
    multiplexer.setup_connections()
    try:
        multiplexer.multiplex_data()
    except KeyboardInterrupt:
        multiplexer.close_connections()