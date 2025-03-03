import time

# Seuil de profondeur critique en mètres
SEUIL_PROFONDEUR_CRITIQUE = 2.0

def lire_hauteur_eau():
    """
    Fonction simulant la lecture de la hauteur d'eau.
    Retourne une valeur de hauteur d'eau en mètres.
    """
    # Dans une application réelle, cette fonction lirait les données d'un capteur.
    # Ici, nous simulons les données en retournant une valeur fixe pour simplifier.
    return 1.5

def alerter_skipper(profondeur):
    """
    Fonction pour alerter le skipper.
    """
    print(f"ALERTE: La profondeur de l'eau est critique ({profondeur} mètres) !")

def suivre_hauteur_eau():
    """
    Fonction principale pour suivre l'évolution de la hauteur d'eau.
    """
    while True:
        profondeur = lire_hauteur_eau()
        print(f"Hauteur d'eau actuelle: {profondeur} mètres")
        
        if profondeur < SEUIL_PROFONDEUR_CRITIQUE:
            alerter_skipper(profondeur)
        
        # Attendre 1 seconde avant la prochaine lecture
        time.sleep(1)

if __name__ == "__main__":
    suivre_hauteur_eau()