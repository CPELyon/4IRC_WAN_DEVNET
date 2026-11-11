"""FOURNI (fonctionne tel quel) : prépare NetBox avec tout ce que vous n'avez PAS à faire vous-même.

    set -a && source .env && set +a        # NB_TOKEN
    python -m scripts.netbox_init

Ce script crée, une seule fois (on peut le relancer sans doublon) :
  1. les références communes : constructeur Cisco, modèles c7200 et c3725, plateforme « ios »,
     rôles core / site_router / switch ;
  2. le plan d'administration hors bande (docs/maquette.md) : VLAN 99, préfixes /26 et une adresse
     RÉSERVÉE par équipement de site (champ dns_name = nom de l'équipement, en minuscules). Votre import l'affectera ;
  3. le cœur et le NOC (data/cores.yaml) : site CPE-CORE, CORE-1, CORE-2, ESW-NOC, interfaces, IP,
     VRRP du NOC (groupe FHRP) et câbles.

Lisez-le : c'est l'exemple à suivre pour importer VOS sites (scripts/netbox_import.py).
"""
import ipaddress
import os
import sys

import pynetbox

from scripts.utils import load_yaml

NB_URL = os.environ.get("NB_URL", "http://localhost:8000")

ROLES = {"core": ("Core", "ff5722"), "site_router": ("Site router", "2196f3"), "switch": ("Switch", "4caf50")}

ADMIN_PREFIXES = {"172.16.100.64/26": "Lyon", "172.16.100.128/26": "Marseille", "172.16.100.192/26": "Paris"}
ADMIN_IPS = {
    "R1-LYON": "172.16.100.126/26", "R2-LYON": "172.16.100.125/26", "ESW-LYON": "172.16.100.124/26",
    "R1-MARS": "172.16.100.190/26", "R2-MARS": "172.16.100.189/26", "ESW-MARS": "172.16.100.188/26",
    "R1-PARS": "172.16.100.254/26", "ESW-PARS": "172.16.100.253/26",
}


def find_or_create(endpoint, lookup, create):
    """Cherche avec les filtres `lookup`, sinon crée avec les champs `create`."""
    obj = endpoint.get(**lookup)
    return obj if obj is not None else endpoint.create(**create)


def references(nb):
    cisco = find_or_create(nb.dcim.manufacturers, {"slug": "cisco"}, {"name": "Cisco", "slug": "cisco"})
    for model in ("c7200", "c3725"):
        find_or_create(nb.dcim.device_types, {"slug": model},
                       {"model": model, "slug": model, "manufacturer": cisco.id})
    find_or_create(nb.dcim.platforms, {"slug": "ios"}, {"name": "ios", "slug": "ios"})
    for slug, (name, color) in ROLES.items():
        find_or_create(nb.dcim.device_roles, {"slug": slug}, {"name": name, "slug": slug, "color": color})


def admin_plan(nb):
    find_or_create(nb.ipam.vlans, {"vid": 99, "name": "admin"}, {"vid": 99, "name": "admin", "status": "active"})
    for prefix, zone in ADMIN_PREFIXES.items():
        find_or_create(nb.ipam.prefixes, {"prefix": prefix},
                       {"prefix": prefix, "status": "active", "description": f"Administration {zone} (VLAN 99)"})
    for host, address in ADMIN_IPS.items():
        find_or_create(nb.ipam.ip_addresses, {"address": address},
                       {"address": address, "status": "reserved", "dns_name": host,
                        "description": f"Administration {host} (à affecter à l'import du site)"})


def device(nb, site, item, role):
    return find_or_create(nb.dcim.devices, {"name": item["hostname"]}, {
        "name": item["hostname"], "site": site.id, "status": "active",
        "role": nb.dcim.device_roles.get(slug=role).id,
        "device_type": nb.dcim.device_types.get(slug=item["model"]).id,
        "platform": nb.dcim.platforms.get(slug=item["platform"]).id})


def interface(nb, dev, name, itype, **fields):
    return find_or_create(nb.dcim.interfaces, {"device_id": dev.id, "name": name},
                          {"device": dev.id, "name": name, "type": itype, **fields})


def address(nb, cidr, itf, **fields):
    return find_or_create(nb.ipam.ip_addresses, {"address": cidr}, {
        "address": cidr, "status": "active",
        "assigned_object_type": "dcim.interface", "assigned_object_id": itf.id, **fields})


def cable(nb, a, b):
    if nb.dcim.interfaces.get(a.id).cable or nb.dcim.interfaces.get(b.id).cable:
        return
    nb.dcim.cables.create(a_terminations=[{"object_type": "dcim.interface", "object_id": a.id}],
                          b_terminations=[{"object_type": "dcim.interface", "object_id": b.id}],
                          status="connected")


def core(nb, data):
    site = find_or_create(nb.dcim.sites, {"slug": data["code"]},
                          {"name": data["site"], "slug": data["code"], "status": "active"})
    noc = data["vlans"][0]                                    # VLAN 1, natif sur l'interface LAN du cœur
    vlan = find_or_create(nb.ipam.vlans, {"site_id": site.id, "vid": noc["id"]},
                          {"site": site.id, "vid": noc["id"], "name": noc["name"], "status": "active"})
    find_or_create(nb.ipam.prefixes, {"prefix": noc["subnet"]},
                   {"prefix": noc["subnet"], "scope_type": "dcim.site", "scope_id": site.id,
                    "vlan": vlan.id, "status": "active", "description": "NOC"})

    switch = data["switches"][0]
    esw = device(nb, site, switch, "switch")
    ports = {p["interface"]: interface(nb, esw, p["interface"], "100base-tx", mode="access",
                                       untagged_vlan=vlan.id) for p in switch["access_ports"]}

    prefixlen = ipaddress.ip_network(noc["subnet"]).prefixlen
    group = find_or_create(nb.ipam.fhrp_groups, {"protocol": "vrrp2", "group_id": noc["id"]},
                           {"protocol": "vrrp2", "group_id": noc["id"], "name": f"{data['site']} VLAN {noc['id']}"})
    find_or_create(nb.ipam.ip_addresses, {"address": f"{noc['gateway']}/{prefixlen}"},
                   {"address": f"{noc['gateway']}/{prefixlen}", "status": "active", "role": "vrrp",
                    "assigned_object_type": "ipam.fhrpgroup", "assigned_object_id": group.id})

    for i, r in enumerate(data["routers"]):
        dev = device(nb, site, r, "core")
        lan = interface(nb, dev, r["lan_interface"], "1000base-x-gbic", mode="access", untagged_vlan=vlan.id)
        ip = address(nb, r["ips"][noc["id"]], lan)
        lo = interface(nb, dev, "Loopback0", "virtual", description="Router-ID")
        address(nb, r["loopback"], lo, role="loopback")
        for link in r["wan"]:
            itf = interface(nb, dev, link["interface"], "other", description=f"{link['peer']} (WAN)")
            address(nb, link["ip"], itf)
        if not nb.ipam.fhrp_group_assignments.get(group_id=group.id, interface_type="dcim.interface",
                                                  interface_id=lan.id):
            nb.ipam.fhrp_group_assignments.create(group=group.id, interface_type="dcim.interface",
                                                  interface_id=lan.id, priority=r["vrrp_priority"])
        nb.dcim.devices.get(dev.id).update({"primary_ip4": ip.id})
        cable(nb, lan, list(ports.values())[i])          # CORE-1 -> f1/0, CORE-2 -> f1/1 (docs/maquette.md)

    # Lien CORE-1 <-> CORE-2 (les liens vers les sites seront câblés par votre import)
    c1, c2 = (nb.dcim.devices.get(name=r["hostname"]) for r in data["routers"])
    cable(nb, nb.dcim.interfaces.get(device_id=c1.id, name="Serial1/3"),
          nb.dcim.interfaces.get(device_id=c2.id, name="Serial1/3"))


if __name__ == "__main__":
    token = os.environ.get("NB_TOKEN")
    if not token:
        sys.exit("NB_TOKEN n'est pas défini : set -a && source .env && set +a")
    nb = pynetbox.api(NB_URL, token=token)
    references(nb)
    admin_plan(nb)
    core(nb, load_yaml("data/cores.yaml"))
    print("NetBox prêt : références, plan d'administration, cœur et NOC.")
