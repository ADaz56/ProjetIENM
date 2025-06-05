import unittest
from unittest.mock import MagicMock, patch
import os
from datetime import datetime
import serial
from freezegun import freeze_time

# Import de la classe à tester
from water_sensor import WaterSensorSystem

class TestWaterSensorSystem(unittest.TestCase):
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Mock du port série
        self.serial_mock = MagicMock(spec=serial.Serial)
        self.serial_patcher = patch('serial.Serial', return_value=self.serial_mock)
        self.serial_mock_class = self.serial_patcher.start()
        
        # Mock pour os.path.exists et os.makedirs
        self.path_exists_patcher = patch('os.path.exists', return_value=False)
        self.makedirs_patcher = patch('os.makedirs')
        self.path_exists_mock = self.path_exists_patcher.start()
        self.makedirs_mock = self.makedirs_patcher.start()
        
        # Création de l'instance avec le port série mocké
        self.system = WaterSensorSystem()
        
        # Configuration du mock série
        self.serial_mock.port = '/dev/ttyUSB0'
        self.serial_mock.is_open = True
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.serial_patcher.stop()
        self.path_exists_patcher.stop()
        self.makedirs_patcher.stop()

    def test_init(self):
        """Test de l'initialisation du système"""
        self.assertEqual(self.system.CRITICAL_LEVEL_METERS, 0.3)
        self.assertEqual(self.system.MAX_LEVEL_METERS, 1.30)
        self.assertEqual(self.system.current_user, "CabonM")
        self.assertEqual(self.system.log_dir, "/home/pi/water_sensor_logs")
        
        # Vérifie que le dossier de logs est créé si inexistant
        self.makedirs_mock.assert_called_once_with("/home/pi/water_sensor_logs")

    @freeze_time("2025-05-12 08:01:17")
    def test_log_data(self):
        """Test de la fonction de journalisation"""
        test_data = "0.75"
        mock_open = unittest.mock.mock_open()
        
        with patch('builtins.open', mock_open):
            self.system.log_data(test_data)
            
        # Vérifie que le fichier est ouvert avec le bon nom
        expected_filename = os.path.join(
            "/home/pi/water_sensor_logs",
            f"sensor_log_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        mock_open.assert_called_once_with(expected_filename, 'a', encoding='utf-8')
        
        # Vérifie le contenu écrit
        expected_log = "[2025-05-12 08:01:17] CabonM: 0.75\n"
        mock_open().write.assert_called_once_with(expected_log)

    def test_read_sensor_data_with_data(self):
        """Test de la lecture du capteur avec données disponibles"""
        # Configure le mock pour simuler des données disponibles
        self.serial_mock.in_waiting = True
        self.serial_mock.readline.return_value = b"0.75\n"
        
        data = self.system.read_sensor_data()
        self.assertEqual(data, "0.75")
        self.serial_mock.readline.assert_called_once()

    def test_read_sensor_data_no_data(self):
        """Test de la lecture du capteur sans données disponibles"""
        # Configure le mock pour simuler l'absence de données
        self.serial_mock.in_waiting = False
        
        data = self.system.read_sensor_data()
        self.assertIsNone(data)
        self.serial_mock.readline.assert_not_called()

    def test_read_sensor_data_error(self):
        """Test de la lecture du capteur avec erreur"""
        # Configure le mock pour lever une exception
        self.serial_mock.in_waiting = True
        self.serial_mock.readline.side_effect = Exception("Erreur de lecture")
        
        data = self.system.read_sensor_data()
        self.assertIsNone(data)

    def test_cleanup(self):
        """Test de la fonction de nettoyage"""
        self.system.cleanup()
        self.serial_mock.close.assert_called_once()

    @patch('time.sleep', return_value=None)
    def test_run(self, mock_sleep):
        """Test de la boucle principale avec interruption"""
        # Configure le mock pour simuler une exécution puis une interruption
        self.serial_mock.in_waiting = True
        self.serial_mock.readline.return_value = b"0.75\n"
        
        # Simule une KeyboardInterrupt après la première itération
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Capture la sortie standard pour vérification
        with patch('builtins.print') as mock_print:
            self.system.run()
            
        # Vérifie que les messages attendus ont été affichés
        expected_calls = [
            unittest.mock.call('\nDémarrage de la lecture du capteur...'),
            unittest.mock.call(f"Port: {self.serial_mock.port}"),
            unittest.mock.call('Appuyez sur Ctrl+C pour arrêter\n'),
            unittest.mock.call('\n' + '=' * 60),
            unittest.mock.call(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"),
            unittest.mock.call(f"Current User's Login: {self.system.current_user}")
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)

    def test_alternative_usb_port(self):
        """Test de la création du système avec le port USB alternatif"""
        # Force une exception sur le premier port
        self.serial_mock_class.side_effect = [serial.SerialException, MagicMock()]
        
        with self.assertRaises(serial.SerialException):
            system1 = WaterSensorSystem()
            
        # Vérifie que le second port est utilisé
        system2 = WaterSensorSystemUSB1()
        self.assertEqual(system2.sensor.port, '/dev/ttyUSB1')

if __name__ == '__main__':
    unittest.main()
