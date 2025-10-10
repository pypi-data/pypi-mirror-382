import pytest
from types import SimpleNamespace
from certbot_dns_hetzner_cloud.hetzner_cloud_helper import HetznerCloudHelper
import certbot_dns_hetzner_cloud.hetzner_cloud_helper as mod

# ---- Test-Doubles ----

class FakeRRSet:
    def __init__(self, name, value):
        self.name = name
        self.records = [SimpleNamespace(value=value, comment=None)]

class FakeRRSetListResp:
    def __init__(self, rrsets=None):
        self.rrsets = rrsets or []

class FakeZonesAPI:
    def __init__(self):
        # Aufgerufen-Flags + zuletzt übergebene Argumente
        self.calls = []
        self.bound_zone = SimpleNamespace(id="Z1", name="example.com")

    # Zonen
    def get(self, zone_name):
        self.calls.append(("get", zone_name))
        assert zone_name == "example.com"
        return self.bound_zone

    # RRSet lesen
    def get_rrset_list(self, *, zone, name, type):
        self.calls.append(("get_rrset_list", zone.name, name, type))
        # Rückgabe wird pro Test per Injection gesetzt
        return self._rrset_list

    # RRSet löschen
    def delete_rrset(self, rrset):
        self.calls.append(("delete_rrset", rrset.name))

    # RRSet erstellen
    def create_rrset(self, *, zone, name, type, records):
        self.calls.append(("create_rrset", zone.name, name, type, tuple(r.value for r in records)))
        # Minimal-Response mit rrset zurückgeben (ähnlich hcloud)
        return SimpleNamespace(rrset=FakeRRSet(name, records[0].value))

class FakeClient:
    def __init__(self):
        self.zones = FakeZonesAPI()

class FakeBoundZone:
    def __init__(self, name="example.com", id_="Z1"):
        self.name = name
        self.id = id_

# ---- Fixtures ----

@pytest.fixture
def helper(monkeypatch):
    # 1) Hetzner-Client faken
    def fake_init(self, api_key: str):
        self.client = FakeClient()
    monkeypatch.setattr(HetznerCloudHelper, "__init__", fake_init)

    # 2) BoundZone-Klasse im Modul patchen, damit isinstance(...) True ist
    monkeypatch.setattr(mod, "BoundZone", FakeBoundZone)

    # 3) Instanz + Default-BoundZone setzen
    h = HetznerCloudHelper("DUMMY")
    h.client.zones.bound_zone = FakeBoundZone(name="example.com", id_="Z1")

    # (optional) leere RRSet-Liste als Default
    h.client.zones._rrset_list = FakeRRSetListResp([])

    return h

# ---- Tests ----

def test_ensure_zone_with_string(helper):
    zones = helper.client.zones
    zones._rrset_list = FakeRRSetListResp([])  # default

    z = helper._ensure_zone("example.com")
    assert z.name == "example.com"
    assert ("get", "example.com") in zones.calls

def test_ensure_zone_with_boundzone(helper, monkeypatch):
    zones = helper.client.zones
    zones._rrset_list = FakeRRSetListResp([])

    # make BoundZone isinstance(...) pass
    monkeypatch.setattr(mod, "BoundZone", FakeBoundZone)

    bound = FakeBoundZone(name="example.com", id_="Z1")
    zones.bound_zone = bound  # our fake bound zone

    z = helper._ensure_zone(bound)

    assert z is bound
    assert z.name == "example.com"
    assert not any(c[0] == "get" for c in zones.calls)

def test_delete_txt_record_deletes_when_present(helper):
    zones = helper.client.zones
    # Simuliere vorhandenes RRSet
    zones._rrset_list = FakeRRSetListResp([FakeRRSet("_acme-challenge", '"old"')])

    helper.delete_txt_record("example.com", "_acme-challenge")

    # Erwartung: get -> get_rrset_list -> delete_rrset
    assert ("get", "example.com") in zones.calls
    assert ("get_rrset_list", "example.com", "_acme-challenge", "TXT") in zones.calls
    assert ("delete_rrset", "_acme-challenge") in zones.calls

def test_delete_txt_record_noop_when_absent(helper):
    zones = helper.client.zones
    zones._rrset_list = FakeRRSetListResp([])

    helper.delete_txt_record("example.com", "_acme-challenge")

    # Kein delete_rrset-Call
    assert ("get_rrset_list", "example.com", "_acme-challenge", "TXT") in zones.calls
    assert not [c for c in zones.calls if c[0] == "delete_rrset"]

def test_put_txt_record_quotes_value_and_replaces(helper):
    zones = helper.client.zones
    # Vorhandenes RRSet -> sollte erst gelöscht, dann neu erstellt werden
    zones._rrset_list = FakeRRSetListResp([FakeRRSet("_acme-challenge", '"old"')])

    resp = helper.put_txt_record("example.com", "_acme-challenge", value="abc123", comment="test")

    # Reihenfolge prüfen: get → get_rrset_list → delete_rrset → create_rrset
    names = [c[0] for c in zones.calls]
    assert names[:4] == ["get", "get_rrset_list", "delete_rrset", "create_rrset"]

    # create_rrset wurde mit gequotetem Value aufgerufen:
    create_call = [c for c in zones.calls if c[0] == "create_rrset"][-1]
    _, zone_name, rr_name, rr_type, values = create_call
    assert zone_name == "example.com"
    assert rr_name == "_acme-challenge"
    assert rr_type == "TXT"
    assert values == ('"abc123"',)  # helper quotet den Wert

    # Response rrset enthält den neuen Wert
    assert resp.rrset.records[0].value == '"abc123"'
