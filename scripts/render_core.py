"""EXEMPLE FOURNI (fonctionne tel quel) : génère la configuration des deux routeurs du cœur.

    python -m scripts.render_core

Lisez ce script et templates/core_router.j2 : c'est le modèle à suivre pour vos sites.
"""
import yaml

from scripts.utils import get_jinja_env

if __name__ == "__main__":
    with open("data/cores.yaml") as f:
        cores = yaml.safe_load(f)
    template = get_jinja_env().get_template("core_router.j2")
    for router in cores["routers"]:
        config = template.render(router=router, vlans=cores["vlans"], ospf=cores["ospf"])
        print(f"===== {router['hostname']} =====")
        print(config)
