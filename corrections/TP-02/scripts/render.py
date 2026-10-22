"""TP-02, modules 2 à 4 : générer les configurations des sites à partir de data/ et templates/.

    python -m scripts.render

Pour chaque fichier de site dans data/ (sauf cores.yaml), on génère :
    config/<hostname>.cfg  pour chaque switch et pour chaque routeur.
"""
import glob

from scripts.utils import get_jinja_env, load_yaml, save_text


def render_switch(site, switch, env):
    """Retourne la configuration d'un switch du site (str), à partir de templates/site_switch.j2.

    Le template a besoin du site (VLANs) ET du switch concerné (un site peut avoir plusieurs switchs).
    """
    return env.get_template("site_switch.j2").render(site=site, switch=switch)


def render_router(site, router, env):
    """Retourne la configuration d'un routeur du site (str), à partir de templates/site_router.j2.

    Le template a besoin du site (VLANs, nombre de routeurs) ET du routeur concerné.
    """
    return env.get_template("site_router.j2").render(site=site, router=router)


def render_site(site):
    """Retourne un dict {hostname: configuration} pour tous les équipements du site."""
    env = get_jinja_env()
    configs = {}
    for switch in site["switches"]:
        configs[switch["hostname"]] = render_switch(site, switch, env)
    for router in site["routers"]:
        configs[router["hostname"]] = render_router(site, router, env)
    return configs


if __name__ == "__main__":
    for path in sorted(glob.glob("data/*.yaml")):
        if path.endswith("cores.yaml"):
            continue
        site = load_yaml(path)
        if site is None:
            continue
        for hostname, config in render_site(site).items():
            save_text(f"config/{hostname}.cfg", config)
            print(f"config/{hostname}.cfg généré")
