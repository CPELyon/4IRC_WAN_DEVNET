# Projet fil rouge — Automatisation réseau (CPE Lyon)

Vous êtes l'équipe NetOps de CPE. Trois sites (Lyon, Marseille, Paris) sont reliés par un cœur national.
Au fil des 7 séances, vous construisez l'outil qui automatise ce réseau, bloc par bloc, en suivant le
framework du Network Automation Forum (NAF).

| Séance | Bloc NAF | Sujet |
|---|---|---|
| Avant la 1 | — | [TP-00 — Préparer son environnement](TP-00/README.md) (GNS3, VM, réseau) |
| 1 | Intention | TP-01 — Décrire le réseau |
| 2 | Intention | TP-02 — Générer les configurations |
| 3 | Exécuteur | TP-03 — Appliquer l'état voulu |
| 4 | Exécuteur + Collecteur | TP-04 — Passer à l'échelle, lire l'état réel |
| 5 | Intention (source de vérité) | TP-05 — NetBox |
| 6 | Observabilité + Orchestrateur | TP-06 — Détecter les écarts, orchestrer |
| 7 | Présentation | TP-07 — Une API pour piloter le réseau |

**Commencez par le TP-00**, à faire avant la séance 1 : il se lit directement sur GitHub.

Le dépôt grandit au fil des séances : chaque sujet `TP-0N/`, ses squelettes de code et la correction
de la séance précédente sont publiés au début de la séance.

## Arborescence

```
4IRC_WAN_DEVNET/
├── TP-00/           préparer son environnement (avant la séance 1)
├── TP-01 … TP-07/   les sujets de TP (publiés au fil des séances)
├── data/            l'INTENTION en YAML (cores.yaml est fourni en exemple)
├── templates/       les templates Jinja2 (core_router.j2 est fourni en exemple)
├── config/          les configurations générées (ne pas modifier à la main)
├── backups/         les sauvegardes des équipements
├── inventory/       l'inventaire Nornir (séance 4)
├── scripts/         votre code Python (squelettes fournis séance par séance)
├── tests/           les tests automatiques (pytest)
├── observability/   l'historique des collectes et les événements (séance 6)
├── api/             l'API Flask (séance 7)
├── ci/              la pipeline CI GitHub Actions fournie (séance 6)
├── corrections/     les corrections, publiées après chaque séance
└── docs/            la maquette, le plan d’adressage, le modèle de données
```

## Deux dépôts : `upstream` et `origin`

- **`upstream`** : le dépôt de l'enseignant, https://github.com/CPELyon/4IRC_WAN_DEVNET. Vous le lisez, vous n'y poussez jamais.
- **`origin`** : votre dépôt, privé. Vous y poussez votre travail, en SSH ou en HTTPS avec un jeton (au choix, voir TP-01).

La mise en place est décrite dans le TP-01 (module 1). Ensuite, **au début de chaque séance** :

```bash
git pull --no-edit upstream main     # récupère le nouveau sujet, les squelettes et la correction
git push                   # les range aussi dans votre dépôt
```

## Conventions du projet

- **On lance toujours les scripts depuis la racine** : `python -m scripts.<nom>` (jamais `cd scripts`).
- **Chaque fonction du squelette a une docstring** : elle décrit ce que la fonction doit faire. Remplacez le `raise NotImplementedError` par votre code.
- **Les fichiers de `config/` sont générés** : on corrige les données ou le template, jamais la config générée.
- **Pas de mot de passe dans le code** : on les lit dans des variables d'environnement (voir `docs/maquette.md`).
- **Un commit par étape qui fonctionne**, avec un message clair : `git commit -m "TP2 : template VRRP"`.

## Règles pour éviter les conflits

- **Ne modifiez pas** les fichiers de l'enseignant : `README.md`, `TP-0N/README.md`, `docs/`, `corrections/`.
  Ils peuvent être mis à jour, et vos modifications créeraient des conflits au `git pull --no-edit upstream main`.
- Vos notes et comptes rendus vont dans **vos** fichiers (par ex. `TP-01/notes-lyon.txt`).
- Les squelettes (`scripts/`, `templates/`, `tests/`…) sont à vous : l'enseignant n'y touche plus une fois publiés.

## Si vous avez décroché

Les corrections arrivent dans `corrections/TP-0N/`, avec la même arborescence que le projet.
Comparez avec votre code, ou copiez les fichiers dont vous avez besoin pour repartir :

```bash
cp corrections/TP-02/templates/site_router.j2 templates/
```

## Accès à la maquette

Voir [docs/maquette.md](docs/maquette.md) : topologie, plan d'adressage, identifiants.
