import os
import subprocess
import requests
import zipfile
import shutil

# Variables
SHOUTCAST_DIR = r"C:\Shoutcast"
CONFIG_FILE = os.path.join(SHOUTCAST_DIR, "sc_serv.conf")
SERVICE_NAME = "ShoutcastServer"
IP_PUBLIC = requests.get('https://ifconfig.me').text.strip()

# Fonction pour afficher les messages
def log(message):
    print(f"\n[INFO] {message}")

# Vérifier si l'utilisateur est administrateur
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    print("Veuillez exécuter ce script en tant qu'administrateur.")
    exit(1)

# Télécharger Shoutcast Server
log("Téléchargement de Shoutcast Server...")
shoutcast_url = "https://download.nullsoft.com/shoutcast/tools/sc_serv2_win32.zip"
shoutcast_zip = os.path.join(os.environ["TEMP"], "shoutcast.zip")
response = requests.get(shoutcast_url, stream=True)
with open(shoutcast_zip, "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

# Extraire l'archive
log("Extraction de l'archive...")
with zipfile.ZipFile(shoutcast_zip, 'r') as zip_ref:
    zip_ref.extractall(os.environ["TEMP"])

# Créer le répertoire Shoutcast
log("Création du répertoire Shoutcast...")
os.makedirs(SHOUTCAST_DIR, exist_ok=True)

# Déplacer les fichiers Shoutcast
log("Déplacement des fichiers Shoutcast...")
shutil.move(os.path.join(os.environ["TEMP"], "sc_serv2.exe"), os.path.join(SHOUTCAST_DIR, "sc_serv.exe"))
shutil.move(os.path.join(os.environ["TEMP"], "sc_serv.conf"), CONFIG_FILE)

# Configurer Shoutcast
log("Configuration de Shoutcast...")
config_content = f"""
; Configuration de base pour Shoutcast Server

; Port de base
portbase=8000

; Mot de passe administrateur
adminpassword=admin

; Mot de passe pour les sources (streaming)
password=source

; Nom de la station
streamname=Ma Station Shoutcast

; Description de la station
streamdescription=Diffusion en direct sur le réseau local

; URL de la station
streamurl=http://{IP_PUBLIC}:8000

; Genre de la station
streamgenre=Variété

; Nombre maximum d'auditeurs
maxuser=10

; Encodage audio (par défaut : MP3)
encoder=mp3

; Bitrate (128 kbps par défaut)
bitrate=128
"""

with open(CONFIG_FILE, "w") as f:
    f.write(config_content)

# Configurer le service Windows
log("Configuration du service Windows...")
service_command = f'sc create {SERVICE_NAME} binPath= "{os.path.join(SHOUTCAST_DIR, "sc_serv.exe")} {CONFIG_FILE}" start= auto'
subprocess.run(service_command, shell=True)

# Démarrer le service
log("Démarrage du service Shoutcast...")
subprocess.run(f"sc start {SERVICE_NAME}", shell=True)

# Vérifier le statut du service
log("Vérification du statut du service...")
subprocess.run(f"sc query {SERVICE_NAME}", shell=True)

# Afficher les informations de connexion
log("Serveur Shoutcast installé et configuré !")
print(f"URL de diffusion : http://{IP_PUBLIC}:8000")
print("Mot de passe administrateur : admin")
print("Mot de passe source : source")

# Fin du script
log("Installation terminée !")
