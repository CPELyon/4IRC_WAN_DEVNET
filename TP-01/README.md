# TP-01 — Décrire le réseau

**Bloc NAF : Intention** · Séance 1 · ≈ 3 h

> L'intention, c'est l'**état voulu** du réseau, décrit de façon structurée et indépendante du constructeur.
> Aujourd'hui, vous configurez un site à la main… puis vous le décrivez en données.

| Module | Durée | Objectif |
|---|---|---|
| 1. Mettre en place son poste | 45 min | Travailler dans la VM depuis VS Code, avec Git |
| 2. Configurer Lyon à la main | 1 h 15 | VLAN, trunk, inter-VLAN, VRRP sur le siège |
| 3. Décrire Lyon en YAML | 45 min | Passer de la configuration aux données |
| 4. Lire et parcourir le YAML en Python | 30 min | Charger l'intention et en afficher un résumé |

Avant de commencer : lisez [docs/maquette.md](../docs/maquette.md) (topologie, adresses, identifiants).

---

## Module 1 — Mettre en place son poste (45 min)

**Objectif** : à la fin, je code dans la VM depuis VS Code et j'enregistre mon travail dans Git.

### Découvrir
1. Pré-requis : le [TP-00](../TP-00/README.md) est fait. Démarrez la maquette et la VM **depuis GNS3**, et vérifiez `ssh -p 2222 cpe@127.0.0.1`.
2. Depuis un terminal de votre PC, générez une paire de clés SSH :
   ```bash
   ssh-keygen -t ed25519 -C "prenom.nom@cpe.fr"
   ```
3. Copiez la clé publique dans la VM :
   - **Windows (PowerShell)** :
     ```powershell
     type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -p 2222 cpe@127.0.0.1 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
     ```
   - **Linux / macOS** : `ssh-copy-id -p 2222 cpe@127.0.0.1`
4. Ajoutez un raccourci dans le fichier `~/.ssh/config` de votre PC (`C:\Users\<vous>\.ssh\config` sous Windows) :
   ```
   Host devnet
       HostName 127.0.0.1
       Port 2222
       User cpe
   ```
   Testez : `ssh devnet` se connecte **sans mot de passe**.

### Construire
5. Dans VS Code (extension **Remote - SSH** installée au TP-00) : `F1 › Remote-SSH: Connect to Host… › devnet`.
6. Sur GitHub, créez **votre** dépôt `4IRC_WAN_DEVNET` : **privé**, **vide** (sans README, sans .gitignore, sans licence). Dans Settings › Collaborators, ajoutez l'enseignant.
7. Choisissez **comment Git s'authentifie** auprès de GitHub pour pousser sur votre dépôt (une seule des deux options) :

   | | Option A — SSH | Option B — HTTPS + jeton |
   |---|---|---|
   | Principe | Une clé SSH de la VM, déclarée sur GitHub | Un jeton d'accès personnel (PAT), utilisé comme mot de passe |
   | URL de votre dépôt | `git@github.com:<vous>/4IRC_WAN_DEVNET.git` | `https://github.com/<vous>/4IRC_WAN_DEVNET.git` |
   | Avantage | Rien à retaper, aucun secret dans un fichier | Passe partout, même si le port 22 est filtré |

   **Option A — SSH**
   ```bash
   ssh-keygen -t ed25519 -C "prenom.nom@cpe.fr"     # dans la VM, Entrée à chaque question
   cat ~/.ssh/id_ed25519.pub                         # à copier dans GitHub › Settings › SSH and GPG keys › New SSH key
   ssh -T git@github.com                             # doit répondre « Hi <vous>! »
   ```

   **Option B — HTTPS + jeton**
   - GitHub › Settings › Developer settings › Personal access tokens › **Fine-grained tokens** › Generate new token.
   - *Repository access* : **Only select repositories** › `4IRC_WAN_DEVNET` ; *Permissions* : **Contents** en *Read and write* (et **Workflows** en *Read and write*, utile à la séance 6) ; expiration : la fin du module.
   - Copiez le jeton tout de suite (il ne sera plus affiché), puis, dans la VM :
     ```bash
     git config --global credential.helper store   # le jeton sera mémorisé dans ~/.git-credentials
     ```
     Au premier `git push`, Git demande un identifiant (votre login GitHub) et un mot de passe : **collez le jeton**.
   - Si VS Code propose de « se connecter avec GitHub » au moment du push, vous pouvez accepter : c'est une autre façon de faire du HTTPS.

8. Dans la VM, clonez le dépôt de l'enseignant (public, aucune authentification), puis branchez-le sur le vôtre :
   ```bash
   git clone https://github.com/CPELyon/4IRC_WAN_DEVNET.git
   cd 4IRC_WAN_DEVNET
   git remote rename origin upstream        # upstream = le dépôt de l'enseignant (lecture seule)
   git remote add origin <URL de votre dépôt, SSH ou HTTPS selon votre option>   # origin = votre dépôt
   git push -u origin main
   git remote -v                            # vérifiez : deux remotes
   git config --global pull.rebase false    # git pull fusionne (merge) au lieu de refuser
   ```
   Pas encore d'identité Git ? `git config --global user.name "Prénom Nom"` et `git config --global user.email "prenom.nom@cpe.fr"`.
9. Installez l'environnement Python :
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
10. Lancez l'exemple fourni : `python -m scripts.render_core`. Il affiche la configuration du cœur, générée à partir de `data/cores.yaml`.

### Vérifier
- Depuis la VM : `ping 172.16.100.62` (passerelle du NOC), puis `ssh cisco@172.16.100.126` (R1-LYON).
- Faites un premier commit : ajoutez votre nom dans un fichier `MEMBRES.md`, `git add`, `git commit`, `git push`.

### Comprendre
- Pourquoi la clé privée ne doit-elle jamais quitter votre PC ?
- SSH ou jeton HTTPS : que se passe-t-il si votre clé ou votre jeton fuit ? Comment le révoquer ?
- À quoi servent `origin` et `upstream` ? Que fera `git pull --no-edit upstream main` au début de la séance 2 ?
- Le code s'exécute-t-il sur votre PC ou sur la VM ? Comment le savez-vous dans VS Code ?

✅ **Point de contrôle** : faites vérifier votre `git remote -v`, votre `git log` et une session SSH vers R1-LYON.

---

## Module 2 — Configurer Lyon à la main (1 h 15)

**Objectif** : à la fin, les PC des VLAN 10 et 20 de Lyon communiquent, et la passerelle survit à la panne de R1.

Le VLAN 99 (administration) et les trunks vers les routeurs sont **déjà configurés** : n'y touchez pas.

### Construire
1. **ESW-LYON** : créez les VLAN 10 (`teacher`) et 20 (`student`), puis mettez f1/2 en accès VLAN 10 et f1/3 en accès VLAN 20.
   ```
   vlan database
    vlan 10 name teacher
    vlan 20 name student
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

✅ **Point de contrôle** : faites constater le test de bascule.

---

## Module 3 — Décrire Lyon en YAML (45 min)

**Objectif** : à la fin, la configuration de Lyon est décrite dans `data/lyon.yaml`, sans aucune syntaxe Cisco.

### Découvrir
1. Ouvrez `data/cores.yaml` et `templates/core_router.j2` : repérez ce qui est **donnée** (dans le YAML) et ce qui est **syntaxe** (dans le template).

### Construire
2. Sur papier (10 min) : proposez une structure de données pour un site. De quoi a-t-on besoin pour reconstruire tout ce que vous avez tapé au module 2 ?
3. Comparez avec le modèle de référence du projet : [docs/modele-donnees.md](../docs/modele-donnees.md). Notez les différences.
4. Écrivez `data/lyon.yaml` en suivant le modèle de référence (il sera utilisé par les tests à partir du TP-02).
5. Vérifiez la syntaxe : `yamllint data/lyon.yaml`.

### Comprendre
- Pourquoi ne pas stocker `vrrp: true` ? Pourquoi ne pas répéter le groupe VRRP ?
- Pourquoi le VLAN 99 n'apparaît-il pas dans vos données ?
- Écrivez la même information en JSON (`data/lyon.json`, juste les VLANs) : lequel est le plus lisible ?

### Aller plus loin
- Écrivez dès maintenant `data/marseille.yaml` et `data/paris.yaml` (voir le plan d'adressage). Attention : Paris n'a qu'un routeur.

---

## Module 4 — Lire et parcourir le YAML en Python (30 min)

**Objectif** : à la fin, un script affiche le résumé d'un site à partir de son fichier YAML.

### Construire
1. Complétez `load_yaml()` dans `scripts/utils.py` : gérez le fichier introuvable et le YAML invalide.
2. Complétez `summarize()` dans `scripts/tp1_summary.py`.
3. Lancez : `python -m scripts.tp1_summary data/lyon.yaml`.

### Découvrir
- Avant de coder, explorez : `print(type(site))`, `print(site.keys())`, `print(site["vlans"][0])`.

### Vérifier
- Le résumé affiche 2 VLANs, 3 équipements, VRRP : oui.
- Testez avec un fichier qui n'existe pas, puis avec un YAML volontairement cassé : le script doit afficher un message clair, pas une trace d'erreur.

### Comprendre
- Votre script fonctionne-t-il sur Marseille sans modification ? Et sur Paris ? Pourquoi ?

✅ **Fin de séance** : `git add data scripts TP-01 && git commit -m "TP1 : Lyon décrit en YAML" && git push`.
