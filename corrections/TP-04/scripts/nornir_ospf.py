"""TP-04, modules 1 et 2 : l'inventaire Nornir, puis OSPF sur tous les routeurs de site (correction).

    python -m scripts.nornir_ospf
"""
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_save_config, netmiko_send_config
from nornir_utils.plugins.functions import print_result

from scripts.utils import get_credentials, get_jinja_env, load_yaml, save_text


def init_nornir():
    """Initialise Nornir depuis inventory/config.yaml et injecte les identifiants
    (nr.inventory.defaults.username / password) depuis get_credentials()."""
    nr = InitNornir(config_file="inventory/config.yaml")
    username, password = get_credentials()
    nr.inventory.defaults.username = username      # defaults : hérité par tous les hôtes
    nr.inventory.defaults.password = password
    return nr


def site_routers(nr):
    """Retourne l'objet Nornir filtré sur les routeurs de site (jamais le cœur !)."""
    return nr.filter(role="site_router")


def render_ospf(task):
    """Tâche Nornir : génère la config OSPF du routeur avec templates/ospf.j2 et la stocke dans
    task.host["ospf_config"], puis l'écrit dans config/<hostname>-ospf.cfg pour pouvoir la relire
    avant de déployer. Les données viennent du fichier du site (task.host["data_file"])."""
    site = load_yaml(task.host["data_file"])
    router = next(r for r in site["routers"] if r["hostname"] == task.host.name)
    config = get_jinja_env().get_template("ospf.j2").render(site=site, router=router)
    task.host["ospf_config"] = config
    save_text(f"config/{task.host.name}-ospf.cfg", config)   # à relire avant de déployer
    return config                       # visible dans print_result


def deploy_ospf(task):
    """Tâche Nornir : appelle render_ospf puis pousse la config (netmiko_send_config ou napalm_configure)."""
    task.run(task=render_ospf)
    task.run(task=netmiko_send_config, config_commands=task.host["ospf_config"].splitlines())
    task.run(task=netmiko_save_config)

    # Variante NAPALM (fusion, avec diff) :
    # from nornir_napalm.plugins.tasks import napalm_configure
    # task.run(task=napalm_configure, configuration=task.host["ospf_config"], dry_run=False)


if __name__ == "__main__":
    nr = init_nornir()

    # ----- Module 1 : découvrir l'inventaire (décommenter pour tester)
    # print(nr.inventory.hosts)                          # les 10 équipements
    # h = nr.inventory.hosts["R1-LYON"]
    # print(h.hostname, h.platform, h.groups, h["role"], h["data_file"])
    # print(h.data, h.extended_data())                   # {} : role vient des groupes, pas de l'hôte
    # print(h.username)                                  # cisco : .env -> get_credentials() -> defaults
    # print(h.get_connection_parameters("netmiko").dict())   # ce que Nornir passera à Netmiko (cisco_ios)
    # print(nr.filter(role="switch").inventory.hosts.keys())
    # print(nr.filter(F(site="CPE-LYON") & F(role="site_router")).inventory.hosts.keys())
    # print(site_routers(nr).inventory.hosts.keys())     # 5 routeurs, ni CORE-1 ni CORE-2

    # ----- Module 2 : OSPF
    # Un seul routeur d'abord :
    # result = nr.filter(name="R1-PARS").run(task=deploy_ospf)
    # Aperçu sans rien envoyer (génère seulement config/<hostname>-ospf.cfg) :
    # result = site_routers(nr).run(task=render_ospf)
    result = site_routers(nr).run(task=deploy_ospf)
    print_result(result)
    print("Échecs :", list(result.failed_hosts) or "aucun")
