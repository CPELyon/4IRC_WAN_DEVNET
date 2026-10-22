"""Tests des configurations générées (à compléter au TP-06).

    pytest tests/test_render.py -v
"""
import glob

import pytest

from scripts.render import render_site
from scripts.utils import load_yaml

SITES = [p for p in sorted(glob.glob("data/*.yaml")) if not p.endswith("cores.yaml")]


@pytest.mark.parametrize("path", SITES)
def test_chaque_vlan_a_sa_sous_interface(path):
    site = load_yaml(path)
    configs = render_site(site)
    for router in site["routers"]:
        for vlan in site["vlans"]:
            assert f"encapsulation dot1Q {vlan['id']}" in configs[router["hostname"]]


# TP-06 : ajoutez vos propres tests, par exemple
# - un site à deux routeurs a bien une ligne "vrrp <id> ip <gateway>" par VLAN sur chaque routeur
# - Paris n'a aucune ligne vrrp
# - aucune config générée ne touche au VLAN 99
