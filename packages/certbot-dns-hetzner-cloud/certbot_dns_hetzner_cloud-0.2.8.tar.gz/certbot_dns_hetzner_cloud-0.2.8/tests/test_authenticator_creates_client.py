import pytest
from unittest.mock import MagicMock, patch, ANY
from certbot_dns_hetzner_cloud.authenticator import HetznerCloudDNSAuthenticator

def test_setup_credentials_creates_client():
    auth = object.__new__(HetznerCloudDNSAuthenticator)

    mock_credentials = MagicMock()
    mock_credentials.conf.return_value = "dummy_token"

    with patch.object(auth, "_configure_credentials", return_value=mock_credentials) as mock_configure, \
         patch("certbot_dns_hetzner_cloud.authenticator.HetznerCloudHelper", autospec=True) as mock_helper:

        auth._setup_credentials()

        mock_configure.assert_called_once_with(
            "credentials",
            ANY,
            {"api_token": "Hetzner Cloud API Token"},
        )
        mock_helper.assert_called_once_with("dummy_token")

        # Falls du in _setup_credentials auf hetzner_dns_helper umgestellt hast:
        client = getattr(auth, "hetzner_dns_helper", getattr(auth, "_client", None))
        assert client is mock_helper.return_value
