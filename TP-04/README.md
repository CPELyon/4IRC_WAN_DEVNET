# TP-04 — Passer à l'échelle avec Nornir

**Bloc NAF : Exécuteur** · Séance 4 · Avant de commencer : `git pull --no-edit upstream main`

> Au TP-03, chaque script ouvrait ses connexions une par une, avec des IP écrites à la main.
> Nornir change d'échelle : un inventaire décrit tout le réseau, des filtres choisissent les cibles,
> et une même tâche part sur tous les équipements en parallèle.

| Module | Objectif |
|---|---|
| 1. L'inventaire Nornir | Décrire les équipements, leurs rôles, leurs sites, et comment s'y connecter |
| 2. OSPF sur les sites | Monter les voisins avec le cœur, en une seule exécution |

Rappel : le cœur est **fourni et en lecture seule**. Vos tâches de configuration ne doivent jamais le cibler.

---

## Module 1 — L'inventaire Nornir

**Objectif** : à la fin, Nornir connaît les 10 équipements administrables (cœur, routeurs et switchs de site), sait s'y connecter, et je sais les filtrer.

### Préparer les identifiants
Les identifiants des équipements ne s'écrivent ni dans le code ni dans l'inventaire : ils vivent dans un fichier `.env` à la racine du projet, qui n'est **jamais poussé**.

```bash
printf 'NET_USER=cisco\nNET_PASSWORD=cisco\n' > .env
set -a && source .env && set +a      # charge le fichier dans le terminal (à refaire dans chaque nouveau terminal)
echo $NET_USER
git status                           # .env n'apparaît pas : il est listé dans .gitignore
```

👀 **Lisez** `get_credentials()` dans `scripts/utils.py` : où va-t-elle chercher les identifiants ? **(au TP-05, le jeton NetBox rejoindra le même `.env`)**

### Construire
👀 **Lisez** les fichiers de `inventory/` : `config.yaml` (où sont les autres fichiers, `num_workers`), `groups.yaml` (rôles, sites, `data_file`) et `defaults.yaml`. Comment un hôte hérite-t-il des données de ses groupes ? À quoi sert `data_file` ? **(`data_file` relie chaque hôte à son YAML : vos templates OSPF du module 2 en dépendent ; `num_workers` explique la durée du déploiement)**

1. Complétez `inventory/hosts.yaml` (le cœur et R1-LYON sont donnés) et les groupes de sites dans `inventory/groups.yaml`.
2. Complétez `init_nornir()` (identifiants de `get_credentials()` rangés dans `nr.inventory.defaults`) et `site_routers()` dans `scripts/nornir_ospf.py`.

### Découvrir
```python
nr = init_nornir()
print(nr.inventory.hosts)
h = nr.inventory.hosts["R1-LYON"]
print(h.hostname, h.platform, h.groups, h["role"], h["data_file"])
print(h.data, h.extended_data())
print(h.username)
print(h.get_connection_parameters("netmiko").dict())
print(nr.filter(role="switch").inventory.hosts.keys())
print(nr.filter(F(site="CPE-LYON") & F(role="site_router")).inventory.hosts.keys())
```
- D'où viennent `platform` et `role` alors qu'ils ne sont pas dans `hosts.yaml` ? Pourquoi `h.data` est-il vide ?
- `h.username` n'est écrit dans aucun fichier YAML : quel chemin a-t-il suivi depuis `.env` ?
- Pourquoi ranger les identifiants dans `nr.inventory.defaults` plutôt que sur chaque hôte ?
- Lisez la valeur par défaut de `get_credentials()` : pourquoi vos scripts marchent-ils même sans `.env` chargé, et pourquoi ce ne serait pas acceptable sur un vrai réseau ?

### Vérifier
- `site_routers(nr)` renvoie exactement 5 routeurs, sans CORE-1 ni CORE-2.
- `h.username` vaut la valeur de votre `.env`.

---

## Module 2 — OSPF sur les sites

**Objectif** : à la fin, les 5 routeurs de site sont voisins OSPF du cœur et les sites communiquent entre eux.

### Construire
1. `templates/ospf.j2` : processus 1, `router-id` = loopback, un `network … area 0` pour chaque lien WAN, la loopback et chaque VLAN utilisateur, `passive-interface` sur les sous-interfaces des VLANs et Lo0.
   - Toutes les informations sont **déjà dans vos YAML** : pas de nouvelle donnée à inventer.
   - Le template reçoit les **mêmes variables que `site_router.j2`** : `site` et `router` (l'élément de `site["routers"]` qui correspond à l'hôte).
   - Filtres utiles : `network`, `wildcard`.
2. Complétez `render_ospf()` : elle génère la config OSPF du routeur, la range dans `task.host["ospf_config"]` **et l'écrit dans `config/<hostname>-ospf.cfg`** (avec `save_text`, comme au TP-02).
3. Générez sans rien envoyer : `site_routers(nr).run(task=render_ospf)`, puis **relisez les 5 fichiers `config/*-ospf.cfg`** (router-id, réseaux, interfaces passives) avant d'aller plus loin.
4. Complétez `deploy_ospf()` : elle appelle `render_ospf`, puis pousse `task.host["ospf_config"]` (avec `netmiko_send_config` ou `napalm_configure`).
5. Testez d'abord sur un seul routeur : `nr.filter(name="R1-PARS").run(task=deploy_ospf)`.
6. Puis sur tous : `site_routers(nr).run(task=deploy_ospf)`.

### Vérifier
- `config/` contient `R1-LYON-ospf.cfg`, `R2-LYON-ospf.cfg`, `R1-MARS-ospf.cfg`, `R2-MARS-ospf.cfg` et `R1-PARS-ospf.cfg`.
- Sur CORE-1 : `show ip ospf neighbor` → R1-LYON, R1-MARS, R1-PARS et CORE-2 en FULL.
- PC-LYON-10 → `ping 172.16.50.1` (Paris) et `ping 172.16.30.1` (Marseille).
- Coupez le lien R1-LYON ↔ CORE-1 (`shutdown` sur s1/0 de R1-LYON, à remettre en `no shutdown` ensuite) : Lyon joint-il toujours Paris ? Par où passe le trafic (`traceroute`) ?

### Comprendre
- Pourquoi `passive-interface` sur les VLANs des PC ?
- Combien de temps a pris le déploiement sur 5 routeurs ? Et en séquentiel (`num_workers: 1`) ?
- Relancez `deploy_ospf` : que renvoie Nornir pour chaque routeur ? Qu'est-ce que `print_result` affiche de `changed` ?

✅ **Point de contrôle** : faites constater les voisins OSPF et un ping Lyon → Paris.

✅ **Fin de séance** : `git commit -m "TP4 : Nornir et OSPF"` puis `git push`.
