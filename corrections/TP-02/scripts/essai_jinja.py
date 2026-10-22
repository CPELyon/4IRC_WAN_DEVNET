"""TP-02, module 2 : un premier template Jinja2 (correction).

    python -m scripts.essai_jinja        (depuis la racine du projet)
"""
from jinja2 import Template

from scripts.utils import load_yaml

# 1. Le template de départ : des variables simples, passées à render()
t = Template(
   """interface {{ name }}\n
   description {{ desc }}\n""")
print(t.render(name="GigabitEthernet0/0.10", desc="VLAN teacher"))

# 2. Une sous-interface par VLAN de Lyon : les données viennent de data/lyon.yaml
# 3. La ligne description n'est écrite que si le VLAN a un nom
site = load_yaml("data/lyon.yaml")
t = Template(
   """{% for vlan in vlans %}
interface GigabitEthernet0/0.{{ vlan.id }}
{% if vlan.name %}
 description VLAN {{ vlan.name }}
{% endif %}
 encapsulation dot1Q {{ vlan.id }}
{% endfor %}
-----""")
print(t.render(vlans=site["vlans"]))

# 3 (vérification). Tous les VLANs de Lyon ont un nom : on en ajoute un sans nom pour voir la condition agir
vlans = site["vlans"] + [{"id": 100}]
print(t.render(vlans=vlans))

# Comprendre 1. Variable absente : vide par défaut, ou valeur de repli avec le filtre default
print(Template("hostname {{ inconnue }}").render())                     # "hostname " (rien, sans erreur)
print(Template('hostname {{ inconnue | default("?") }}').render())      # "hostname ?"

# Comprendre 2. Les lignes vides viennent des balises {% %} : le retour à la ligne qui les suit reste dans le texte.
# {%- supprime les blancs (dont le retour à la ligne) AVANT la balise, -%} ceux APRÈS.
# Ici on met {%- partout : chaque balise « mange » la fin de la ligne précédente, l'indentation est conservée.
# (Au module 3, get_jinja_env() fait la même chose pour tous les templates avec trim_blocks et lstrip_blocks => Ces paramètres agissent comme les -% nativements)
t = Template(
   """-----
   {%- for vlan in vlans %}
interface GigabitEthernet0/0.{{ vlan.id }}
{%- if vlan.name %}
 description VLAN {{ vlan.name }}
{%- endif %}
 encapsulation dot1Q {{ vlan.id }}
{%- endfor %}""")
print(t.render(vlans=vlans))
