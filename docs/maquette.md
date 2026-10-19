# La maquette CPE-NET

## Topologie

- **Cœur national** : CORE-1 et CORE-2, OSPF area 0. **Fourni et déjà configuré : on n'y touche pas.**
- **CPE-LYON (siège)** : R1-LYON, R2-LYON (VRRP), ESW-LYON, PC-LYON-10, PC-LYON-20.
- **CPE-MARS (Marseille)** : R1-MARS, R2-MARS (VRRP), ESW-MARS, PC-MARS-10, PC-MARS-20.
- **CPE-PARS (Paris, agence)** : R1-PARS seul, relié aux deux cœurs, ESW-PARS, PC-PARS-10, PC-PARS-20.
- **NOC** : ESW-NOC, PC-ADMIN et votre VM DEVNET, reliés aux deux cœurs.

Nommage : `<RÔLE>-<CODE DU SITE>`, avec un code de 4 lettres (LYON, MARS, PARS). Détail dans [modele-donnees.md](modele-donnees.md).

## Câblage

| Équipement | Port | Vers |
|---|---|---|
| R1 du site | g0/0 | ESW f1/0 (trunk) |
| R2 du site | g0/0 | ESW f1/1 (trunk) |
| PC VLAN 10 | e0 | ESW f1/2 |
| PC VLAN 20 | e0 | ESW f1/3 |
| R1-LYON / R1-MARS / R1-PARS | s1/0 | CORE-1 |
| R2-LYON / R2-MARS | s1/0 | CORE-2 |
| R1-PARS | s1/1 | CORE-2 |
| CORE-1 / CORE-2 | g0/0 | ESW-NOC f1/0 / f1/1 |
| PC-ADMIN / VM DEVNET (e1) | e0 / e1 | ESW-NOC f1/2 / f1/3 |

## Plan d'adressage des sites

| Réseau | Lyon | Marseille | Paris |
|---|---|---|---|
| VLAN 10 teacher | 172.16.10.0/24 | 172.16.30.0/24 | 172.16.50.0/24 |
| VLAN 20 student | 172.16.20.0/24 | 172.16.40.0/24 | 172.16.60.0/24 |
| Passerelle (VIP VRRP) | .254 | .254 | .254 (le routeur lui-même, pas de VRRP) |
| R1 / R2 | .252 / .253 | .252 / .253 | — |
| PC | .1 | .1 | .1 |
| VLAN 30 invités (démo) | 172.16.13.0/24 | 172.16.33.0/24 | 172.16.53.0/24 |

**La logique** : chaque site a une dizaine de réseaux à lui. Lyon prend 172.16.1x et 172.16.2x, Marseille 172.16.3x et 172.16.4x,
Paris 172.16.5x et 172.16.6x. Dans chaque VLAN, la passerelle est la dernière adresse (.254), puis R1 (.252) et R2 (.253) ;
les PC commencent à .1.

- **VRRP** : groupe = numéro de VLAN, R1 maître (priorité 110, preempt), R2 priorité 100.

## Loopbacks (router-id, déjà configurées)

Règle : **10.255.0.XY/32**, avec X = numéro du site (0 = cœur, 1 = Lyon, 2 = Marseille, 3 = Paris) et Y = numéro du routeur.

| Routeur | Loopback | | Routeur | Loopback |
|---|---|---|---|---|
| CORE-1 | 10.255.0.1 | | R1-MARS | 10.255.0.21 |
| CORE-2 | 10.255.0.2 | | R2-MARS | 10.255.0.22 |
| R1-LYON | 10.255.0.11 | | R1-PARS | 10.255.0.31 |
| R2-LYON | 10.255.0.12 | | | |

## Liens WAN (point à point, déjà configurés)

Règle : **10.0.0.0/24 découpé en /30**, numérotés dans l'ordre des liens. Un /30 contient 4 adresses : le réseau, deux
adresses utilisables, le broadcast. **Le cœur prend toujours la première adresse utilisable**, le site la seconde.

| Lien | Réseau | Côté cœur | Côté site |
|---|---|---|---|
| CORE-1 s1/3 ↔ CORE-2 s1/3 | 10.0.0.0/30 | CORE-1 .1 | CORE-2 .2 |
| CORE-1 s1/0 ↔ R1-LYON s1/0 | 10.0.0.4/30 | .5 | .6 |
| CORE-2 s1/0 ↔ R2-LYON s1/0 | 10.0.0.8/30 | .9 | .10 |
| CORE-1 s1/1 ↔ R1-MARS s1/0 | 10.0.0.12/30 | .13 | .14 |
| CORE-2 s1/1 ↔ R2-MARS s1/0 | 10.0.0.16/30 | .17 | .18 |
| CORE-1 s1/2 ↔ R1-PARS s1/0 | 10.0.0.20/30 | .21 | .22 |
| CORE-2 s1/2 ↔ R1-PARS s1/1 | 10.0.0.24/30 | .25 | .26 |

Les liens WAN et les loopbacks sont annoncés en OSPF par le cœur ; les sites rejoindront OSPF au TP-04.

## Administration (déjà configurée)

L'administration passe par un plan dédié en **routage statique, indépendant d'OSPF** : vous pouvez casser OSPF sans perdre l'accès SSH.

Règle : **172.16.100.0/24 découpé en quatre /26**, un par zone. Dans chaque site (VLAN 99), R1 a la dernière adresse,
R2 la précédente, le switch celle d'avant.

| Zone | Réseau | Équipements |
|---|---|---|
| NOC (VLAN 1, VRRP groupe 1) | 172.16.100.0/26 | PC-ADMIN .1, VM DEVNET .2, CORE-1 .60, CORE-2 .61, passerelle VRRP .62 |
| Lyon (VLAN 99) | 172.16.100.64/26 | R1-LYON .126, R2-LYON .125, ESW-LYON .124 |
| Marseille (VLAN 99) | 172.16.100.128/26 | R1-MARS .190, R2-MARS .189, ESW-MARS .188 |
| Paris (VLAN 99) | 172.16.100.192/26 | R1-PARS .254, ESW-PARS .253 |

- **Routes** : chaque cœur a une route statique vers le /26 de chaque site. Côté site, R1 a une route vers le NOC par son
  cœur. R2 passe par R1 tant que R1 répond (suivi `ip sla` + `track 1`), sinon par son propre cœur (route de secours,
  distance 250). Paris a une route principale par CORE-1 et une de secours par CORE-2.
- **Switchs** : passerelle par défaut = R1 du site.
- **VM DEVNET** : 172.16.100.2/26, routes 172.16.0.0/16 et 10.0.0.0/8 via 172.16.100.62 (voir TP-00).

## Identifiants

- Équipements : `cisco` / `cisco` (enable : `cisco`).
- VM DEVNET : `cpe` / `123`.
- Dans vos scripts, lisez-les dans l'environnement :

```bash
export NET_USER=cisco
export NET_PASSWORD=cisco
```

## Ce que vous ne devez pas faire

- Modifier la configuration de CORE-1, CORE-2 et ESW-NOC.
- Supprimer ou modifier le VLAN 99, les sous-interfaces `.99`, les routes statiques, les IP des liens WAN.
- Redistribuer les routes statiques dans OSPF.
