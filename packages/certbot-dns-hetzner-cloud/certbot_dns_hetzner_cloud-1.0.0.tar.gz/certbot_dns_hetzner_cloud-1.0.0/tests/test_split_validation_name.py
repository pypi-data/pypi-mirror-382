import pytest
from certbot_dns_hetzner_cloud.authenticator import split_validation_name

@pytest.mark.parametrize("fqdn, zone, rec", [
    ("_acme-challenge.example.com.", "example.com", "_acme-challenge"),
    ("_acme-challenge.sub.example.com.", "example.com", "_acme-challenge.sub"),
    ("_acme-challenge.sub.example.co.uk.", "example.co.uk", "_acme-challenge.sub"),
])
def test_split_validation_name_ok(fqdn, zone, rec):
    z, r = split_validation_name(fqdn)
    assert z == zone
    assert r == rec

def test_split_validation_name_robust_without_trailing_dot():
    z, r = split_validation_name("_acme-challenge.example.com")
    assert z == "example.com"
    assert r == "_acme-challenge"
