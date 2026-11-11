"""TP-05, module 3 : importer l'intention des sites (data/*.yaml) dans NetBox avec pynetbox.

    set -a && source .env && set +a        # NB_TOKEN
    python -m scripts.netbox_import data/lyon.yaml data/mars.yaml data/pars.yaml

FOURNI, SAUF get_api() et get_or_create() : c'est à vous de les écrire (module 3).
Tout le reste fonctionne tel quel : lisez-le pour voir comment on parle à NetBox avec pynetbox.
Documentation de pynetbox : https://netbox-community.github.io/pynetbox/

Import IDEMPOTENT : chaque objet est cherché avant d'être créé, puis mis à jour s'il a changé.
On peut relancer le script autant de fois qu'on veut, sans doublon.

Pré-requis : python -m scripts.netbox_init (références, plan d'administration, cœur).

Ce qui est créé pour un fichier de site :
  - le site (slug = code du fichier : lyon, mars, pars) ;
  - les VLANs du site (avec leur description s'il y en a une) et leurs préfixes ;
  - les équipements, leurs interfaces (LAN, sous-interfaces, loopback, WAN, administration) et leurs IP ;
  - la redondance VRRP sous forme de groupes FHRP : l'IP virtuelle (rôle « vrrp ») et la priorité de chaque routeur ;
  - l'IP d'administration réservée par netbox_init, affectée et choisie comme IP principale (Nornir s'y connecte) ;
  - les câbles WAN (retrouvés par le /30 commun) et les câbles routeur ↔ switch.
"""
import ipaddress
import os
import sys

import pynetbox

from scripts.utils import load_yaml

NB_URL = os.environ.get("NB_URL", "http://localhost:8000")

ADMIN_VLAN = 99

# Clés de filtre de l'API -> nom du champ à la création (pynetbox filtre par device_id, crée avec device)
FILTER_TO_FIELD = {"site_id": "site", "device_id": "device", "manufacturer_id": "manufacturer"}


def get_api():
    """Retourne un client pynetbox authentifié (jeton dans la variable d'environnement NB_TOKEN)."""
    # Si NB_TOKEN est absent : arrêter avec un message clair (sys.exit), plutôt qu'une KeyError.
    # Astuce : nb.status() échoue tout de suite si l'URL ou le jeton sont faux.
    raise NotImplementedError("TP-05, module 3")


def get_or_create(endpoint, lookup, **fields):
    """Retourne l'objet trouvé avec endpoint.get(**lookup), ou le crée avec lookup + fields.
    C'est ce qui rend l'import IDEMPOTENT : on peut le relancer sans créer de doublons.
    Si l'objet existe déjà, ses champs sont mis à jour avec `fields` (le reste du script s'en sert,
    par exemple pour fixer l'IP principale d'un équipement déjà créé).

    Trois choses à savoir :
    - on CHERCHE avec un filtre (device_id=…) mais on CRÉE avec le nom du champ (device=…) :
      FILTER_TO_FIELD (plus haut) fait la traduction ;
    - obj.update(fields) renvoie True si quelque chose a changé ;
    - affichez ce que vous faites, par exemple « créé devices : R1-LYON » ou « mis à jour … »
      (endpoint.name donne le type d'objet) ; rien à afficher si l'objet est déjà à jour."""
    raise NotImplementedError("TP-05, module 3")


def slugify(text):
    return text.lower().replace(" ", "-").replace("/", "-")


# ------------------------------------------------------------------ objets communs
def get_device_type(nb, model):
    return nb.dcim.device_types.get(slug=slugify(model))      # créé par netbox_init


def get_platform(nb, platform):
    return nb.dcim.platforms.get(slug=platform)               # « ios », créée par netbox_init


def get_role(nb, slug):
    return nb.dcim.device_roles.get(slug=slug)                # core, site_router, switch


def admin_ip(nb, hostname, itf):
    """Affecte l'IP d'administration réservée par netbox_init (dns_name = hostname en minuscules) à l'interface `itf`."""
    ip = nb.ipam.ip_addresses.get(dns_name=hostname.lower())   # NetBox range le dns_name en minuscules
    if ip is None:
        sys.exit(f"Pas d'IP d'administration réservée pour {hostname} : lancez d'abord scripts.netbox_init")
    if ip.update({"status": "active", "assigned_object_type": "dcim.interface", "assigned_object_id": itf.id}):
        print(f"  affectée   IP d'administration {ip} -> {hostname}")
    return ip


def interface(nb, device, name, itype, **fields):
    return get_or_create(nb.dcim.interfaces, {"device_id": device.id, "name": name}, type=itype, **fields)


def ip_on(nb, address, itf, **fields):
    return get_or_create(nb.ipam.ip_addresses, {"address": address},
                         assigned_object_type="dcim.interface", assigned_object_id=itf.id,
                         status="active", **fields)


# ------------------------------------------------------------------ import d'un site
def import_vlans(nb, site, nb_site):
    vlans = {}
    for v in site["vlans"]:
        vlan = get_or_create(nb.ipam.vlans, {"site_id": nb_site.id, "vid": v["id"]},
                             name=v["name"], description=v.get("description", ""), status="active")
        get_or_create(nb.ipam.prefixes, {"prefix": v["subnet"]},
                      scope_type="dcim.site", scope_id=nb_site.id, vlan=vlan.id, status="active",
                      description=f"{site['site']} VLAN {v['id']} {v['name']}")
        vlans[v["id"]] = vlan
    return vlans


def lan_name(router, vid):
    return f"{router['lan_interface']}.{vid}"


def import_router(nb, site, nb_site, router, role, vlans):
    dev = get_or_create(nb.dcim.devices, {"name": router["hostname"]},
                        site=nb_site.id, role=role.id, status="active",
                        device_type=get_device_type(nb, router["model"]).id,
                        platform=get_platform(nb, router["platform"]).id)

    lan = interface(nb, dev, router["lan_interface"], "1000base-x-gbic")
    lan_itfs = {}
    for vid, cidr in router["ips"].items():
        itf = interface(nb, dev, lan_name(router, vid), "virtual", parent=lan.id,
                        mode="access", untagged_vlan=vlans[vid].id)
        ip_on(nb, cidr, itf)
        lan_itfs[vid] = itf

    lo = interface(nb, dev, "Loopback0", "virtual", description="Router-ID")
    ip_on(nb, router["loopback"], lo, role="loopback")

    for link in router.get("wan", []):
        itf = interface(nb, dev, link["interface"], "other", description=f"{link['peer']} (WAN)")
        ip_on(nb, link["ip"], itf)

    # IP principale = IP d'administration (sous-interface .99), réservée par netbox_init
    adm = interface(nb, dev, f"{router['lan_interface']}.{ADMIN_VLAN}", "virtual", parent=lan.id,
                    mgmt_only=True, description="Administration (VLAN 99, hors OSPF)")
    primary = admin_ip(nb, router["hostname"], adm)
    get_or_create(nb.dcim.devices, {"id": dev.id}, primary_ip4=primary.id)
    return dev, lan, lan_itfs


def import_switch(nb, site, nb_site, switch, role, vlans):
    dev = get_or_create(nb.dcim.devices, {"name": switch["hostname"]},
                        site=nb_site.id, role=role.id, status="active",
                        device_type=get_device_type(nb, switch["model"]).id,
                        platform=get_platform(nb, switch["platform"]).id)
    for port in switch["access_ports"]:
        interface(nb, dev, port["interface"], "100base-tx", mode="access", untagged_vlan=vlans[port["vlan"]].id)
    trunks = [interface(nb, dev, t, "100base-tx", mode="tagged-all") for t in switch["trunks"]]
    adm = interface(nb, dev, f"Vlan{ADMIN_VLAN}", "virtual", mgmt_only=True, description="Administration")
    primary = admin_ip(nb, switch["hostname"], adm)
    get_or_create(nb.dcim.devices, {"id": dev.id}, primary_ip4=primary.id)
    return dev, trunks


def import_vrrp(nb, site, routers):
    """Un groupe FHRP (VRRP) par VLAN quand le site a deux routeurs : IP virtuelle + priorité de chacun."""
    if len(routers) < 2:
        return
    for v in site["vlans"]:
        prefixlen = ipaddress.ip_network(v["subnet"]).prefixlen
        group = get_or_create(nb.ipam.fhrp_groups, {"protocol": "vrrp2", "group_id": v["id"],
                                                   "name": f"{site['site']} VLAN {v['id']}"})
        get_or_create(nb.ipam.ip_addresses, {"address": f"{v['gateway']}/{prefixlen}"},
                      role="vrrp", status="active",
                      assigned_object_type="ipam.fhrpgroup", assigned_object_id=group.id)
        for router, lan_itfs in routers:
            itf = lan_itfs[v["id"]]
            assignment = nb.ipam.fhrp_group_assignments.get(group_id=group.id, interface_type="dcim.interface",
                                                            interface_id=itf.id)
            if assignment is None:
                nb.ipam.fhrp_group_assignments.create(group=group.id, interface_type="dcim.interface",
                                                      interface_id=itf.id, priority=router["vrrp_priority"])
                print(f"  créé       priorité VRRP de {router['hostname']} dans {group}")
            elif assignment.update({"priority": router["vrrp_priority"]}):
                print(f"  mis à jour priorité VRRP de {router['hostname']} dans {group}")


def cable(nb, a, b):
    """Câble deux interfaces si aucune des deux n'est déjà câblée."""
    a, b = nb.dcim.interfaces.get(a.id), nb.dcim.interfaces.get(b.id)
    if a.cable or b.cable:
        return
    nb.dcim.cables.create(a_terminations=[{"object_type": "dcim.interface", "object_id": a.id}],
                          b_terminations=[{"object_type": "dcim.interface", "object_id": b.id}],
                          status="connected")
    print(f"  créé       câble {a.device.name} {a.name} <-> {b.device.name} {b.name}")


def import_wan_cables(nb, router):
    """Relie chaque lien WAN à l'interface du voisin qui porte une IP du même /30 (s'il est déjà importé)."""
    dev = nb.dcim.devices.get(name=router["hostname"])
    for link in router.get("wan", []):
        net = ipaddress.ip_interface(link["ip"]).network
        peer = nb.dcim.devices.get(name=link["peer"])
        if peer is None:
            continue                        # le voisin sera câblé quand son fichier sera importé
        mine = nb.dcim.interfaces.get(device_id=dev.id, name=link["interface"])
        for ip in nb.ipam.ip_addresses.filter(device_id=peer.id, parent=str(net)):
            if ip.assigned_object_type == "dcim.interface":
                cable(nb, mine, nb.dcim.interfaces.get(ip.assigned_object_id))


# ------------------------------------------------------------------ contrôle avant import (fourni)
def check_before_import(nb, site):
    """Vérifie un fichier de site AVANT de toucher à NetBox. Retourne la liste des problèmes (vide si tout va bien).
    But : s'arrêter avec un message clair, plutôt qu'au milieu de l'import avec un NetBox à moitié rempli."""
    problems = [f"clé « {key} » absente" for key in ("site", "code", "routers", "switches", "vlans") if key not in site]
    if problems:
        return problems

    for v in site["vlans"]:
        try:
            if ipaddress.ip_address(v["gateway"]) not in ipaddress.ip_network(v["subnet"]):
                problems.append(f"VLAN {v['id']} : la passerelle {v['gateway']} n'est pas dans {v['subnet']}")
        except KeyError as e:
            problems.append(f"VLAN {v.get('id', '?')} : clé {e} absente")
        except ValueError as e:
            problems.append(f"VLAN {v.get('id', '?')} : adresse invalide ({e})")

    for device in site["routers"] + site["switches"]:
        name = device.get("hostname", "?")
        if nb.ipam.ip_addresses.get(dns_name=name.lower()) is None:
            problems.append(f"{name} : aucune IP d'administration réservée à ce nom (noms attendus : R1-LYON, ESW-MARS…)")
        if not device.get("model") or get_device_type(nb, device["model"]) is None:
            problems.append(f"{name} : modèle « {device.get('model')} » inconnu dans NetBox (c7200 ou c3725)")
        if not device.get("platform") or get_platform(nb, device["platform"]) is None:
            problems.append(f"{name} : plateforme « {device.get('platform')} » inconnue dans NetBox (ios)")

    for router in site["routers"]:
        name = router.get("hostname", "?")
        keys = ["loopback", "lan_interface", "ips"] + (["vrrp_priority"] if len(site["routers"]) > 1 else [])
        problems += [f"{name} : clé « {key} » absente" for key in keys if key not in router]
        for vid, cidr in router.get("ips", {}).items():
            if not isinstance(vid, int):
                problems.append(f"{name} : dans ips, la clé « {vid} » doit être un numéro de VLAN (sans guillemets)")
            try:
                ipaddress.ip_interface(cidr)
            except ValueError:
                problems.append(f"{name} : adresse invalide dans ips : {cidr}")
    for switch in site["switches"]:
        problems += [f"{switch.get('hostname', '?')} : clé « {key} » absente"
                     for key in ("trunks", "access_ports") if key not in switch]
    return problems


def import_site(nb, site):
    """Crée dans NetBox : le site, ses VLANs, leurs préfixes, les équipements (routeurs, switch),
    leurs interfaces et leurs adresses IP (rôle "vrrp" pour les VIP).
    Affiche chaque objet créé ou mis à jour : si rien ne s'affiche, NetBox était déjà à jour."""
    print(f"== {site['site']} ==")
    nb_site = get_or_create(nb.dcim.sites, {"slug": site["code"]}, name=site["site"], status="active")
    vlans = import_vlans(nb, site, nb_site)

    router_role = get_role(nb, "site_router")
    switch_role = get_role(nb, "switch")

    routers = []
    for r in site["routers"]:
        dev, lan, lan_itfs = import_router(nb, site, nb_site, r, router_role, vlans)
        routers.append((r, lan_itfs, lan))
    switches = [import_switch(nb, site, nb_site, s, switch_role, vlans) for s in site["switches"]]

    import_vrrp(nb, site, [(r, itfs) for r, itfs, _ in routers])

    # Câbles routeur ↔ switch : trunks[i] du premier switch vers le routeur i (voir docs/maquette.md)
    if switches and switches[0][1]:
        for (_, _, lan), trunk in zip(routers, switches[0][1]):
            cable(nb, lan, trunk)
    for r in site["routers"]:
        import_wan_cables(nb, r)


if __name__ == "__main__":
    paths = sys.argv[1:] or ["data/lyon.yaml"]
    nb = get_api()
    sites = []
    for path in paths:                                   # 1. on vérifie TOUS les fichiers avant d'importer quoi que ce soit
        site = load_yaml(path)
        if site is None:
            sys.exit(1)
        problems = check_before_import(nb, site)
        if problems:
            print(f"{path} : à corriger avant l'import (rien n'a été envoyé à NetBox)")
            for problem in problems:
                print(f"  - {problem}")
            sys.exit(1)
        sites.append(site)
    for site in sites:                                   # 2. puis on importe
        import_site(nb, site)
