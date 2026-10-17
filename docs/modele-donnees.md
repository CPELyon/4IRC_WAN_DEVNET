# Modèle de données d'un site (référence du projet)

À partir du TP-02, tous les scripts et les tests utilisent cette structure. Au TP-01, proposez d'abord la vôtre,
puis comparez-la avec celle-ci : qu'avez-vous oublié ? qu'avez-vous fait différemment, et pourquoi ?

```yaml
site: CPE-XXXX                 # nom du site
code: xxxx                     # code court, en minuscules (lyon, marseille, paris)

switch:
  hostname: ESW-XXXX
  trunks:                      # ports vers les routeurs
    - FastEthernet1/0
  access_ports:                # un port par PC
    - interface: FastEthernet1/2
      vlan: 10

routers:                       # 1 routeur (pas de VRRP) ou 2 routeurs (VRRP)
  - hostname: R1-XXXX
    loopback: 10.255.0.X/32
    lan_interface: GigabitEthernet0/0
    vrrp_priority: 110         # ignoré s'il n'y a qu'un routeur
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
- Le cœur suit le même esprit : voir `data/cores.yaml`.
