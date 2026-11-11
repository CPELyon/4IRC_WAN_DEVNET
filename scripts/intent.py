"""TP-05, module 4 : l'INTENTION lue dans NetBox, avec le même format que docs/modele-donnees.md.

    python -m scripts.intent                  # les sites présents dans NetBox
    python -m scripts.intent lyon             # le site reconstruit depuis NetBox
    python -m scripts.intent lyon --compare   # identique à data/lyon.yaml ?

À partir d'ici, tous les scripts (génération, dérive, workflow) lisent l'intention ICI, plus dans data/.
Documentation de pynetbox : https://netbox-community.github.io/pynetbox/
"""
import sys

import yaml

from scripts.netbox_import import get_api
from scripts.utils import load_yaml


def list_sites(nb):
    """Retourne la liste des codes de site présents dans NetBox (lyon, mars, pars…), sans le cœur.
    Le code d'un site est son slug NetBox (voir netbox_import.py)."""
    raise NotImplementedError("TP-05, module 4")


# ------------------------------------------------------------------ fourni (lisez-le)
def _ips_of(nb, itf):
    """Adresses IP (au format '172.16.10.252/24') affectées à l'interface `itf`."""
    return [str(ip.address) for ip in nb.ipam.ip_addresses.filter(interface_id=itf.id)]


def _router(nb, dev, multiple):
    """Un élément de site["routers"], reconstruit depuis l'équipement NetBox `dev`."""
    itfs = list(nb.dcim.interfaces.filter(device_id=dev.id))
    subs = [i for i in itfs if i.parent and not i.mgmt_only]      # sous-interfaces des VLANs (pas la .99)
    router = {
        "hostname": dev.name,
        "platform": dev.platform.slug,
        "model": dev.device_type.model,
        "loopback": next(_ips_of(nb, i)[0] for i in itfs if i.name == "Loopback0"),
        "lan_interface": subs[0].parent.name,
    }
    if multiple:                                                    # la priorité VRRP est portée par le groupe FHRP
        prio = nb.ipam.fhrp_group_assignments.filter(interface_type="dcim.interface", interface_id=subs[0].id)
        router["vrrp_priority"] = next(iter(prio)).priority
    router["wan"] = []
    for i in itfs:
        if i.type.value == "other" and _ips_of(nb, i):
            peer = i.link_peers[0].device.name if i.link_peers else i.description.replace(" (WAN)", "")
            router["wan"].append({"interface": i.name, "ip": _ips_of(nb, i)[0], "peer": peer})
    router["ips"] = {i.untagged_vlan.vid: _ips_of(nb, i)[0] for i in subs}
    return router


def _switch(nb, dev):
    """Un élément de site["switches"], reconstruit depuis l'équipement NetBox `dev`."""
    itfs = list(nb.dcim.interfaces.filter(device_id=dev.id))
    return {
        "hostname": dev.name,
        "platform": dev.platform.slug,
        "model": dev.device_type.model,
        "trunks": [i.name for i in itfs if i.mode and i.mode.value == "tagged-all"],
        "access_ports": [{"interface": i.name, "vlan": i.untagged_vlan.vid}
                         for i in itfs if i.mode and i.mode.value == "access" and i.untagged_vlan],
    }


# ------------------------------------------------------------------ à compléter (module 4)
def _vlans(nb, site, routers):
    """La liste site["vlans"] : un dict par VLAN du site, trié par numéro, avec les clés
    id, name, description (seulement si le VLAN en a une), subnet et gateway.

    - subnet : le préfixe rattaché au VLAN ;
    - gateway : l'IP virtuelle VRRP du préfixe (rôle « vrrp »), sans le masque ; s'il n'y en a pas
      (site à un seul routeur), l'IP du routeur dans ce VLAN."""
    # Indices : nb.ipam.vlans.filter(site_id=…), nb.ipam.prefixes.get(vlan_id=…),
    #           nb.ipam.ip_addresses.get(role="vrrp", parent=<préfixe>) ;
    #           un objet NetBox n'est pas une chaîne : str(prefix.prefix), str(ip.address).
    raise NotImplementedError("TP-05, module 4")


def get_site(nb, code):
    """Reconstruit, à partir de NetBox, le dictionnaire du site `code` dans le format de docs/modele-donnees.md
    (site, code, switches, routers, vlans), exactement comme si on avait lu data/<code>.yaml.
    Retourne None si le site n'existe pas dans NetBox."""
    site = nb.dcim.sites.get(slug=code)
    if site is None:
        return None
    routers_nb = sorted(nb.dcim.devices.filter(site_id=site.id, role="site_router"), key=lambda d: d.name)
    switches_nb = sorted(nb.dcim.devices.filter(site_id=site.id, role="switch"), key=lambda d: d.name)
    routers = [_router(nb, d, len(routers_nb) > 1) for d in routers_nb]
    return {"site": site.name, "code": site.slug,
            "switches": [_switch(nb, d) for d in switches_nb],
            "routers": routers,
            "vlans": _vlans(nb, site, routers)}


if __name__ == "__main__":
    # python -m scripts.intent                  -> les sites présents dans NetBox (list_sites)
    # python -m scripts.intent lyon             -> le site relu dans NetBox, au format YAML
    # python -m scripts.intent lyon --compare   -> compare avec data/lyon.yaml
    nb = get_api()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(list_sites(nb))
        sys.exit()
    code = args[0]
    site = get_site(nb, code)
    if site is None:
        sys.exit(f"Site inconnu dans NetBox : {code}")
    if "--compare" not in sys.argv:
        print(yaml.safe_dump(site, sort_keys=False, allow_unicode=True))
        sys.exit()
    reference = load_yaml(f"data/{code}.yaml")
    if site == reference:
        print(f"OK : NetBox et data/{code}.yaml décrivent exactement le même site")
        sys.exit()
    print(f"DIFFÉRENT de data/{code}.yaml :")
    for key in reference:
        yml, nbx = reference[key], site.get(key)
        if yml == nbx:
            continue
        if isinstance(yml, list) and isinstance(nbx, list) and len(yml) == len(nbx):
            for i, (y, n) in enumerate(zip(yml, nbx)):        # n'affiche que les éléments qui diffèrent
                if y != n:
                    print(f"- {key}[{i}]\n    YAML   : {y}\n    NetBox : {n}")
        else:
            print(f"- {key}\n    YAML   : {yml}\n    NetBox : {nbx}")
    sys.exit(1)
