"""TP-03, module 3 : modifier Marseille proprement avec NAPALM (diff, commit, rollback) (correction).

    python -m scripts.deploy_napalm R1-MARS
    python -m scripts.deploy_napalm R1-MARS --rollback     # annule le dernier commit
"""
import sys

from napalm import get_network_driver

from scripts.utils import get_credentials

MARS = {"R1-MARS": "172.16.100.190", "R2-MARS": "172.16.100.189", "ESW-MARS": "172.16.100.188"}


def open_device(host):
    """Ouvre et retourne une session NAPALM (driver "ios") vers `host`."""
    username, password = get_credentials()
    driver = get_network_driver("ios")
    device = driver(hostname=host, username=username, password=password)
    device.open()
    return device


def preview(device, config_path):
    """Charge config_path en mode fusion (merge) et retourne le diff, SANS rien appliquer."""
    device.load_merge_candidate(filename=config_path)
    return device.compare_config()


def apply(device, config_path, auto=False):
    """Affiche le diff ; s'il est vide, ne fait rien. Sinon, demande confirmation (input) sauf si
    auto=True, puis commit. Retourne True si une modification a été appliquée."""
    diff = preview(device, config_path)
    if not diff:
        print("Aucune différence : rien à appliquer.")
        device.discard_config()
        return False

    print(diff)
    if not auto and input("Appliquer ces changements ? [o/N] ").strip().lower() != "o":
        print("Annulé.")
        device.discard_config()
        return False

    device.commit_config()
    print("Changements appliqués.")
    return True


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
    device = open_device(MARS[name])
    try:
        # ----- Module 3 étape 1 : essai (décommenter pour tester)
        # from pprint import pprint
        # facts = device.get_facts()
        # pprint(facts)                      # un dictionnaire aux clés normalisées, pas du texte
        # print(facts["hostname"], facts["os_version"], "Serial1/0" in facts["interface_list"])

        apply(device, f"config/{name}.cfg")
    finally:
        device.close()
