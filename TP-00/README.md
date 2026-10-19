# TP-00 — Préparer son environnement

> À la fin de la préparation, la maquette tourne dans GNS3, la VM DEVNET y est branchée, et vous vous connectez
> à la VM en SSH depuis votre PC, VS Code travaille dans la VM et votre dépôt Git est prêt. Le TP-01 commence directement par la configuration du site de Lyon.

**Matériel** : un PC avec 16 Go de RAM (la maquette en prend environ 4 Go, la VM 4 Go) et 20 Go de disque libre.

---

## 1. Installer les logiciels

1. **VirtualBox** : https://www.virtualbox.org (version standard).
2. **GNS3 2.2.49** : https://www.gns3.com, version « all-in-one ». Gardez les options par défaut (Npcap compris sous Windows).
   Au premier lancement, choisissez **« Run appliances on my local computer »** (pas de GNS3 VM).
3. **VS Code** : https://code.visualstudio.com (l'extension Remote - SSH s'installe à l'étape 5.2).
4. **Client SSH** : déjà présent sous Windows 10/11, macOS et Linux. Vérifiez dans un terminal : `ssh -V`.


## 2. Importer la VM et la maquette

> ⚠️ Ne démarrez pas la VM depuis VirtualBox ⚠️
1. **La VM** : VirtualBox › **Fichier › Importer un appareil virtuel** › `devnet.ova` (lien sur e-campus).

   Tout est déjà réglé dans la VM : la carte n°1 en NAT avec l'accès depuis votre PC (SSH sur le port 2222, NetBox sur le port 8000), la carte n°2 prête pour GNS3.

2. **La maquette** : GNS3 › **File › Import portable project** › `4IRC_WAN_DEVNET.gns3project` (lien sur e-campus).

## 3. Brancher la VM sur la maquette

1. GNS3 › **Edit › Preferences › VirtualBox › VirtualBox VMs › New** › choisissez `devnet`.
2. Sélectionnez-la › **Edit** › onglet **Network** : **Adapters = 2**.
3. Glissez la VM dans le projet, près du NOC, puis câblez son interface **e1** sur **ESW-NOC fa1/3**.
   L'interface e0 reste en NAT : c'est elle qui donne Internet à la VM et l'accès SSH depuis votre PC.
4. Démarrez **tous** les équipements (▶ vert), y compris la VM, puis attendez 2 minutes.

> ⚠️ Démarrez toujours la VM **depuis GNS3**, jamais directement depuis VirtualBox.

## 4. Vérifier

Depuis un terminal de votre PC :

```bash
ssh -p 2222 cpe@127.0.0.1        # mot de passe : 123
```

Puis, dans la VM :

```bash
devnet-check
```

Toutes les lignes doivent afficher **OK** (R1-LYON répond une fois la maquette démarrée). Testez aussi l'accès à un routeur :
`ssh cisco@172.16.100.126` (mot de passe `cisco`) doit afficher le prompt `R1-LYON#`.

Un test échoue ? Notez lequel et le message d'erreur, et prévenez l'intervenant.

## 5. Mettre en place son poste

**Objectif** : à la fin, VS Code travaille dans la VM, et mon dossier de travail est relié au dépôt de l'enseignant (pour récupérer) et à mon dépôt privé (pour enregistrer).

### 5.1 Se connecter à la VM sans mot de passe
1. Depuis un terminal de votre PC, générez une paire de clés SSH :
   ```bash
   ssh-keygen -t ed25519 -C "prenom.nom@cpe.fr"
   ```
2. Copiez la clé publique dans la VM :
   - **Windows (PowerShell)** :
     ```powershell
     type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -p 2222 cpe@127.0.0.1 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
     ```
   - **Linux / macOS** : `ssh-copy-id -p 2222 cpe@127.0.0.1`
3. Ajoutez un raccourci dans le fichier `~/.ssh/config` de votre PC (`C:\Users\<vous>\.ssh\config` sous Windows) :
   ```
   Host devnet
       HostName 127.0.0.1
       Port 2222
       User cpe
   ```
   Testez : `ssh devnet` se connecte **sans mot de passe**.

### 5.2 Ouvrir son espace de travail dans VS Code

4. Sur votre PC, ouvrez VS Code et installez l'extension **Remote - SSH** :
   onglet **Extensions** à gauche (ou Ctrl+Shift+X) › tapez `Remote - SSH` › choisissez celle de **Microsoft** (identifiant `ms-vscode-remote.remote-ssh`) › **Install**.
   Une fois installée, une icône **><** apparaît tout en bas à gauche de la fenêtre.
5. Cliquez sur l'icône **><** (Open a Remote Window) › **Connect to Host…** › `devnet`.
   Une nouvelle fenêtre s'ouvre ; la première fois, VS Code installe son serveur dans la VM (≈ 1 min).
   Vérifiez en bas à gauche : **SSH: devnet** doit s'afficher. Tout ce que vous faites dans cette fenêtre se passe **dans la VM**.
6. Ouvrez un terminal dans la VM : menu **Terminal › New Terminal**. Créez le dossier du projet :
   ```bash
   mkdir -p ~/4IRC_WAN_DEVNET_NOM_PRENOM      # remplacez NOM_PRENOM par vos nom et prénom, ex. DUPONT_MARIE
   ```
7. Ouvrez ce dossier comme espace de travail : **File › Open Folder…** › `/home/cpe/4IRC_WAN_DEVNET_NOM_PRENOM` › **OK**.
   Si VS Code demande « Do you trust the authors… ? », répondez **Yes**.
   À partir de maintenant, ouvrez toujours ce dossier (**File › Open Recent**) : l'explorateur à gauche montre vos fichiers, le terminal s'ouvre dans le projet.
8. Installez les extensions utiles **dans la VM** : onglet Extensions (Ctrl+Shift+X) › cherchez **Python** (Microsoft) puis **YAML** (Red Hat) › **Install in SSH: devnet**.

### 5.3 Configurer Git

9. Dans le terminal de VS Code, donnez votre identité à Git (une seule fois) :
   ```bash
   git config --global user.name "Prénom Nom"
   git config --global user.email "prenom.nom@cpe.fr"
   git config --global init.defaultBranch main
   git config --global pull.rebase false     # git pull fusionne (merge) au lieu de refuser
   ```

### 5.4 Créer son dépôt sur GitHub

10. Sur https://github.com, cliquez sur **+** en haut à droite › **New repository**, puis remplissez :
    - **Repository name** : `4IRC_WAN_DEVNET_NOM_PRENOM`, avec **votre** nom puis votre prénom, en majuscules, sans accent ni espace (ex. `4IRC_WAN_DEVNET_DUPONT_MARIE`) : l'intervenant retrouve ainsi chaque dépôt d'un coup d'œil
    - visibilité : **Private**
    - n'ajoutez **ni README, ni .gitignore, ni licence** (laissez ces options désactivées ou sur « None ») : le dépôt doit être **vide**
    - cliquez sur **Create repository**. Gardez la page qui s'affiche ouverte : elle donne l'URL du dépôt (boutons **HTTPS** / **SSH**)
11. Dans votre dépôt : **Settings** (onglet sous le nom du dépôt) › section **Access** › **Collaborators** › **Add people** › tapez **coublece** › cliquez sur le nom proposé › bouton **Add coublece to …** (suivi du nom de votre dépôt). L'intervenant reçoit une invitation par mail.
12. Choisissez **comment Git s'authentifie** auprès de GitHub (une seule des deux options) :

    | | Option A — HTTPS + jeton | Option B — SSH |
    |---|---|---|
    | Principe | Un jeton d'accès personnel (PAT), utilisé comme mot de passe | Une clé SSH de la VM, déclarée sur GitHub |
    | URL de votre dépôt | `https://github.com/<vous>/4IRC_WAN_DEVNET_NOM_PRENOM.git` | `git@github.com:<vous>/4IRC_WAN_DEVNET_NOM_PRENOM.git` |
    | Avantage | Passe partout, même si le port 22 est filtré | Rien à retaper, aucun secret dans un fichier |

    **Option A — HTTPS + jeton**
    - Cliquez sur votre photo de profil (en haut à droite) › **Settings** › tout en bas du menu de gauche, **Developer settings** › **Personal access tokens** › **Fine-grained tokens** › **Generate new token**.
    - **Token name** : `devnet` ; **Expiration** : la fin du module ; **Resource owner** : votre compte.
    - **Repository access** : **Only select repositories**, puis choisissez `4IRC_WAN_DEVNET_NOM_PRENOM` dans la liste.
    - **Permissions** › permissions du dépôt (*Repository permissions*) : ajoutez **Contents** avec l'accès **Read and write**, et **Workflows** en **Read and write** (utile à la séance 6). *Metadata* en lecture seule est ajouté automatiquement.
    - **Generate token**, puis copiez le jeton tout de suite (il ne sera plus affiché). Dans la VM :
      ```bash
      git config --global credential.helper store   # le jeton sera mémorisé dans ~/.git-credentials
      ```
      Au premier `git push`, Git demande un identifiant (votre login GitHub) et un mot de passe : **collez le jeton**.
    - Si VS Code propose de « se connecter avec GitHub » au moment du push, vous pouvez accepter : c'est une autre façon de faire du HTTPS.

    **Option B — SSH**
    - Dans la VM, créez une clé et affichez sa partie publique :
      ```bash
      ssh-keygen -t ed25519 -C "prenom.nom@cpe.fr"     # Entrée à chaque question
      cat ~/.ssh/id_ed25519.pub                         # copiez toute la ligne affichée
      ```
    - Sur GitHub : photo de profil › **Settings** › section **Access** › **SSH and GPG keys** › **New SSH key** ;
      **Title** : `VM devnet` ; **Key type** : **Authentication Key** ; **Key** : collez la ligne ; **Add SSH key** (GitHub peut redemander votre mot de passe).
    - Testez depuis la VM :
      ```bash
      ssh -T git@github.com                             # répondez yes, puis : « Hi <vous>! »
      ```

### 5.5 Récupérer le dépôt de l'enseignant et le relier au vôtre

Votre dossier local va être relié à **deux** dépôts distants :

| Nom du remote | Dépôt | Usage |
|---|---|---|
| `upstream` | `CPELyon/4IRC_WAN_DEVNET` (l'enseignant, public) | Vous **récupérez** (pull) les sujets et le code fourni |
| `origin` | `<vous>/4IRC_WAN_DEVNET_NOM_PRENOM` (le vôtre, privé) | Vous **enregistrez** (push) votre travail |

13. Dans le terminal de VS Code, transformez le dossier (encore vide) en dépôt Git et récupérez le dépôt de l'enseignant :
    ```bash
    cd ~/4IRC_WAN_DEVNET_NOM_PRENOM
    git init
    git remote add upstream https://github.com/CPELyon/4IRC_WAN_DEVNET.git
    git pull upstream main
    ls                                         # README.md, TP-00, TP-01, data, docs, scripts, templates…
    ```
    Les fichiers apparaissent aussi dans l'explorateur de VS Code, à gauche.
14. Reliez ce dossier à **votre** dépôt GitHub (`origin`) et poussez-y le contenu, sans rien modifier :
    ```bash
    git remote add origin <URL de votre dépôt, HTTPS ou SSH selon votre option>
    git push -u origin main
    git remote -v                              # origin = vous, upstream = l'enseignant
    ```
    Rechargez la page de votre dépôt sur GitHub : il contient maintenant les mêmes fichiers que celui de l'enseignant.

    Au début de chaque séance, vous récupérerez la suite avec `git pull --no-edit upstream main`, puis `git push`.

### 5.6 Préparer Python et lancer l'exemple

15. Créez l'environnement Python du projet et installez les bibliothèques :
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate                  # le prompt commence par (.venv)
    pip install -r requirements.txt
    ```
    Dans VS Code : **Ctrl+Shift+P › Python: Select Interpreter** › choisissez `./.venv/bin/python`.
    Le dossier `.venv` n'est pas versionné : il est listé dans `.gitignore`.
16. Lancez l'exemple fourni : `python -m scripts.render_core`. Il affiche la configuration du cœur, générée à partir de `data/cores.yaml`.

### Vérifier
- `git remote -v` affiche **deux** remotes : `origin` (votre dépôt) et `upstream` (CPELyon).
- Sur GitHub, votre dépôt privé contient les mêmes fichiers que celui de l'intervenant.
- Depuis la VM : `ping 172.16.100.62` (passerelle du NOC), puis `ssh cisco@172.16.100.126` (R1-LYON).

---

### Problèmes fréquents

- **`ssh -p 2222` refusé** : la VM n'a pas fini de démarrer (attendez 1 minute), ou elle a été lancée depuis VirtualBox au lieu de GNS3.
- **La VM ne démarre pas depuis GNS3** : vérifiez qu'elle est arrêtée dans VirtualBox, puis relancez-la depuis GNS3.
- Pour tout autre problème, sollicitez l'intervenant.
