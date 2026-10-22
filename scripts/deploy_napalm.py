"""TP-03, module 3 : modifier Marseille proprement avec NAPALM (diff, commit, rollback).

    python -m scripts.deploy_napalm R1-MARS
    python -m scripts.deploy_napalm R1-MARS --rollback     # annule le dernier commit
"""
import sys

from napalm import get_network_driver

from scripts.utils import get_credentials

MARS = {"R1-MARS": "172.16.100.190", "R2-MARS": "172.16.100.189", "ESW-MARS": "172.16.100.188"}


def open_device(host):
    """Ouvre et retourne une session NAPALM (driver "ios") vers `host`."""
    raise NotImplementedError("TP-03, module 3")


def preview(device, config_path):
    """Charge config_path en mode fusion (merge) et retourne le diff, SANS rien appliquer."""
    raise NotImplementedError("TP-03, module 3")


def apply(device, config_path, auto=False):
    """Affiche le diff ; s'il est vide, ne fait rien. Sinon, demande confirmation (input) sauf si
    auto=True, puis commit. Retourne True si une modification a été appliquée."""
    raise NotImplementedError("TP-03, module 3")


# ------------------------------------------------------------------ fourni
def rollback():
    """Option --rollback : annule le dernier commit sur l'équipement demandé, puis arrête le script.

    À appeler en PREMIÈRE ligne du __main__. Sans --rollback dans la commande, elle ne fait rien.
        python -m scripts.deploy_napalm R1-MARS --rollback

    Au moment du commit, NAPALM a sauvegardé la running-config dans la flash de l'équipement ;
    device.rollback() la remet en place (configure replace) : l'équipement retrouve son état d'avant.
    """
    if "--rollback" not in sys.argv:
        return
    noms = [arg for arg in sys.argv[1:] if arg != "--rollback"]
    if not noms or noms[0] not in MARS:
        sys.exit(f"Précisez l'équipement à remettre en état : {', '.join(MARS)}\n"
                 "  ex. python -m scripts.deploy_napalm R1-MARS --rollback")
    name = noms[0]
    device = open_device(MARS[name])
    try:
        device.rollback()
        print(f"{name} : retour à la configuration d'avant le dernier commit.")
    finally:
        device.close()
    sys.exit(0)


if __name__ == "__main__":
    rollback()      # avec --rollback : annule le dernier commit et s'arrête ici ; sinon ne fait rien
    name = sys.argv[1] if len(sys.argv) > 1 else "R1-MARS"
    # À compléter : ouvrir la session, appliquer config/<name>.cfg, fermer la session.
    # Erreur volontaire (Vérifier) : appelez rollback() en PREMIÈRE ligne du __main__ (voir sa docstring).
