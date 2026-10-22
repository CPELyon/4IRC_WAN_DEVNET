# TP-03 — Appliquer l'état voulu

**Bloc NAF : Exécuteur** · Séance 3 · Avant de commencer : `git pull --no-edit upstream main`

> L'exécuteur applique les changements sur le réseau, guidé par l'intention. Le NAF lui demande de parler
> les interfaces d'écriture (ici SSH), de proposer un **dry-run**, d'être **transactionnel** et **idempotent**.
> Aujourd'hui, vous comparez deux exécuteurs : Netmiko (impératif) et NAPALM (déclaratif).

| Module | Objectif |
|---|---|
| 1. Netmiko : premiers pas | Se connecter et lire une commande |
| 2. Netmiko : déployer Paris | Pousser la config générée et sauvegarder |
| 3. NAPALM : changer Marseille | Diff avant d'appliquer, commit, rollback |
| 4. Comparer les deux approches | Savoir quand utiliser l'un ou l'autre |

Pré-requis : `config/R1-PARS.cfg`, `config/ESW-PARS.cfg` et les configs de Marseille générées au TP-02.
Variables d'environnement : `export NET_USER=cisco NET_PASSWORD=cisco`.

---

## Module 1 — Netmiko : premiers pas

**Objectif** : à la fin, je lis l'état d'un équipement depuis Python.

### Construire
1. Complétez `connect()` et `show()` dans `scripts/deploy_netmiko.py`.
   - 👀 **Lisez** `get_credentials()` dans `scripts/utils.py` : d'où viennent l'identifiant et le mot de passe ? Pourquoi ne jamais les écrire dans le code ? *(Nornir au TP-04 et le jeton NetBox au TP-05 suivent la même règle)*
2. Utiliser ces fonction pour vous connectez à R1-PARS (172.16.100.254) et affichez `show ip interface brief`.

### Découvrir
- `print(type(conn))`, puis `print(conn.find_prompt())`.
- Affichez `show running-config | section interface`. Quel est le type de la sortie ?

---

## Module 2 — Netmiko : déployer Paris

**Objectif** : à la fin, Paris fonctionne, configuré par mon script, et sauvegardé.

### Construire
1. Complétez `deploy_file()` : `send_config_from_file()` puis `save_config()`.
2. Complétez `backup()` : `show running-config` écrit dans `backups/<hostname>-avant.cfg` ou `backups/<hostname>-apres.cfg`. (utiliser la fonction save_text qui est prévu pour ça)
3. Complétez le `__main__` : sauvegarde avant, déploiement de `config/<hostname>.cfg` pour ESW-PARS puis R1-PARS, sauvegarde après.
4. Lancez : `python -m scripts.deploy_netmiko`.

### Vérifier
- PC-PARS-10 joint 172.16.50.254 et PC-PARS-20.
- `backups/` contient `R1-PARS-avant.cfg` et `R1-PARS-apres.cfg` (idem pour ESW-PARS) : comparez-les avec `diff`.
- **Relancez le script une deuxième fois.** Que renvoie Netmiko ? Les commandes ont-elles été renvoyées ?

### Comprendre
- Si une commande échoue au milieu du fichier, dans quel état est l'équipement ?
- Netmiko sait-il ce qui va changer **avant** d'envoyer les commandes ?

✅ **Point de contrôle** : faites constater Paris fonctionnel et vos sauvegardes.

---

## Module 3 — NAPALM : changer Marseille

**Objectif** : à la fin, je modifie un équipement en voyant le diff avant de valider, et je sais revenir en arrière.

### Découvrir
👀 **Lisez** le dictionnaire `MARS` et le `__main__` de `scripts/deploy_napalm.py` : la liste des équipements et leurs IP sont écrites à la main. Quel problème cela pose-t-il pour 50 sites ? **(l'inventaire Nornir du TP-04 répond à cette question)**

1. Complétez `open_device()` dans `scripts/deploy_napalm.py`, puis affichez `device.get_facts()` pour R1-MARS : comparez avec la sortie texte de Netmiko.

### Construire
2. Dans `data/mars.yaml`, ajoutez une description aux VLANs (et le template correspondant), régénérez `ESW-MARS.cfg`, `R1-MARS.cfg` et `R2-MARS.cfg`
3. Complétez `preview()` : `load_merge_candidate(filename=...)` puis `compare_config()` : c'est le **dry-run**.
4. Complétez `apply()` : diff vide → rien à faire ; sinon confirmation puis `commit_config()`, ou `discard_config()`.
5. Appliquez sur R1-MARS et R2-MARS.

### Vérifier
- Relancez `apply()` sur R1-MARS : le diff doit être **vide** (idempotence).
- **Erreur volontaire** : mettez une mauvaise IP virtuelle VRRP dans les données, appliquez, constatez la panne.
  Pour revenir en arrière, 👀 **lisez** `rollback()` (fournie) dans `scripts/deploy_napalm.py` et appelez-la en première ligne
  du `__main__`, puis lancez `python -m scripts.deploy_napalm R1-MARS --rollback`. Le service revient-il ?

### Comprendre
- Que montre exactement `compare_config()` ? Que faut-il activer sur l'équipement pour que NAPALM fonctionne (archive, SCP) ?

### Aller plus loin
- Déployez ESW-MARS avec NAPALM : que se passe-t-il ? (Les getters et le merge sont-ils disponibles sur ce switch ?)

✅ **Fin de séance** : `git commit -m "TP3 : exécuteurs Netmiko et NAPALM"` puis `git push`.
