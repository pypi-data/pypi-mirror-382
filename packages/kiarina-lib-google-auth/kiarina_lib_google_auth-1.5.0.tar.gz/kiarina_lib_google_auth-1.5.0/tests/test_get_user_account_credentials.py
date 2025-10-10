import json
import os

from google.oauth2.credentials import Credentials
import pytest

from kiarina.lib.google.auth import CredentialsCache, get_user_account_credentials


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE" not in os.environ,
    reason="GCP authorized user file not set",
)
def test_file():
    credentials = get_user_account_credentials(
        authorized_user_file=os.environ[
            "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE"
        ],
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
    )
    assert isinstance(credentials, Credentials)


def test_nonexistent_file():
    with pytest.raises(ValueError, match="Authorized user file does not exist"):
        get_user_account_credentials(
            authorized_user_file="/path/to/nonexistent/file.json",
            scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
        )


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA" not in os.environ,
    reason="GCP authorized user data not set",
)
def test_data():
    credentials = get_user_account_credentials(
        authorized_user_data=json.loads(
            os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA"]
        ),
        scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
    )
    assert isinstance(credentials, Credentials)


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA" not in os.environ,
    reason="GCP authorized user data not set",
)
def test_cache():
    from unittest.mock import patch, MagicMock

    class InMemoryCache(CredentialsCache):
        def __init__(self):
            self._cache: str | None = None

        def get(self) -> str | None:
            return self._cache

        def set(self, value: str) -> None:
            self._cache = value

    cache = InMemoryCache()
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only"]

    # Mock Credentials to control valid/expired state
    with patch(
        "kiarina.lib.google.auth._utils.get_user_account_credentials.Credentials"
    ) as MockCredentials:
        # First call: credentials are invalid and need refresh
        mock_creds_invalid = MagicMock(spec=Credentials)
        mock_creds_invalid.valid = False
        mock_creds_invalid.expired = True
        mock_creds_invalid.refresh_token = "mock_refresh_token"
        mock_creds_invalid.to_json.return_value = json.dumps(
            {
                "type": "authorized_user",
                "client_id": "mock_client_id",
                "client_secret": "mock_client_secret",
                "refresh_token": "mock_refresh_token",
            }
        )

        # After refresh, credentials become valid
        def refresh_side_effect(_):
            mock_creds_invalid.valid = True
            mock_creds_invalid.expired = False

        mock_creds_invalid.refresh.side_effect = refresh_side_effect

        MockCredentials.from_authorized_user_info.return_value = mock_creds_invalid

        # First call: should refresh and cache
        credentials = get_user_account_credentials(
            authorized_user_data=json.loads(
                os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA"]
            ),
            scopes=scopes,
            cache=cache,
        )

        assert isinstance(credentials, MagicMock)
        assert credentials.valid is True
        assert cache.get() is not None
        mock_creds_invalid.refresh.assert_called_once()

        # Second call: should use cached credentials
        mock_creds_cached = MagicMock(spec=Credentials)
        mock_creds_cached.valid = True
        mock_creds_cached.expired = False

        MockCredentials.from_authorized_user_info.return_value = mock_creds_cached

        credentials2 = get_user_account_credentials(
            authorized_user_data=json.loads(
                os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_DATA"]
            ),
            scopes=scopes,
            cache=cache,
        )

        assert isinstance(credentials2, MagicMock)
        assert credentials2.valid is True
        # Cached credentials should not need refresh
        mock_creds_cached.refresh.assert_not_called()
