import time
import Adafruit_ADS1x15
import requests
import pandas as pd

# Créez une instance du convertisseur ADS1115 pour le premier capteur.
adc1 = Adafruit_ADS1x15.ADS1115()

# Spécifiez le canal que vous avez connecté le premier capteur MQ-2.
channel1 = 0  # Utilisez A0 si vous avez connecté le capteur sur le canal 0.

# Coefficients de calibration pour chaque gaz polluant.
calibration_coefficients = {
    "LPG": 1.2,
    "Smoke": 0.8,
    "Alcohol": 1.5,
    "Propane": 0.9,
    "Hydrogen": 1.1,
    "Methane": 0.7,
    "Carbon Monoxide": 1.3
}

# Configuration ThingSpeak pour la première chaîne.
api_key1 = "SM5ZOPCSSVHPOG6M"
api_url1 = f"https://api.thingspeak.com/update?api_key={api_key1}"

# Configuration ThingSpeak pour la deuxième chaîne.
channel_id2 = "ID_DE_LA_DEUXIEME_CHAINE"
api_key2 = "CLE_API_DE_LA_DEUXIEME_CHAINE"
api_url2 = f"https://api.thingspeak.com/update?api_key={api_key2}"

# Création du DataFrame pour stocker les valeurs en direct
df = pd.DataFrame(columns=["Temps", "Capteur 1 - LPG", "Capteur 1 - Smoke", "Capteur 1 - Alcohol",
                           "Capteur 1 - Propane", "Capteur 1 - Hydrogen", "Capteur 1 - Methane",
                           "Capteur 1 - Carbon Monoxide", "Capteur 2 - LPG", "Capteur 2 - Smoke",
                           "Capteur 2 - Alcohol", "Capteur 2 - Propane", "Capteur 2 - Hydrogen",
                           "Capteur 2 - Methane", "Capteur 2 - Carbon Monoxide"])

# Boucle infinie pour lire les valeurs des capteurs et envoyer les concentrations à ThingSpeak.
while True:
    concentrations = {}

    # Lire les valeurs du premier capteur.
    for gas, calibration_coefficient in calibration_coefficients.items():
        value1 = adc1.read_adc(channel1, gain=1)
        concentration1 = value1 * calibration_coefficient
        concentrations[gas + " Capteur 1"] = concentration1

    # Lire les valeurs du deuxième capteur.
    # Créez une deuxième instance du convertisseur ADS1115 pour le deuxième capteur.
    adc2 = Adafruit_ADS1x15.ADS1115()
    # Spécifiez le canal que vous avez connecté le deuxième capteur MQ-2.
    channel2 = 1  # Utilisez A1 si vous avez connecté le capteur sur le canal 1.
    for gas, calibration_coefficient in calibration_coefficients.items():
        value2 = adc2.read_adc(channel2, gain=1)
        concentration2 = value2 * calibration_coefficient
        concentrations[gas + " Capteur 2"] = concentration2

    # Envoie des concentrations à ThingSpeak (Chaîne 1).
    params1 = {
        "field1": concentrations["LPG Capteur 1"],
        "field2": concentrations["Smoke Capteur 1"],
        "field3": concentrations["Alcohol Capteur 1"],
        "field4": concentrations["Propane Capteur 1"],
        "field5": concentrations["Hydrogen Capteur 1"],
        "field6": concentrations["Methane Capteur 1"],
        "field7": concentrations["Carbon Monoxide Capteur 1"]
    }
    response1 = requests.get(api_url1, params=params1)

    # Ajout des valeurs au DataFrame
    df.loc[len(df)] = [time.strftime("%Y-%m-%d %H:%M:%S")] + list(concentrations.values())

    # Envoie des concentrations à ThingSpeak (Chaîne 2).
    params2 = {
        "field1": concentrations["LPG Capteur 2"],
        "field2": concentrations["Smoke Capteur 2"],
        "field3": concentrations["Alcohol Capteur 2"],
        "field4": concentrations["Propane Capteur 2"],
        "field5": concentrations["Hydrogen Capteur 2"],
        "field6": concentrations["Methane Capteur 2"],
        "field7": concentrations["Carbon Monoxide Capteur 2"]
    }
    response2 = requests.get(api_url2, params=params2)

    print("Concentrations envoyées à ThingSpeak (Chaîne 1) :", concentrations)

    # Pause d'une seconde entre les mesures.
    time.sleep(1)

# Calcul de la marge d'erreur entre les deux capteurs.
error_margin = df.iloc[-1][1:8] - df.iloc[-1][8:]

# Calcul du pourcentage de purification.
purification_percentage = (1 - (df.iloc[-1][8:].sum() / df.iloc[-1][1:8].sum())) * 100

# Affichage de la marge d'erreur et du pourcentage de purification.
print("Marge d'erreur entre les deux capteurs :", error_margin)
print("Pourcentage de purification :", purification_percentage)

# Enregistrement du DataFrame dans un fichier Excel.
df.to_excel("valeurs_capteurs.xlsx", index=False)
