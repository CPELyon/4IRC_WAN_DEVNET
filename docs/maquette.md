# La maquette CPE-NET

## Topologie

- **Cœur national** : CORE-1 et CORE-2, OSPF area 0. **Fourni et déjà configuré : on n'y touche pas.**
- **CPE-LYON (siège)** : R1-LYON, R2-LYON (VRRP), ESW-LYON, PC-LYON-10, PC-LYON-20.
- **CPE-MARSEILLE** : R1-MARS, R2-MARS (VRRP), ESW-MARS, PC-MARS-10, PC-MARS-20.
- **CPE-PARIS (agence)** : R1-PARIS seul, relié aux deux cœurs, ESW-PARIS, PC-PARIS-10, PC-PARIS-20.
- **NOC** : ESW-NOC, PC-ADMIN et votre VM DEVNET, reliés aux deux cœurs.

## Câblage des sites

| Équipement | Port | Vers |
|---|---|---|
| R1 du site | g0/0 | ESW f1/0 (trunk) |
| R2 du site | g0/0 | ESW f1/1 (trunk) |
| PC VLAN 10 | e0 | ESW f1/2 |
| PC VLAN 20 | e0 | ESW f1/3 |
| R1-LYON / R1-MARS / R1-PARIS | s1/0 | CORE-1 |
| R2-LYON / R2-MARS | s1/0 | CORE-2 |
| R1-PARIS | s1/1 | CORE-2 |

## Plan d'adressage

| Réseau | Lyon | Marseille | Paris |
|---|---|---|---|
| VLAN 10 teacher | 172.16.10.0/24 | 172.16.30.0/24 | 172.16.50.0/24 |
| VLAN 20 student | 172.16.20.0/24 | 172.16.40.0/24 | 172.16.60.0/24 |
| Passerelle (VIP VRRP) | .254 | .254 | .254 (pas de VRRP) |
| R1 / R2 | .252 / .253 | .252 / .253 | — |
| VLAN 30 invités (démo) | 172.16.13.0/24 | 172.16.33.0/24 | 172.16.53.0/24 |

- **VRRP** : groupe = numéro de VLAN, R1 maître (priorité 110, preempt), R2 priorité 100.
- **Liens WAN** (/30, déjà configurés) : R1-LYON 10.0.0.6, R2-LYON 10.0.0.10, R1-MARS 10.0.0.14, R2-MARS 10.0.0.18, R1-PARIS 10.0.0.22 et 10.0.0.26 (le cœur a la première adresse de chaque /30).
- **Loopbacks** (router-id, déjà configurées) : R1-LYON 10.255.0.11, R2-LYON .12, R1-MARS .21, R2-MARS .22, R1-PARIS .31, CORE-1 .1, CORE-2 .2.

## Administration (VLAN 99, déjà configuré)

L'administration passe par un VLAN dédié en **routage statique, indépendant d'OSPF** : vous pouvez casser OSPF sans perdre l'accès SSH.

| Équipement | IP d'administration |
|---|---|
| CORE-1 / CORE-2 | 172.16.100.60 / 172.16.100.61 |
| R1-LYON / R2-LYON / ESW-LYON | 172.16.100.126 / .125 / .124 |
| R1-MARS / R2-MARS / ESW-MARS | 172.16.100.190 / .189 / .188 |
| R1-PARIS / ESW-PARIS | 172.16.100.254 / .253 |
| VM DEVNET | 172.16.100.2/26, routes 172.16.0.0/16 et 10.0.0.0/8 via 172.16.100.62 (déjà configuré, voir TP-00) |

- Identifiants : `cisco` / `cisco` (enable : `cisco`).
- VM DEVNET : `cpe` / `123`.
- Dans vos scripts, lisez-les dans l'environnement :

```bash
export NET_USER=cisco
export NET_PASSWORD=cisco
```

## Ce que vous ne devez pas faire

- Modifier la configuration de CORE-1 et CORE-2.
- Supprimer ou modifier le VLAN 99, les sous-interfaces `.99`, les routes statiques, les IP des liens WAN.
- Redistribuer les routes statiques dans OSPF.
