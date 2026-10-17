# TP-00 — Préparer son environnement

**À faire avant la séance 1** · ≈ 45 min · Lisible directement sur GitHub, aucun outil requis

> À la fin de ce TP, la maquette tourne dans GNS3, la VM DEVNET y est branchée, et vous vous connectez
> à la VM en SSH depuis votre PC. La séance 1 commence directement par Git et VS Code (TP-01).

**Matériel** : un PC avec 16 Go de RAM (la maquette en prend environ 4 Go, la VM 4 Go) et 20 Go de disque libre.

**Fournis par l'enseignant** : la VM `devnet-v4.ova` et la maquette `CPE-NET-fil-rouge.gns3project`.

| Étape | Durée |
|---|---|
| 1. Installer les logiciels | 15 min |
| 2. Déclarer les images IOS | 10 min |
| 3. Importer la VM et la maquette | 10 min |
| 4. Brancher la VM sur la maquette | 5 min |
| 5. Vérifier | 5 min |

---

## 1. Installer les logiciels (15 min)

1. **VirtualBox** : https://www.virtualbox.org (version standard).
2. **GNS3 2.2.49** : https://www.gns3.com, version « all-in-one ». Gardez les options par défaut (Npcap compris sous Windows).
   Au premier lancement, choisissez **« Run appliances on my local computer »** (pas de GNS3 VM).
3. **VS Code** : https://code.visualstudio.com, puis l'extension **Remote - SSH** (Microsoft).
4. **Client SSH** : déjà présent sous Windows 10/11, macOS et Linux. Vérifiez dans un terminal : `ssh -V`.

## 2. Déclarer les images IOS (10 min)

Récupérez sur le e-campus les deux images :

- `c7200-adventerprisek9-mz.124-24.T5.image` (routeurs)
- `c3725-adventerprisek9-mz.124-15.T14.image` (switchs)

Pour chacune : GNS3 › **Edit › Preferences › Dynamips › IOS routers › New** › *New image* › choisissez le fichier › gardez les options par défaut jusqu'à la fin.

> **Idle-PC** : sans cette valeur, un seul routeur peut saturer votre processeur. Si GNS3 propose
> « Idle-PC finder », lancez-le et prenez une valeur marquée d'une étoile.

## 3. Importer la VM et la maquette (10 min)

1. **La VM** : VirtualBox › **Fichier › Importer un appareil virtuel** › `devnet-v4.ova` › Importer. Ne la démarrez pas depuis VirtualBox.

   Tout est déjà réglé dans la VM : la carte n°1 en NAT avec l'accès SSH depuis votre PC (port 2222), la carte n°2 prête pour GNS3.

2. **La maquette** : GNS3 › **File › Import portable project** › `CPE-NET-fil-rouge.gns3project`.

## 4. Brancher la VM sur la maquette (5 min)

1. GNS3 › **Edit › Preferences › VirtualBox › VirtualBox VMs › New** › choisissez `devnet-v4`.
2. Sélectionnez-la › **Edit** › onglet **Network** : **Adapters = 2**, cochez **« Allow GNS3 to use any configured VirtualBox adapter »**.
3. Glissez la VM dans le projet, près du NOC, puis câblez son interface **e1** sur **ESW-NOC fa1/3**.
   L'interface e0 reste en NAT : c'est elle qui donne Internet à la VM et l'accès SSH depuis votre PC.
4. Démarrez **tous** les équipements (▶ vert), y compris la VM, puis attendez 2 minutes.

> ⚠️ Démarrez toujours la VM **depuis GNS3**, jamais directement depuis VirtualBox.

## 5. Vérifier (5 min)

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

Un test échoue ? Notez lequel et le message d'erreur, et prévenez l'enseignant **avant** la séance.

### Pour gagner du temps à la séance 5 (facultatif, ≈ 1,5 Go à télécharger)

Chez vous, avec une bonne connexion, téléchargez à l'avance les images de NetBox :

```bash
cd ~/netbox-docker && docker compose pull
```

---

## La VM DEVNET en bref

| Élément | Valeur |
|---|---|
| Système | Ubuntu Server 24.04, sans interface graphique, clavier AZERTY |
| Compte | `cpe` / `123` (droits `sudo`, membre du groupe `docker`) |
| Carte 1, NAT (`enp0s3`) | Internet ; SSH depuis le PC : `ssh -p 2222 cpe@127.0.0.1` |
| Carte 2, GNS3 (`enp0s8`) | 172.16.100.2/26, routes vers 172.16.0.0/16 et 10.0.0.0/8 via 172.16.100.62 |
| Outils | git, Python 3 (venv, pip), Docker et Docker Compose, NetBox (`~/netbox-docker`) |
| SSH vers les IOS 12.4 | Anciens algorithmes déjà autorisés pour 172.16.\* et 10.\* |

### Problèmes fréquents

- **`ssh -p 2222` refusé** : la VM n'a pas fini de démarrer (attendez 1 minute), ou elle a été lancée depuis VirtualBox au lieu de GNS3.
- **La VM ne démarre pas depuis GNS3** : vérifiez qu'elle est arrêtée dans VirtualBox, puis relancez-la depuis GNS3.
- **Processeur à 100 %** : l'Idle-PC n'est pas réglé (étape 2).
