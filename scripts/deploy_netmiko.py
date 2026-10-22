"""TP-03, modules 1 et 2 : se connecter avec Netmiko, déployer Paris, sauvegarder.

    python -m scripts.deploy_netmiko
"""
from netmiko import ConnectHandler

from scripts.utils import get_credentials, save_text


def connect(host):
    """Ouvre et retourne une connexion Netmiko vers `host` (IP d'administration).

    device_type : "cisco_ios". Identifiants : get_credentials().
    """
    raise NotImplementedError("TP-03, module 1")


def show(conn, command):
    """Envoie une commande show et retourne la sortie texte."""
    raise NotImplementedError("TP-03, module 1")


def deploy_file(conn, path):
    """Envoie les commandes du fichier `path` en mode configuration, sauvegarde (write memory)
    et retourne la sortie de Netmiko."""
    raise NotImplementedError("TP-03, module 2")


def backup(conn, hostname, moment):
    """Récupère la running-config et l'écrit dans backups/<hostname>-<moment>.cfg
    (moment = "avant" ou "apres")."""
    raise NotImplementedError("TP-03, module 2")


if __name__ == "__main__":
    PARS = {"R1-PARS": "172.16.100.254", "ESW-PARS": "172.16.100.253"}
    # À compléter : pour chaque équipement de Paris, se connecter, déployer config/<hostname>.cfg,
    # puis faire une sauvegarde.
