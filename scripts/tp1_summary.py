"""TP-01, module 3 : afficher un résumé d'un site décrit en YAML.

    python -m scripts.tp1_summary data/lyon.yaml

Résultat attendu (exemple) :
    Site CPE-LYON : 3 équipements, 2 VLANs, VRRP : oui
      - VLAN 10 teacher : 172.16.10.0/24, passerelle 172.16.10.254
      - VLAN 20 student : 172.16.20.0/24, passerelle 172.16.20.254
      - R1-LYON : priorité VRRP 110
      - R2-LYON : priorité VRRP 100
"""
import sys

from scripts.utils import load_yaml


def summarize(site):
    """Retourne le résumé du site sous forme de liste de lignes (str).

    Indices : len(), une boucle for sur site["vlans"] et site["routers"], une f-string par ligne.
    Un site a du VRRP s'il a plus d'un routeur.
    """
    raise NotImplementedError("TP-01, module 3")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/lyon.yaml"
    site = load_yaml(path)
    if site is not None:
        print("\n".join(summarize(site)))
