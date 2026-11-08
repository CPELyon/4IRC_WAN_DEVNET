"""TP-03, modules 1 et 2 : se connecter avec Netmiko, déployer Paris, sauvegarder (correction).

    python -m scripts.deploy_netmiko
"""
from netmiko import ConnectHandler

from scripts.utils import get_credentials, save_text


def connect(host):
    """Ouvre et retourne une connexion Netmiko vers `host` (IP d'administration).

    device_type : "cisco_ios". Identifiants : get_credentials().
    """
    username, password = get_credentials()
    return ConnectHandler(device_type="cisco_ios", host=host, username=username, password=password)


def show(conn, command):
    """Envoie une commande show et retourne la sortie texte."""
    return conn.send_command(command)


def deploy_file(conn, path):
    """Envoie les commandes du fichier `path` en mode configuration, sauvegarde (write memory)
    et retourne la sortie de Netmiko."""
    output = conn.send_config_from_file(path)
    output += conn.save_config()
    return output


def backup(conn, hostname, moment):
    """Récupère la running-config et l'écrit dans backups/<hostname>-<moment>.cfg
    (moment = "avant" ou "apres")."""
    save_text(f"backups/{hostname}-{moment}.cfg", show(conn, "show running-config"))


if __name__ == "__main__":
    PARS = {"R1-PARS": "172.16.100.254", "ESW-PARS": "172.16.100.253"}

    # ----- Module 1 : essais (décommenter pour tester, puis recommenter avant le module 2)
    # conn = connect(PARS["R1-PARS"])
    # print(show(conn, "show ip interface brief"))
    # print(type(conn))                  # classe Netmiko propre à cisco_ios (CiscoIosSSH)
    # print(conn.find_prompt())          # R1-PARS#
    # sortie = show(conn, "show running-config | section interface")
    # print(sortie)
    # print(type(sortie))                # <class 'str'> : du texte brut

    # ----- Module 2 : déployer Paris
    # Le switch d'abord (VLANs et trunk), puis le routeur (sous-interfaces)
    for hostname in ("ESW-PARS", "R1-PARS"):
        conn = connect(PARS[hostname])
        try:
            backup(conn, hostname, "avant")
            print(f"===== {hostname}")
            print(deploy_file(conn, f"config/{hostname}.cfg"))
            backup(conn, hostname, "apres")
        finally:
            conn.disconnect()
