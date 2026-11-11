"""FOURNI : génère config/<hostname>.cfg pour tous les sites, à partir de NetBox (et plus de data/).

    python -m scripts.render_netbox            # tous les sites
    python -m scripts.render_netbox lyon       # un seul site

Même rendu que scripts/render.py (vos templates n'ont pas changé) : seule la SOURCE de l'intention change.
"""
import sys

from scripts.intent import get_site, list_sites
from scripts.netbox_import import get_api
from scripts.render import render_site
from scripts.utils import save_text

if __name__ == "__main__":
    nb = get_api()
    for code in sys.argv[1:] or list_sites(nb):
        for hostname, config in render_site(get_site(nb, code)).items():
            save_text(f"config/{hostname}.cfg", config)
            print(f"config/{hostname}.cfg généré (NetBox, site {code})")
