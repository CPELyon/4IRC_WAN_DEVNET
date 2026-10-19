# TP-01 — Décrire le réseau

> L'intention, c'est l'**état voulu** du réseau, décrit de façon structurée et indépendante du constructeur.
> Aujourd'hui, vous configurez un site à la main… puis vous le décrivez en données.

| Module | Objectif |
|---|---|
| 1. Configurer Lyon à la main | VLAN, trunk, inter-VLAN, VRRP sur le siège |
| 2. Décrire Lyon en YAML | Passer de la configuration aux données |
| 3. Lire et parcourir le YAML en Python | Charger l'intention et en afficher un résumé |

Avant de commencer : le [TP-00](../TP-00/README.md) est terminé (VS Code connecté à la VM, votre dépôt GitHub relié à celui de l'enseignant), et vous avez lu [docs/maquette.md](../docs/maquette.md) (topologie, adresses, identifiants).

---

## Module 1 — Configurer Lyon à la main

**Objectif** : à la fin, les PC des VLAN 10 et 20 de Lyon communiquent, et la passerelle survit à la panne de R1.

Le VLAN 99 (administration) et les trunks vers les routeurs sont **déjà configurés** : n'y touchez pas.

### Construire
1. **ESW-LYON** : créez les VLAN 10 (`teacher`) et 20 (`student`), puis mettez f1/2 en accès VLAN 10 et f1/3 en accès VLAN 20.
   ```
   vlan 10
    name teacher
   vlan 20
    name student
   exit
   ```
2. **R1-LYON et R2-LYON** : créez les sous-interfaces `GigabitEthernet0/0.10` et `.20` (encapsulation dot1Q).
   - R1 : 172.16.10.252/24 et 172.16.20.252/24 ; R2 : .253.
3. Ajoutez le **VRRP** : groupe = numéro de VLAN, IP virtuelle .254, R1 priorité 110 + preempt, R2 priorité 100.
4. **Notez chaque commande tapée** dans un fichier `TP-01/notes-lyon.txt`, équipement par équipement.

### Vérifier
- `show vlan-switch brief` sur ESW-LYON, `show vrrp brief` sur R1 et R2 (R1 Master, R2 Backup).
- Depuis PC-LYON-10 : `ping 172.16.10.254`, puis `ping 172.16.20.1`.
- **Test de bascule** : `shutdown` sur g0/0 de R1-LYON. Le ping continue-t-il ? Qui est Master ? Remettez `no shutdown` : que se passe-t-il, et pourquoi (preempt) ?

### Comprendre
- Dans vos notes, quelles lignes sont **identiques** sur R1 et R2 ? Lesquelles **changent** ?
- Combien de lignes faudrait-il taper pour Marseille et Paris ? Et pour 50 sites ?


---

## Module 2 — Décrire Lyon en YAML

**Objectif** : à la fin, la configuration de Lyon est décrite dans `data/lyon.yaml`, sans aucune syntaxe Cisco.

### Découvrir
1. Ouvrez `data/cores.yaml` et `templates/core_router.j2` : repérez ce qui est **donnée** (dans le YAML) et ce qui est **syntaxe** (dans le template).
   - 👀 **Lisez** `scripts/render_core.py`, puis lancez-le : `python -m scripts.render_core`. Repérez la ligne `template.render(...)` : quelles données reçoit le template, et sous quels noms ? **(c'est ce que vous écrirez au TP-02 pour vos sites)**

### Construire
2. A partir des configuration que vous avez mises en place, identifier les variables par un champ `{{nom_de_la_variable}}` et créer le fichier `data/lyon.yaml` qui représente ces variables.
3. Comparez avec le modèle de référence du projet : [docs/modele-donnees.md](../docs/modele-donnees.md). Notez les différences.
4. Écrivez `data/lyon.yaml` en suivant le modèle de référence (il sera utilisé par les tests à partir du TP-02).
5. Vérifiez la syntaxe : `yamllint data/lyon.yaml`.

### Comprendre
- Pourquoi ne pas stocker `vrrp: true` ? Pourquoi ne pas répéter le groupe VRRP ?
- Pourquoi le VLAN 99 n'apparaît-il pas dans vos données ?
- Écrivez la même information en JSON (`data/lyon.json`, juste les VLANs) : lequel est le plus lisible ?

### Aller plus loin
- Écrivez dès maintenant `data/mars.yaml` et `data/pars.yaml` (voir le plan d'adressage). Attention : Paris n'a qu'un routeur.

---

## Module 3 — Lire et parcourir le YAML en Python

**Objectif** : à la fin, un script affiche le résumé d'un site à partir de son fichier YAML.

### Construire
1. Complétez `load_yaml()` dans `scripts/utils.py` : gérez le fichier introuvable et le YAML invalide.
   - 👀 **Lisez** la partie « fourni » de `scripts/utils.py` : que renvoient `ip_addr`, `netmask`, `wildcard` et `network` pour `172.16.10.252/24` ? Pourquoi suffit-il alors de stocker une seule valeur par IP dans le YAML ? **(ces filtres servent dans tous vos templates, dès le TP-02)**
2. Complétez `summarize()` dans `scripts/tp1_summary.py`.
   - 👀 **Lisez** le `__main__` de `scripts/tp1_summary.py` : d'où vient `sys.argv[1]`, et que se passe-t-il si on ne donne pas de fichier ? **(tous les scripts du projet prennent leurs arguments ainsi)**
3. Lancez : `python -m scripts.tp1_summary data/lyon.yaml`.

### Découvrir
- Avant de coder, explorez : `print(type(site))`, `print(site.keys())`, `print(site["vlans"][0])`.

### Vérifier
- Le résumé affiche 2 VLANs, 3 équipements, VRRP : oui.
- Testez avec un fichier qui n'existe pas, puis avec un YAML volontairement cassé : le script doit afficher un message clair, pas une trace d'erreur.

### Comprendre
- Votre script fonctionne-t-il sur Marseille sans modification ? Et sur Paris ? Pourquoi ?

✅ **Fin de séance** : `git add data scripts TP-01 && git commit -m "TP1 : Lyon décrit en YAML" && git push`.
