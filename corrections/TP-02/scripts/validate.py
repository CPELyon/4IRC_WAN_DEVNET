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
    errors = []
    vlan_list = set()  # ensemble : ne peut pas contenir de doublons
    vlan_subnets = {}

    for vlan in site.get("vlans", []):
        vlan_id = vlan["id"]

        # 1. Chaque VLAN a un id unique
        if vlan_id in vlan_list:
            errors.append(f"VLAN {vlan_id} : identifiant dupliqué")
        vlan_list.add(vlan_id)

        # 2. La passerelle de chaque VLAN appartient à son subnet
        try:
            subnet = ipaddress.ip_network(vlan["subnet"], strict=False)
            vlan_subnets[vlan_id] = subnet
        except ValueError:
            errors.append(f"VLAN {vlan_id} : subnet invalide ({vlan['subnet']})")
            continue

        try:
            gw_ip = ipaddress.ip_interface(vlan["gateway"]).ip
            if gw_ip not in subnet:
                errors.append(f"VLAN {vlan_id} : passerelle hors du réseau")
        except ValueError:
            errors.append(f"VLAN {vlan_id} : passerelle invalide ({vlan['gateway']})")

    # 3. Chaque IP de routeur appartient au subnet du VLAN correspondant
    routers = site.get("routers", [])

    for router in routers:
        hostname = router["hostname"]
        for vlan_id, ip_str in router.get("ips", {}).items():
            try:
                ip_addr = ipaddress.ip_interface(ip_str).ip
            except ValueError:
                errors.append(f"Routeur {hostname} : IP invalide ({ip_str})")
                continue

            if vlan_id not in vlan_subnets:
                errors.append(f"Routeur {hostname} : VLAN {vlan_id} inexistant")
            elif ip_addr not in vlan_subnets[vlan_id]:
                errors.append(
                    f"Routeur {hostname} : IP {ip_addr} hors du réseau du VLAN {vlan_id}"
                )

    # 4. Un site à deux routeurs doit avoir des priorités VRRP différentes
    if len(routers) == 2:
        priorities = [router.get("vrrp_priority") for router in routers]
        if None in priorities:
            errors.append("VRRP : priorité manquante sur un des deux routeurs")
        elif priorities[0] == priorities[1]:
            errors.append("VRRP : les deux routeurs ont la même priorité")

    return errors


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
