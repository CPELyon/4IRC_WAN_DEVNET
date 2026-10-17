# TP-00 — Préparer son environnement

**À faire avant la séance 1** · ≈ 1 h · Lisible directement sur GitHub, aucun outil requis

> À la fin de ce TP, la maquette tourne dans GNS3, la VM DEVNET y est branchée, et vous vous connectez
> à la VM en SSH depuis votre PC. La séance 1 commence directement par Git et VS Code (TP-01).

**Matériel** : un PC avec 16 Go de RAM (la maquette en prend environ 4 Go, la VM environ 2 Go) et 20 Go de disque libre.

| Étape | Durée |
|---|---|
| 1. Installer les logiciels | 15 min |
| 2. Déclarer les images IOS | 10 min |
| 3. Importer la VM et la maquette | 15 min |
| 4. Brancher la VM sur la maquette | 10 min |
| 5. Configurer le réseau de la VM | 10 min |

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

## 3. Importer la VM et la maquette (15 min)

1. **La VM** : VirtualBox › **Fichier › Importer un appareil virtuel** › `devnet-v3.ova` (fourni par l'enseignant). Ne la démarrez pas.
2. **Accès SSH depuis votre PC** : VirtualBox › VM `devnet` › **Configuration › Réseau › Adaptateur 1** (NAT) › **Avancé › Redirection de ports** › ajoutez :

   | Nom | Protocole | IP hôte | Port hôte | IP invité | Port invité |
   |---|---|---|---|---|---|
   | ssh | TCP | 127.0.0.1 | 2222 | *(vide)* | 22 |

3. **La maquette** : GNS3 › **File › Import portable project** › `CPE-NET-fil-rouge.gns3project` (fourni par l'enseignant).

## 4. Brancher la VM sur la maquette (10 min)

1. GNS3 › **Edit › Preferences › VirtualBox › VirtualBox VMs › New** › choisissez `devnet`.
2. Sélectionnez-la › **Edit** › onglet **Network** : **Adapters = 2**, cochez **« Allow GNS3 to use any configured VirtualBox adapter »**.
3. Glissez la VM dans le projet, près du NOC, puis câblez son interface **e1** sur **ESW-NOC fa1/3**.
   L'interface e0 reste en NAT : c'est elle qui donne Internet à la VM et l'accès SSH depuis votre PC.
4. Démarrez **tous** les équipements (▶ vert), y compris la VM, puis attendez 2 minutes.

> ⚠️ Démarrez toujours la VM **depuis GNS3**, jamais directement depuis VirtualBox.

## 5. Configurer le réseau de la VM (10 min)

Connectez-vous à la VM, soit dans la fenêtre de console ouverte par VirtualBox, soit depuis votre PC :

```bash
ssh -p 2222 cpe@127.0.0.1
```

1. Repérez les interfaces : `ip link show`.
   - `enp0s3` : l'interface NAT (Internet), adresse en 10.0.2.x reçue par DHCP ;
   - `enp0s8` : l'interface branchée sur la maquette (si le nom diffère, adaptez la commande suivante).
2. Donnez-lui son adresse et ses routes vers la maquette. Cette configuration est **permanente** : elle survit aux redémarrages.
   ```bash
   sudo nmcli connection add type ethernet con-name gns3 ifname enp0s8 \
        ipv4.method manual ipv4.addresses 172.16.100.2/26 \
        ipv4.routes "172.16.0.0/16 172.16.100.62, 10.0.0.0/8 172.16.100.62" \
        ipv4.never-default yes autoconnect yes
   sudo nmcli connection up gns3
   ```
   `ipv4.never-default` garde la route par défaut sur l'interface NAT : Internet continue de passer par là.

## ✅ Vérifier avant la séance 1

| Test | Commande | Résultat attendu |
|---|---|---|
| Internet depuis la VM | `ping -c 3 8.8.8.8` | Réponses |
| Passerelle du NOC | `ping -c 3 172.16.100.62` | Réponses |
| Un routeur de site | `ping -c 3 172.16.100.126` (R1-LYON) | Réponses |
| SSH vers la maquette | `ssh cisco@172.16.100.126` (mot de passe `cisco`) | Prompt `R1-LYON#` |
| SSH PC → VM | depuis votre PC : `ssh -p 2222 cpe@127.0.0.1` | Prompt de la VM |

Un test échoue ? Notez lequel et le message d'erreur, et prévenez l'enseignant **avant** la séance.

### Problèmes fréquents

- **SSH vers un routeur refusé avec « no matching key exchange method »** : les IOS de la maquette sont anciens.
  Dans la VM, ajoutez à `~/.ssh/config` :
  ```
  Host 172.16.* 10.*
      KexAlgorithms +diffie-hellman-group1-sha1,diffie-hellman-group14-sha1
      HostKeyAlgorithms +ssh-rsa
      PubkeyAcceptedAlgorithms +ssh-rsa
      Ciphers +aes128-cbc,3des-cbc
  ```
- **La VM ne démarre pas depuis GNS3** : vérifiez qu'elle est arrêtée dans VirtualBox, puis relancez-la depuis GNS3.
- **Processeur à 100 %** : l'Idle-PC n'est pas réglé (étape 2).
