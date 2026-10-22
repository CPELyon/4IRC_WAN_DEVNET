# TP-02 — Générer les configurations

**Bloc NAF : Intention** · Séance 2 · Avant de commencer : `git pull --no-edit upstream main`

> Le bloc Intention ne fait pas que stocker : il **valide** les données et **génère** les artefacts de
> configuration. Aujourd'hui, une seule source (vos YAML) produit les configs de tous les sites.

| Module | Objectif |
|---|---|
| 1. Valider ses données | Détecter les erreurs avant qu'elles ne partent sur le réseau |
| 2. Un premier template | Comprendre Template() et render() |
| 3. Templates switch, routeur et VRRP | Générer les configs de Marseille et Paris |
| 4. Générer Marseille, l'appliquer, tester | Vérifier que la config générée fonctionne vraiment |

Pré-requis : `data/lyon.yaml` conforme à [docs/modele-donnees.md](../docs/modele-donnees.md).
Écrivez `data/mars.yaml` et `data/pars.yaml` si ce n'est pas déjà fait.

---

## Module 1 — Valider ses données

**Objectif** : à la fin, `python -m scripts.validate` signale toute incohérence dans `data/`.

### Construire
1. Vérifiez d'abord la **forme** de vos fichiers avec `yamllint data/` (règles dans `.yamllint`) : indentation, tabulations, clés en double. Corrigez jusqu'à ce qu'il ne signale plus rien.
2. Vérifiez ensuite le **fond** : complétez `check_site()` dans `scripts/validate.py` (4 contrôles décrits dans la docstring).
   - 👀 **Lisez** le `__main__` de `scripts/validate.py` : que renvoie `sys.exit(0 if ok else 1)` au système, et à quoi cela peut-il servir ? **(la pipeline CI du TP-06 s'arrête grâce à ce code de sortie)**
3. Utilisez le module `ipaddress` :
   ```python
   import ipaddress
   ipaddress.ip_address("172.16.10.254") in ipaddress.ip_network("172.16.10.0/24")   # True
   ipaddress.ip_interface("172.16.10.252/24").ip                                      # 172.16.10.252
   ```

### Tester sa fonction avec pytest
Pour savoir si `check_site()` fonctionne, on ne se contente pas d'essayer à la main : des **tests automatiques** sont fournis.
`pytest` cherche les fichiers `tests/test_*.py`, exécute chaque fonction `test_…`, et vérifie chaque `assert` : vrai, le test passe ; faux (ou une erreur), il échoue.

4. 👀 **Ouvrez `tests/test_validate.py`** : quel site de test est utilisé ? Que modifie `test_passerelle_hors_reseau()` avant d'appeler `check_site()`, et qu'attend-il en retour ? **(au TP-06, vous écrirez vos propres tests, lancés automatiquement par la CI)**
5. Lancez les tests **avant** de coder : `pytest tests/test_validate.py -v`. Lisez la sortie : combien échouent, et pourquoi ?
6. Relancez-les après avoir complété `check_site()`.

### Vérifier
- `yamllint data/` ne signale rien.
- `pytest tests/test_validate.py -v` : les 6 tests passent (`PASSED`).
- `python -m scripts.validate` : vos trois sites sont OK.
- Introduisez une erreur volontaire dans `data/pars.yaml` (passerelle dans le mauvais réseau) : est-elle détectée ?

### Comprendre
- À quoi servent les codes de sortie 0 et 1 de `scripts/validate.py` ?
- Que détecte `yamllint` que `check_site()` ne voit pas, et inversement ?

---

## Module 2 — Un premier template

**Objectif** : à la fin, je sais transformer un dictionnaire en texte de configuration avec Jinja2.

### Découvrir
Créez le fichier `scripts/essai_jinja.py` :
```python
from jinja2 import Template

t = Template(
   """interface {{ name }}\n
   description {{ desc }}\n""")
print(t.render(name="GigabitEthernet0/0.10", desc="VLAN teacher"))
```
1. Exécutez le code et analysez son fonctionnement : `python -m scripts.essai_jinja` (depuis la racine du projet).
2. Ajoutez une boucle `{% for vlan in vlans %}` qui génère une sous-interface par VLAN de Lyon : fournissez au template les données de `data/lyon.yaml`.
3. Ajoutez une condition `{% if %}` : n'écrire la ligne `description` que si le VLAN a un nom.

### Comprendre
- Que se passe-t-il si une variable est absente des données ? Essayez `{{ inconnue | default("?") }}`.
- D'où viennent les lignes vides en trop ? Testez `{%-` et `-%}`.

---

## Module 3 — Templates switch, routeur et VRRP

**Objectif** : à la fin, `python -m scripts.render` génère `config/<hostname>.cfg` pour tous les équipements des sites.

### Découvrir
1. Relisez `templates/core_router.j2` et `scripts/render_core.py` : c'est le modèle à suivre.
2. Repérez les filtres disponibles dans `scripts/utils.py` : `ip_addr`, `netmask`, `wildcard`, `network`.
   - 👀 **Lisez** `get_jinja_env()` dans `scripts/utils.py` : que font `trim_blocks` et `lstrip_blocks` ? C'est la réponse à la question des lignes vides du module 2. **(tous les templates du module passent par cette fonction)**

### Construire
3. `templates/site_switch.j2` : les VLANs (`vlan <id>` / `name <nom>` en mode configuration), les ports d'accès et les trunks d'**un** switch (un site peut en avoir plusieurs : `switches` est une liste).
4. `templates/site_router.j2` : une sous-interface par VLAN avec l'IP **réelle** du routeur, puis le VRRP.
   - Le VRRP n'est généré **que si le site a deux routeurs** : la condition se calcule dans le template (`site.routers | length`).
   - Groupe VRRP = numéro de VLAN, IP virtuelle = `gateway`, priorité = `vrrp_priority`, `preempt`.
5. Complétez `scripts/render.py` (`render_switch`, `render_router`, `render_site`) et `save_text()` dans `scripts/utils.py`.
   - 👀 **Lisez** le `__main__` de `scripts/render.py` : quels fichiers sont lus, où sont écrites les configurations et sous quel nom ? **(au TP-03, vos exécuteurs déploieront exactement ces fichiers)**

### Vérifier
- `python -m scripts.render` crée 3 fichiers pour Lyon, 3 pour Marseille, 2 pour Paris.
- **Comparez `config/R1-LYON.cfg` avec vos notes du TP-01** : mêmes commandes ?
- `config/R1-PARS.cfg` ne contient aucune ligne `vrrp`.
- `pytest tests/test_render.py -v` passe. 👀 Ouvrez `tests/test_render.py` : que vérifie ce test, et pourquoi tourne-t-il une fois par site (`parametrize`) ?

### Comprendre
- Pour ajouter un 4e site, que faut-il modifier ?
- Dans un template, pourquoi éviter `{% if router.hostname == "R1-LYON" %}` ?

✅ **Point de contrôle** : faites vérifier vos templates et le résultat pour Paris.

---

## Module 4 — Générer Marseille, l'appliquer, tester

**Objectif** : à la fin, Marseille fonctionne avec une configuration que je n'ai pas tapée.

### Construire
1. Ouvrez une console sur ESW-MARS, R1-MARS et R2-MARS, passez en `configure terminal` et **copiez-collez** le contenu des fichiers générés.
2. Si une commande est refusée : corrigez **le template ou les données**, régénérez, recommencez. Jamais la config générée à la main.

### Vérifier
- PC-MARS-10 joint sa passerelle 172.16.30.254 et PC-MARS-20.
- `show vrrp brief` : R1-MARS Master sur les deux groupes.
- Test de bascule comme au TP-01.

### Comprendre
- Le copier-coller est-il une bonne méthode pour 50 sites ? Que manque-t-il ?

✅ **Fin de séance** : `git commit -m "TP2 : templates et configs générées"` puis `git push`.
Paris est généré mais **pas appliqué** : ce sera le travail de l'exécuteur au TP-03.
