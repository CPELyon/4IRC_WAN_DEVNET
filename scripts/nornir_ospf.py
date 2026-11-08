"""TP-04, modules 1 et 2 : l'inventaire Nornir, puis OSPF sur tous les routeurs de site.

    python -m scripts.nornir_ospf
"""
from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result

from scripts.utils import get_credentials, get_jinja_env, load_yaml


def init_nornir():
    """Initialise Nornir depuis inventory/config.yaml et injecte les identifiants
    (nr.inventory.defaults.username / password) depuis get_credentials()."""
    raise NotImplementedError("TP-04, module 1")


def site_routers(nr):
    """Retourne l'objet Nornir filtré sur les routeurs de site (jamais le cœur !)."""
    raise NotImplementedError("TP-04, module 1")


def render_ospf(task):
    """Tâche Nornir : génère la config OSPF du routeur avec templates/ospf.j2 et la stocke dans
    task.host["ospf_config"], puis l'écrit dans config/<hostname>-ospf.cfg (save_text) pour
    pouvoir la relire avant de déployer. Les données viennent du fichier du site (task.host["data_file"]) ;
    le template reçoit site=<le site> et router=<l'élément de site["routers"] de cet hôte>."""
    raise NotImplementedError("TP-04, module 2")


def deploy_ospf(task):
    """Tâche Nornir : appelle render_ospf puis pousse la config (netmiko_send_config ou napalm_configure)."""
    raise NotImplementedError("TP-04, module 2")


if __name__ == "__main__":
    nr = init_nornir()
    # Module 1 : afficher les hôtes, tester les filtres
    # Module 2 : result = site_routers(nr).run(task=deploy_ospf) ; print_result(result)

    print_result(result)
    print("Échecs :", list(result.failed_hosts) or "aucun")
