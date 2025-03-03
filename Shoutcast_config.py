import os
import subprocess
import requests

# Variables
SHOUTCAST_DIR = "/usr/local/shoutcast"
CONFIG_FILE = os.path.join(SHOUTCAST_DIR, "sc_serv.conf")
SERVICE_FILE = "/etc/systemd/system/shoutcast.service"
IP_PUBLIC = requests.get('https://ifconfig.me').text.strip()

# Fonction pour afficher les messages
def log(message):
    print(f"\n[INFO] {message}")

# Vérifier si l'utilisateur est root
if os.geteuid() != 0:
    print("Veuillez exécuter ce script en tant que root.")
    exit(1)

# Mettre à jour le système
log("Mise à jour du système...")
subprocess.run(["apt-get", "update", "-y"])
subprocess.run(["apt-get", "upgrade", "-y"])

# Installer les dépendances
log("Installation des dépendances...")
subprocess.run(["apt-get", "install", "-y", "wget", "unzip", "libc6", "libstdc++6"])

# Télécharger Shoutcast Server
log("Téléchargement de Shoutcast Server...")
subprocess.run(["wget", "https://download.nullsoft.com/shoutcast/tools/sc_serv2_linux_x64-latest.tar.gz", "-O", "/tmp/shoutcast.tar.gz"])

# Extraire l'archive
log("Extraction de l'archive...")
subprocess.run(["tar", "-xvzf", "/tmp/shoutcast.tar.gz", "-C", "/tmp/"])

# Créer le répertoire Shoutcast
log("Création du répertoire Shoutcast...")
os.makedirs(SHOUTCAST_DIR, exist_ok=True)
subprocess.run(["mv", "/tmp/sc_serv2", os.path.join(SHOUTCAST_DIR, "sc_serv")])
subprocess.run(["mv", "/tmp/sc_serv.conf", CONFIG_FILE])

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

# Donner les permissions d'exécution
log("Définition des permissions...")
os.chmod(os.path.join(SHOUTCAST_DIR, "sc_serv"), 0o755)
os.chmod(CONFIG_FILE, 0o644)

# Configurer le service systemd
log("Configuration du service systemd...")
service_content = f"""
[Unit]
Description=Shoutcast Server
After=network.target

[Service]
ExecStart={os.path.join(SHOUTCAST_DIR, 'sc_serv')} {CONFIG_FILE}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""

with open(SERVICE_FILE, "w") as f:
    f.write(service_content)

# Recharger systemd et démarrer le service
log("Démarrage du service Shoutcast...")
subprocess.run(["systemctl", "daemon-reload"])
subprocess.run(["systemctl", "enable", "shoutcast"])
subprocess.run(["systemctl", "start", "shoutcast"])

# Vérifier le statut du service
log("Vérification du statut du service...")
subprocess.run(["systemctl", "status", "shoutcast"])

# Afficher les informations de connexion
log("Serveur Shoutcast installé et configuré !")
print(f"URL de diffusion : http://{IP_PUBLIC}:8000")
print("Mot de passe administrateur : admin")
print("Mot de passe source : source")

# Fin du script
log("Installation terminée !")
