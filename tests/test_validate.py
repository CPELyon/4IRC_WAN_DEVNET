"""Tests fournis pour vérifier votre fonction check_site (TP-02, module 1).

    pytest tests/test_validate.py -v
"""
import copy

from scripts.validate import check_site

SITE = {
    "site": "CPE-TEST",
    "code": "test",
    "switches": [{"hostname": "ESW-TEST", "platform": "ios", "model": "c3725",
                  "trunks": ["FastEthernet1/0", "FastEthernet1/1"],
                  "access_ports": [{"interface": "FastEthernet1/2", "vlan": 10}]}],
    "routers": [
        {"hostname": "R1-TEST", "platform": "ios", "model": "c7200", "loopback": "10.255.0.91/32", "lan_interface": "GigabitEthernet0/0",
         "vrrp_priority": 110, "wan": [{"interface": "Serial1/0", "ip": "10.0.0.90/30", "peer": "CORE-1"}],
         "ips": {10: "192.168.10.252/24", 20: "192.168.20.252/24"}},
        {"hostname": "R2-TEST", "platform": "ios", "model": "c7200", "loopback": "10.255.0.92/32", "lan_interface": "GigabitEthernet0/0",
         "vrrp_priority": 100, "wan": [{"interface": "Serial1/0", "ip": "10.0.0.94/30", "peer": "CORE-2"}],
         "ips": {10: "192.168.10.253/24", 20: "192.168.20.253/24"}},
    ],
    "vlans": [
        {"id": 10, "name": "teacher", "subnet": "192.168.10.0/24", "gateway": "192.168.10.254"},
        {"id": 20, "name": "student", "subnet": "192.168.20.0/24", "gateway": "192.168.20.254"},
    ],
}


def test_site_valide():
    assert check_site(copy.deepcopy(SITE)) == []


def test_vlan_en_double():
    site = copy.deepcopy(SITE)
    site["vlans"][1]["id"] = 10
    assert len(check_site(site)) >= 1


def test_passerelle_hors_reseau():
    site = copy.deepcopy(SITE)
    site["vlans"][0]["gateway"] = "192.168.99.254"
    assert len(check_site(site)) >= 1


def test_ip_routeur_hors_reseau():
    site = copy.deepcopy(SITE)
    site["routers"][0]["ips"][20] = "192.168.30.252/24"
    assert len(check_site(site)) >= 1


def test_priorites_vrrp_identiques():
    site = copy.deepcopy(SITE)
    site["routers"][1]["vrrp_priority"] = 110
    assert len(check_site(site)) >= 1


def test_site_a_un_routeur_sans_priorite():
    site = copy.deepcopy(SITE)
    site["routers"] = site["routers"][:1]
    del site["routers"][0]["vrrp_priority"]
    assert check_site(site) == []
