const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

describe('Interface de Configuration Tests', () => {
    let dom;
    let document;
    let window;
    let localStorage;
    let mockDate;

    beforeEach(() => {
        // Mock de la date
        mockDate = new Date('2025-05-12T07:49:10Z');
        global.Date = class extends Date {
            constructor() {
                return mockDate;
            }
            static now() {
                return mockDate.getTime();
            }
        };

        // Configuration du DOM
        dom = new JSDOM(`
            <!DOCTYPE html>
            <html>
            <body>
                <div class="user-info">
                    <span>Utilisateur: <span id="current-user">CabonM</span></span>
                    <span>Date et Heure: <span id="current-time" class="datetime"></span></span>
                </div>
                <div class="container">
                    <input type="number" id="threshold" class="form-input">
                    <img id="thresholdStatus" style="display: none;">
                    
                    <input type="text" id="nmea-type" class="form-input">
                    <img id="nmeaStatus" style="display: none;">
                    
                    <input type="text" id="ssid" class="form-input">
                    <input type="password" id="password" class="form-input">
                    <select id="security" class="form-input">
                        <option value="WEP">WEP</option>
                        <option value="WPA">WPA</option>
                        <option value="WPA/WPA2-Personal">WPA/WPA2-Personal</option>
                    </select>
                    <img id="wifiStatus" style="display: none;">
                </div>
            </body>
            </html>
        `, {
            url: 'http://localhost',
            runScripts: 'dangerously',
            resources: 'usable',
        });

        document = dom.window.document;
        window = dom.window;

        // Mock localStorage
        localStorage = {
            data: {},
            getItem: jest.fn(function(key) {
                return this.data[key];
            }),
            setItem: jest.fn(function(key, value) {
                this.data[key] = value;
            }),
            clear: function() {
                this.data = {};
            }
        };

        // Mock fetch
        global.fetch = jest.fn(() =>
            Promise.resolve({
                text: () => Promise.resolve('')
            })
        );

        // Mock URL.createObjectURL
        global.URL.createObjectURL = jest.fn();

        // Configuration des variables globales
        global.window = window;
        global.document = document;
        global.localStorage = localStorage;

        // Implémentation des fonctions
        window.showStatusIcon = function(icon, isValid) {
            icon.style.display = 'inline';
            icon.src = isValid ? 'check.svg' : 'error.svg';
            icon.alt = isValid ? 'Succès' : 'Erreur';
            setTimeout(() => {
                icon.style.display = 'none';
            }, 3000);
        };

        window.saveThreshold = function() {
            const threshold = document.getElementById('threshold').value;
            const statusIcon = document.getElementById('thresholdStatus');
            
            if (threshold && parseFloat(threshold) > 0) {
                localStorage.setItem('waterThreshold', threshold);
                this.logToFile('saveThreshold', { threshold: threshold });
                this.showStatusIcon(statusIcon, true);
            } else {
                this.showStatusIcon(statusIcon, false);
            }
        };

        window.saveNmeaConfig = function() {
            const nmeaType = document.getElementById('nmea-type').value;
            const statusIcon = document.getElementById('nmeaStatus');
            
            if (nmeaType && nmeaType.trim() !== '') {
                localStorage.setItem('nmeaType', nmeaType);
                this.logToFile('saveNmeaConfig', { nmeaType: nmeaType });
                this.showStatusIcon(statusIcon, true);
            } else {
                this.showStatusIcon(statusIcon, false);
            }
        };

        window.saveWifiConfig = function() {
            const ssid = document.getElementById('ssid').value;
            const password = document.getElementById('password').value;
            const security = document.getElementById('security').value;
            const statusIcon = document.getElementById('wifiStatus');
            
            if (ssid && password && security) {
                const wifiConfig = { ssid, password, security };
                localStorage.setItem('wifiConfig', JSON.stringify(wifiConfig));
                this.logToFile('saveWifiConfig', {
                    ssid: ssid,
                    security: security,
                    password: '********'
                });
                this.showStatusIcon(statusIcon, true);
            } else {
                this.showStatusIcon(statusIcon, false);
            }
        };

        window.logToFile = jest.fn();

        window.updateDateTime = function() {
            document.getElementById('current-time').textContent = 
                mockDate.getUTCFullYear() + '-' + 
                String(mockDate.getUTCMonth() + 1).padStart(2, '0') + '-' +
                String(mockDate.getUTCDate()).padStart(2, '0') + ' ' +
                String(mockDate.getUTCHours()).padStart(2, '0') + ':' +
                String(mockDate.getUTCMinutes()).padStart(2, '0') + ':' +
                String(mockDate.getUTCSeconds()).padStart(2, '0') + ' UTC';
        };
    });

    // Tests de l'affichage de la date et de l'utilisateur
    test('should display correct date and time', () => {
        window.updateDateTime();
        expect(document.getElementById('current-time').textContent)
            .toBe('2025-05-12 07:49:10 UTC');
    });

    test('should display correct user', () => {
        expect(document.getElementById('current-user').textContent)
            .toBe('CabonM');
    });

    // Tests de la configuration du seuil d'eau
    test('should save valid water threshold', () => {
        document.getElementById('threshold').value = '100';
        window.saveThreshold();
        expect(localStorage.setItem).toHaveBeenCalledWith('waterThreshold', '100');
        expect(window.logToFile).toHaveBeenCalledWith('saveThreshold', { threshold: '100' });
    });

    test('should not save invalid water threshold', () => {
        document.getElementById('threshold').value = '-10';
        window.saveThreshold();
        expect(localStorage.setItem).not.toHaveBeenCalled();
    });

    // Tests de la configuration NMEA
    test('should save valid NMEA configuration', () => {
        document.getElementById('nmea-type').value = 'GPGGA';
        window.saveNmeaConfig();
        expect(localStorage.setItem).toHaveBeenCalledWith('nmeaType', 'GPGGA');
        expect(window.logToFile).toHaveBeenCalledWith('saveNmeaConfig', { nmeaType: 'GPGGA' });
    });

    test('should not save empty NMEA configuration', () => {
        document.getElementById('nmea-type').value = '';
        window.saveNmeaConfig();
        expect(localStorage.setItem).not.toHaveBeenCalled();
    });

    // Tests de la configuration WiFi
    test('should save valid WiFi configuration', () => {
        document.getElementById('ssid').value = 'TestNetwork';
        document.getElementById('password').value = 'TestPassword';
        document.getElementById('security').value = 'WPA';
        
        window.saveWifiConfig();
        
        expect(localStorage.setItem).toHaveBeenCalledWith('wifiConfig', JSON.stringify({
            ssid: 'TestNetwork',
            password: 'TestPassword',
            security: 'WPA'
        }));
        expect(window.logToFile).toHaveBeenCalledWith('saveWifiConfig', {
            ssid: 'TestNetwork',
            security: 'WPA',
            password: '********'
        });
    });

    test('should not save incomplete WiFi configuration', () => {
        document.getElementById('ssid').value = 'TestNetwork';
        document.getElementById('password').value = '';
        document.getElementById('security').value = 'WPA';
        
        window.saveWifiConfig();
        expect(localStorage.setItem).not.toHaveBeenCalled();
    });

    // Tests des icônes de statut
    test('should show success icon', () => {
        const statusIcon = document.getElementById('thresholdStatus');
        window.showStatusIcon(statusIcon, true);
        
        expect(statusIcon.style.display).toBe('inline');
        expect(statusIcon.src).toContain('check.svg');
        expect(statusIcon.alt).toBe('Succès');
    });

    test('should show error icon', () => {
        const statusIcon = document.getElementById('thresholdStatus');
        window.showStatusIcon(statusIcon, false);
        
        expect(statusIcon.style.display).toBe('inline');
        expect(statusIcon.src).toContain('error.svg');
        expect(statusIcon.alt).toBe('Erreur');
    });

    // Test du logging
    test('should log configuration changes', () => {
        document.getElementById('threshold').value = '100';
        window.saveThreshold();
        expect(window.logToFile).toHaveBeenCalledWith('saveThreshold', { threshold: '100' });
    });
});
