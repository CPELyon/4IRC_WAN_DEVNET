# TP-05 — Une source de vérité : NetBox

**Bloc NAF : Intention** · Séance 5 · Avant de commencer : `git pull --no-edit upstream main`

> Le NAF attend de l'intention des opérations CRUD, une API documentée, une vue unique de l'état voulu et
> des métadonnées de gouvernance. Vos fichiers YAML ne font pas tout ça : NetBox, si.
> **À partir de ce TP, NetBox fait foi jusqu'à la fin du module** : on modifie l'intention dans NetBox, plus dans `data/*.yaml`.

Ici, vous n'avez pas à construire NetBox : la préparation et l'import sont **fournis**. Vous écrivez seulement
les quelques fonctions qui montrent comment on parle à NetBox, et vous passez le plus de temps possible
à **modifier NetBox et voir le changement descendre jusqu'aux équipements**.

| Module | Objectif |
|---|---|
| 1. Découvrir NetBox | Lancer NetBox, le préparer, explorer le cœur |
| 2. Interroger l'API REST | Lire NetBox depuis un navigateur, curl, puis Python |
| 3. Importer ses sites | Compléter deux fonctions, importer Lyon, Marseille et Paris sans doublon |
| 4. Des données NetBox aux configurations | Relire l'intention dans NetBox et générer les mêmes configs |
| 5. Modifier NetBox, voir le réseau suivre | Un changement fait dans NetBox, déployé par Nornir avec un inventaire lu dans NetBox |


📚 **Documentation officielle**, à garder ouverte pendant le TP :
- **pynetbox**, la bibliothèque Python pour NetBox : https://netbox-community.github.io/pynetbox/ (*Quick Start*, puis *API Reference › Endpoint* pour `get`, `filter`, `create`) ;
- **l'API REST de NetBox** : https://netboxlabs.com/docs/netbox/integrations/rest-api/ ;
- **la documentation interactive de votre NetBox**, avec toutes les routes et tous leurs filtres : http://localhost:8000/api/schema/swagger-ui/

---

## Module 1 — Découvrir NetBox

**Objectif** : à la fin, je sais où se trouvent sites, équipements, interfaces, VLANs, préfixes et IP.

### Découvrir
1. Dans la VM, lancez NetBox :
   ```bash
   cd ~/netbox-docker && docker compose up -d
   ```
   > ⏳ **Le tout premier démarrage est long : 10 à 15 minutes sur la VM.** Ce n'est pas une panne. NetBox crée sa base de données
   > (plusieurs centaines de *migrations* : une par évolution du schéma depuis la première version), puis son index de recherche
   > et le compte `admin`. Pendant ce temps, `docker compose` affiche `Waiting` : il attend que NetBox réponde avant de lancer le *worker*.
   > Les démarrages suivants prennent moins d'une minute : la base existe déjà, elle est conservée dans un volume Docker.

   Pour suivre ce qui se passe, dans un **second terminal** :
   ```bash
   cd ~/netbox-docker && docker compose logs -f netbox     # Ctrl+C pour quitter
   ```
   Vous verrez défiler `Applying …`, puis `Building search index`, et enfin `✅ Initialisation is done` : NetBox est prêt.
   Si la première commande s'est arrêtée entre-temps sur `unhealthy`, relancez-la simplement : `docker compose up -d`.
   Vérifiez avec `docker compose ps` : `netbox` doit être `healthy`.

   Ouvrez ensuite **http://localhost:8000 dans le navigateur de votre PC** (la VM redirige le port 8000). Identifiants : `admin` / `admin`.
2. Créez un jeton d'API (*Profil › API Tokens › Add*), puis ajoutez-le au fichier `.env` du TP-04 (à la racine du projet, jamais poussé) :
   ```bash
   cd ~/4IRC_WAN_DEVNET_NOM_PRENOM               # revenez dans VOTRE projet (vous étiez dans ~/netbox-docker)
   echo 'NB_TOKEN=nbt_xxxxxxxx.yyyyyyyyyyyy' >> .env   # votre jeton, SANS « Bearer »
   set -a && source .env && set +a               # à refaire dans chaque nouveau terminal
   git status                                    # .env n'apparaît pas : il est bien ignoré
   ```
   > ⚠️ Dans `.env`, mettez **uniquement le jeton** (il commence par `nbt_`), sans le mot `Bearer` et sans espace.
   > `Bearer` n'est pas une partie du jeton : c'est le **type d'authentification**, que curl et pynetbox ajoutent eux-mêmes
   > dans l'en-tête HTTP (`Authorization: Bearer $NB_TOKEN`). Avec un espace, `source .env` essaie d'exécuter la fin de la ligne
   > comme une commande : `bash: nbt_…: command not found`.
3. Préparez NetBox avec ce que vous n'avez pas à faire vous-même :
   ```bash
   python -m scripts.netbox_init
   ```
   - 👀 **Lisez** `scripts/netbox_init.py` : qu'est-ce qui est créé, et dans quel ordre ? Pourquoi les IP d'administration de vos équipements sont-elles seulement **réservées** ? **(votre import du module 3 les affectera)**
4. Explorez le site **CPE-CORE**, puis CORE-1 : rôle, modèle, plateforme, interfaces, IP, câbles.
   - Où est l'IP virtuelle VRRP du NOC ? (*IPAM › FHRP Groups*)
   - Où sont les IP réservées pour vos équipements ? (*IPAM › IP Addresses*, filtre *Status = Reserved*)
5. Ouvrez l'historique (*Changelog*) : qui a créé ces objets, et quand ?

### Comprendre
- Quelles exigences du NAF NetBox remplit-il, que vos YAML ne remplissaient pas ?
- Comparez CORE-1 dans NetBox et dans `data/cores.yaml` : c'est la même information, rangée autrement. Qu'est-ce qui est **relié** dans NetBox et ne l'était pas dans le YAML ?

---

## Module 2 — Interroger l'API REST

**Objectif** : à la fin, je lis NetBox par son API, comme le ferait n'importe quel outil.

### Construire
1. Ouvrez http://localhost:8000/api/ dans le navigateur : l'API est navigable. Descendez jusqu'à `dcim › devices`.
   Comparez avec http://localhost:8000/api/schema/swagger-ui/ : la même API, documentée route par route.
2. En ligne de commande, dans la VM :
   ```bash
   curl -s -H "Authorization: Bearer $NB_TOKEN" -H "Accept: application/json" \
        "http://localhost:8000/api/dcim/devices/?site=core" | python3 -m json.tool
   ```
3. Même chose en Python avec `requests`, dans `scripts/tp05_module2.py` (à créer) : récupérez la même réponse que le `curl` et affichez-la.
   Lancez-le avec `python -m scripts.tp05_module2`.

### Comprendre
- Que renvoie l'API sans jeton ? Avec un mauvais jeton ? Quels codes HTTP ?
- Dans la réponse JSON, `primary_ip` est un objet, pas une chaîne : pourquoi ?

---

## Module 3 — Importer ses sites

**Objectif** : à la fin, vos trois sites sont dans NetBox, modélisés comme le cœur.

L'import complet est fourni dans `scripts/netbox_import.py`. Il ne lui manque que deux fonctions, celles qui
portent les deux idées importantes : **se connecter** à l'API et **ne jamais créer de doublon**.

**Prérequis** : vos fichiers `data/*.yaml` respectent `docs/modele-donnees.md` et `python -m scripts.validate` passe.
Avant d'envoyer quoi que ce soit à NetBox, l'import vérifie lui-même vos fichiers (noms, modèles, adresses…) et s'arrête
avec la liste de ce qu'il faut corriger. Si vos données s'écartent trop du modèle, repartez de `corrections/TP-01/data/`
(et de `corrections/TP-03/data/mars.yaml`) : attention, l'un de ces fichiers contient encore l'erreur volontaire du TP-02.

### Construire
1. Complétez `get_api()` puis `get_or_create()` dans `scripts/netbox_import.py`, avec la documentation de pynetbox (https://netbox-community.github.io/pynetbox/) : *Quick Start* pour se connecter, *Endpoint* pour `get()` et `create()`.
   - 👀 **Lisez** la docstring de `get_or_create()` : pourquoi « chercher, puis créer seulement si absent » rend-il l'import relançable sans doublon ? **(au TP-06, ajouter un VLAN dans NetBox réutilisera cet import)**
2. Importez Lyon, vérifiez dans l'interface, puis Marseille et Paris :
   ```bash
   python -m scripts.netbox_import data/lyon.yaml
   python -m scripts.netbox_import data/mars.yaml data/pars.yaml
   ```
3. 👀 **Lisez** `import_router()` : retrouvez dans NetBox chaque objet qu'elle crée (interface, sous-interface, IP, IP principale).

### Vérifier
- **Relancez l'import** : plus aucune ligne « créé » ni « mis à jour » ne s'affiche, seulement les noms des sites (idempotence).
- Dans NetBox, le préfixe 172.16.10.0/24 contient .252, .253 et la VIP .254 (rôle VRRP).
- Chaque équipement a une **IP principale** : son IP d'administration.


> ⚠️ **À partir de maintenant, NetBox fait foi : ne relancez plus `python -m scripts.netbox_import data/…`.**
> Vos fichiers `data/*.yaml` contiennent l'intention d'*avant* NetBox, et l'import met à jour les objets qui existent déjà :
> il effacerait vos modifications faites dans NetBox (par exemple la priorité VRRP que vous changerez au module 5).
> Les **fonctions** de `netbox_import.py`, elles, resserviront : au TP-06, `scripts/netbox_vlan.py` relira un site **dans NetBox**,
> y ajoutera un VLAN, et le renverra à `import_site()`. Les données venant de NetBox, seul le nouveau VLAN sera créé.
> Ce qui compte, c'est d'où viennent les données qu'on donne à l'import.

---

## Module 4 — Des données NetBox aux configurations

**Objectif** : à la fin, je génère mes configurations à partir de NetBox, et plus à partir de `data/*.yaml`, sans changer mes templates.

### Le problème
Vos templates (TP-02) attendent un dictionnaire au format de `docs/modele-donnees.md`. Par exemple, pour un VLAN :
```yaml
vlans:
  - id: 10
    name: teacher
    subnet: 172.16.10.0/24
    gateway: 172.16.10.254
```
NetBox contient les mêmes informations, mais **réparties dans plusieurs objets reliés entre eux** :

| Dans le YAML | Dans NetBox |
|---|---|
| `id`, `name` | un **VLAN** (numéro 10, nom `teacher`), rattaché au site |
| `subnet` | un **préfixe** 172.16.10.0/24, rattaché à ce VLAN |
| `gateway` | une **adresse IP** 172.16.10.254/24 de rôle « VRRP », dans ce préfixe |

Il faut donc aller chercher ces objets un par un dans l'API et **reconstruire le dictionnaire**. C'est le rôle de `scripts/intent.py` :
sa fonction `get_site(nb, "lyon")` doit renvoyer **exactement** ce que renvoie `load_yaml("data/lyon.yaml")`. Si c'est le cas,
vos templates fonctionnent tels quels avec NetBox.

### Ce qui est fourni, ce que vous écrivez

| Dans `scripts/intent.py` | Rôle | |
|---|---|---|
| `get_site()` | Assemble le dictionnaire complet d'un site | fourni |
| `_router()`, `_switch()` | Reconstruisent `routers` et `switches` | fourni (lisez-les : ce sont vos modèles) |
| `list_sites()` | Liste les codes des sites présents dans NetBox | **à écrire** |
| `_vlans()` | Reconstruit `vlans` (le tableau ci-dessus) | **à écrire** |

`scripts/render_netbox.py` (fourni) fait ensuite la même chose que `scripts/render.py`, mais avec `get_site()` au lieu de `load_yaml()`.

### Construire
1. Écrivez `list_sites()`, puis testez :
   ```bash
   python -m scripts.intent                    # attendu : ['lyon', 'mars', 'pars']
   ```
2. 👀 **Lisez** `_router()` : comment va-t-on chercher les IP d'une interface ? La priorité VRRP ?
   Puis écrivez `_vlans()` en suivant le tableau du « Problème » (les indices sont dans la docstring), et testez :
   ```bash
   python -m scripts.intent lyon               # le site relu dans NetBox, au format YAML
   python -m scripts.intent lyon --compare     # attendu : OK … exactement le même site
   ```
   Si ce n'est pas `OK`, la commande affiche la partie qui diffère (YAML d'un côté, NetBox de l'autre). Faites ensuite `mars` et `pars`.
3. Générez les configurations **depuis NetBox** et vérifiez qu'elles sont identiques à celles générées depuis les YAML :
   ```bash
   python -m scripts.render && rm -rf /tmp/yaml && cp -r config /tmp/yaml   # depuis les YAML (TP-02)
   python -m scripts.render_netbox                                       # depuis NetBox
   diff -r /tmp/yaml config && echo "Aucune différence"
   ```
   👀 **Lisez** `scripts/render_netbox.py` : il ne fait que quelques lignes. **(c'est ce rendu que la dérive et le workflow utiliseront au TP-06)**

### Comprendre
- Pourquoi les templates n'ont-ils pas eu à changer ? (séparation données / logique)
- `_vlans()` reçoit `routers` en paramètre : à quoi sert-il pour Paris, qui n'a qu'un routeur et donc pas d'IP VRRP ?

---

## Module 5 — Modifier NetBox, voir le réseau suivre

**Objectif** : à la fin, j'ai fait un changement **dans NetBox** et je l'ai déployé avec Nornir, sans toucher à aucun fichier :
NetBox donne **quoi** pousser (l'intention, module 4) et **où** le pousser (l'inventaire).

Au TP-04, Nornir trouvait les équipements dans `inventory/hosts.yaml` : un équipement ajouté, retiré ou réadressé
obligeait à modifier ce fichier à la main. Ici, Nornir lit son inventaire **dans NetBox, à chaque lancement**.

### Découvrir
1. 👀 **Comparez** `inventory/config_netbox.yaml` et `inventory/config.yaml` (TP-04) : qu'est-ce qui remplace `hosts.yaml` et `groups.yaml` ?
2. 👀 **Lisez** la partie fournie de `scripts/nornir_netbox.py` : `init_nornir_netbox()`, `show_inventory()` et `deploy_config()`.
3. Affichez l'inventaire que Nornir trouve dans NetBox :
   ```bash
   python -m scripts.nornir_netbox
   ```
   - D'où viennent l'IP de connexion de chaque équipement, et sa plateforme ?
   - `site` et `rôle` ne sont plus des chaînes, mais les objets NetBox. Pour le voir :
     ```bash
     python -c "from scripts.nornir_netbox import init_nornir_netbox; print(init_nornir_netbox().inventory.hosts['R1-LYON']['site'])"
     ```

### Construire
4. Complétez `site_devices()` puis `deploy_site()` dans `scripts/nornir_netbox.py`.
5. **Dans l'interface de NetBox**, faites ces deux changements :
   - la priorité VRRP de R2-LYON passe à **120**, dans les groupes du VLAN 10 et du VLAN 20 (*IPAM › FHRP Groups › CPE-LYON VLAN 10*, onglet des affectations) ;
   - le VLAN 20 de Lyon reçoit une description : `VLAN etudiants Lyon` (*IPAM › VLANs*).
6. Voyez l'écart avec vos anciens fichiers, puis ce qui changerait sur les équipements :
   ```bash
   python -m scripts.intent lyon --compare        # l'intention a changé par rapport à data/lyon.yaml
   python -m scripts.nornir_netbox lyon --dry-run # les diffs, sans rien appliquer
   ```
   Quels équipements sont concernés ? Pourquoi le switch n'affiche-t-il pas de diff ?
7. Déployez : `python -m scripts.nornir_netbox lyon`, puis sur R2-LYON : `show vrrp brief`. Qui est maître ? Pourquoi ?

### L'inventaire suit NetBox
8. Dans NetBox, passez R2-LYON en statut **Offline** (*Devices › R2-LYON › Edit*), puis relancez `python -m scripts.nornir_netbox` : R2-LYON n'est plus dans l'inventaire, et vous n'avez touché à aucun fichier. 👀 Quelle ligne de `inventory/config_netbox.yaml` produit cet effet ?
9. Toujours avec R2-LYON hors service, remettez sa priorité à **100** dans NetBox et redéployez Lyon. Puis `show vrrp brief` sur les deux routeurs : qui est maître ? Est-ce ce que dit NetBox ?
10. Repassez R2-LYON en **Active** et redéployez Lyon : R1-LYON redevient maître. À la fin, **NetBox et le réseau disent la même chose** (le TP-06 commence par le vérifier).

### Comprendre
- Dans le *Changelog* de NetBox, retrouvez vos changements : qui, quand, quoi. Qu'apporte cet historique par rapport à un fichier YAML modifié à la main ?
- Le diff NAPALM ne contient que vos changements, pas toute la configuration : pourquoi ?
- À l'étape 9, NetBox et R2-LYON ne disaient plus la même chose. Dans quel cas réel mettrait-on un équipement hors service dans NetBox ? Comment détecter cet écart sans tout relire à la main ? **(c'est la dérive, au TP-06)**

✅ **Point de contrôle** : montrez le Changelog, le dry-run et `show vrrp brief`.

---

✅ **Fin de séance** : `git commit -m "TP5 : NetBox source de vérité"` puis `git push`.
