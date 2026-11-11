"""TP-05, module 5 : déployer depuis NetBox.

NetBox donne maintenant l'INTENTION (quoi pousser) ET l'INVENTAIRE (où le pousser). L'inventaire est relu
dans NetBox à chaque lancement : plus de inventory/hosts.yaml à tenir à jour.

    python -m scripts.nornir_netbox                  # les équipements que Nornir trouve dans NetBox
    python -m scripts.nornir_netbox lyon --dry-run   # ce qui changerait sur Lyon (rien n'est appliqué)
    python -m scripts.nornir_netbox lyon             # déployer Lyon
"""
import sys

from nornir import InitNornir
from nornir.core.filter import F
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_netmiko.tasks import netmiko_save_config, netmiko_send_config
from nornir_utils.plugins.functions import print_result

from scripts.intent import get_site
from scripts.netbox_import import get_api
from scripts.render import render_site
from scripts.utils import get_credentials


# ------------------------------------------------------------------ fourni (lisez-le)
def init_nornir_netbox():
    """Initialise Nornir avec NetBox comme inventaire (inventory/config_netbox.yaml) et injecte les
    identifiants, comme init_nornir() au TP-04. Le jeton NetBox est lu dans la variable NB_TOKEN."""
    nr = InitNornir(config_file="inventory/config_netbox.yaml")
    nr.inventory.defaults.username, nr.inventory.defaults.password = get_credentials()
    # La plateforme vient de NetBox : « ios ». NAPALM l'utilise telle quelle, et nornir-netmiko la traduit
    # tout seul en « cisco_ios ». Au TP-04, c'était le rôle du groupe « ios » de groups.yaml.
    return nr


def show_inventory(nr):
    """Affiche ce que Nornir a trouvé dans NetBox : nom, IP de connexion, plateforme, site, rôle."""
    for name, host in sorted(nr.inventory.hosts.items()):
        print(f"{name:10} {host.hostname or '-':16} {host.platform or '-':5} "
              f"site={host['site']['slug']:6} rôle={host['role']['slug']}")


def deploy_config(task, configs, dry_run=True):
    """Tâche Nornir : pousse sur l'hôte sa configuration générée depuis NetBox (configs[nom de l'hôte]).
    - routeurs : NAPALM en mode fusion, comme au TP-03 : le diff est affiché ; si dry_run, rien n'est appliqué ;
    - switch : Netmiko, comme au TP-03 (pas de diff possible) ; si dry_run, on affiche seulement les commandes."""
    config = configs[task.host.name]
    if task.host["role"]["slug"] == "switch":
        if dry_run:
            return f"(dry-run, Netmiko : pas de diff) commandes qui seraient envoyées :\n{config}"
        task.run(task=netmiko_send_config, config_commands=config.splitlines())
        task.run(task=netmiko_save_config)
        return "configuration envoyée et sauvegardée"
    task.run(task=napalm_configure, configuration=config, replace=False, dry_run=dry_run)
    return "dry-run : rien n'a été appliqué" if dry_run else "configuration appliquée"


# ------------------------------------------------------------------ à compléter (module 5)
def site_devices(nr, code):
    """Retourne l'objet Nornir filtré sur les équipements du site `code` (lyon, mars, pars).

    Au TP-04, le site était une chaîne (groups.yaml). Ici, host["site"] est l'objet NetBox du site
    (un dict : {"id": …, "name": "CPE-LYON", "slug": "lyon", …}). Avec F, on descend dans un dict
    avec un double souligné : F(site__slug=…)."""
    raise NotImplementedError("TP-05, module 5")


def deploy_site(nr, code, dry_run=True):
    """Déploie le site `code` : génère ses configurations depuis NetBox (get_site + render_site),
    puis lance deploy_config sur les équipements du site. Retourne le résultat Nornir.

    Indices : render_site() renvoie {nom d'équipement: configuration} ;
              .run(task=deploy_config, configs=…, dry_run=…) transmet ces arguments à la tâche."""
    raise NotImplementedError("TP-05, module 5")


# ------------------------------------------------------------------ fourni
if __name__ == "__main__":
    nr = init_nornir_netbox()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        show_inventory(nr)
        sys.exit()
    result = deploy_site(nr, args[0], dry_run="--dry-run" in sys.argv)
    print_result(result)
    print("Équipements :", ", ".join(sorted(result)) or "aucun")
    print("Échecs :", ", ".join(sorted(result.failed_hosts)) or "aucun")
