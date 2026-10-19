# Modèle de données d'un site (référence du projet)

À partir du TP-02, tous les scripts et les tests utilisent cette structure. Au TP-01, proposez d'abord la vôtre,
puis comparez-la avec celle-ci : qu'avez-vous oublié ? qu'avez-vous fait différemment, et pourquoi ?

Un fichier par site : `data/<code>.yaml` (`data/lyon.yaml`, `data/mars.yaml`, `data/pars.yaml`).

```yaml
site: CPE-XXXX                 # nom du site : CPE- suivi du code en majuscules
code: xxxx                     # code du site, 4 lettres en minuscules (lyon, mars, pars) = nom du fichier

switches:                      # un ou plusieurs switchs
  - hostname: ESW-XXXX
    platform: ios
    model: c3725
    trunks:                    # ports vers les routeurs
      - FastEthernet1/0
    access_ports:              # un port par PC
      - interface: FastEthernet1/2
        vlan: 10

routers:                       # 1 routeur (pas de VRRP) ou 2 routeurs (VRRP)
  - hostname: R1-XXXX
    platform: ios
    model: c7200
    loopback: 10.255.0.X/32
    lan_interface: GigabitEthernet0/0
    vrrp_priority: 110         # seulement s'il y a deux routeurs
    wan:
      - interface: Serial1/0
        ip: 10.0.0.X/30
        peer: CORE-1
    ips:                       # IP RÉELLE du routeur dans chaque VLAN (clé = numéro de VLAN)
      10: 172.16.X.252/24

vlans:
  - id: 10
    name: teacher
    subnet: 172.16.X.0/24
    gateway: 172.16.X.254      # VIP VRRP, ou IP du routeur s'il est seul
```

## Règles

- **Pas de syntaxe Cisco** dans les données : on décrit le réseau, le template s'occupe de la configuration.
- **Un site a du VRRP s'il a deux routeurs** : on ne stocke pas de booléen, on le déduit.
- **Le groupe VRRP est le numéro du VLAN** : inutile de le répéter.
- **Le VLAN 99 d'administration n'apparaît pas** : il est déjà configuré et ne doit pas être modifié.
- **Les équipements sont des listes** (`switches`, `routers`) : un site peut en avoir un ou plusieurs.

## Nommage

| Élément | Règle | Exemples |
|---|---|---|
| Code du site | 4 lettres | `LYON`, `MARS`, `PARS` (en minuscules dans `code`) |
| Nom du site | `CPE-<CODE>` | `CPE-LYON`, `CPE-MARS`, `CPE-PARS` |
| Routeur | `R<n>-<CODE>` | `R1-LYON`, `R2-MARS`, `R1-PARS` |
| Switch | `ESW-<CODE>` | `ESW-LYON` |
| PC | `PC-<CODE>-<VLAN>` | `PC-MARS-10` |

Le rôle et le site se lisent donc directement dans le nom : `role, code = "R1-MARS".split("-")`.

## Le cœur et le NOC

`data/cores.yaml` décrit le cœur (CORE-1, CORE-2) et le NOC (ESW-NOC) avec **les mêmes champs** que les sites,
plus deux champs qui lui sont propres : `ospf` et `admin_routes` (routes d'administration). Le NOC est le VLAN 1,
d'où le groupe VRRP 1. Ce fichier est fourni et sert d'exemple : les scripts des TP ne le traitent pas.
