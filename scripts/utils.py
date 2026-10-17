"""Fonctions utilitaires partagées par tous les scripts du projet.

TP-01 : load_yaml
TP-02 : save_text, get_jinja_env (fourni)
TP-03 : get_credentials (fourni)
"""
import ipaddress
import os

from jinja2 import Environment, FileSystemLoader


def load_yaml(path):
    """Charge un fichier YAML et retourne son contenu (dict ou list).

    - Si le fichier n'existe pas : afficher un message clair et retourner None.
    - Si le YAML est invalide : afficher le message d'erreur et retourner None.

    >>> data = load_yaml("data/cores.yaml")
    >>> data["devices"][0]["hostname"]
    'CORE-1'
    """
    raise NotImplementedError("TP-01, module 4")


def save_text(path, content):
    """Écrit `content` dans le fichier `path` (crée le dossier parent s'il n'existe pas)."""
    raise NotImplementedError("TP-02, module 3")


# ------------------------------------------------------------------ fourni
def ip_addr(cidr):
    """'172.16.10.252/24' -> '172.16.10.252'"""
    return str(ipaddress.ip_interface(cidr).ip)


def netmask(cidr):
    """'172.16.10.252/24' -> '255.255.255.0'"""
    return str(ipaddress.ip_interface(cidr).netmask)


def wildcard(cidr):
    """'172.16.10.0/24' -> '0.0.0.255' (utile pour OSPF)"""
    return str(ipaddress.ip_interface(cidr).network.hostmask)


def network(cidr):
    """'172.16.10.252/24' -> '172.16.10.0'"""
    return str(ipaddress.ip_interface(cidr).network.network_address)


def get_jinja_env(folder="templates"):
    """Environnement Jinja2 du projet, avec les filtres ip_addr, netmask, wildcard et network."""
    env = Environment(loader=FileSystemLoader(folder), trim_blocks=True, lstrip_blocks=True)
    env.filters.update(ip_addr=ip_addr, netmask=netmask, wildcard=wildcard, network=network)
    return env


def get_credentials():
    """Identifiants des équipements, lus dans les variables d'environnement NET_USER et NET_PASSWORD."""
    return os.environ.get("NET_USER", "cisco"), os.environ.get("NET_PASSWORD", "cisco")
