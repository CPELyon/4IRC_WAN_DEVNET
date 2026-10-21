"""TP-02, module 1 : valider les données d'intention avant de générer quoi que ce soit.

    python -m scripts.validate            # valide tous les sites de data/
    pytest tests/test_validate.py -v      # vérifie votre fonction check_site
"""
import glob
import ipaddress
import sys

from scripts.utils import load_yaml


def check_site(site):
    """Retourne la liste des erreurs trouvées dans un site (liste vide = site valide).

    Contrôles demandés :
    1. chaque VLAN a un id unique ;
    2. la passerelle de chaque VLAN appartient à son subnet ;
    3. chaque IP de routeur (routers[].ips) appartient au subnet du VLAN correspondant ;
    4. un site à deux routeurs doit avoir des priorités VRRP différentes.

    Indices : ipaddress.ip_network(), ipaddress.ip_interface(...).ip, l'opérateur `in`.
    Chaque erreur est une phrase lisible, par exemple "VLAN 10 : passerelle hors du réseau".
    """
    raise NotImplementedError("TP-02, module 1")


if __name__ == "__main__":
    ok = True
    for path in sorted(glob.glob("data/*.yaml")):
        if path.endswith("cores.yaml"):
            continue
        site = load_yaml(path)
        errors = check_site(site) if site is not None else ["fichier illisible (voir le message ci-dessus)"]
        status = "OK" if not errors else "ERREURS"
        print(f"{path} : {status}")
        for e in errors:
            print(f"  - {e}")
        ok = ok and not errors
    sys.exit(0 if ok else 1)
