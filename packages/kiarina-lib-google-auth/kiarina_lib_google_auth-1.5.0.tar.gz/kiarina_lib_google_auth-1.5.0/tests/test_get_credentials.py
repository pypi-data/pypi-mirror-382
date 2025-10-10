import os

import google.auth.compute_engine.credentials
import google.oauth2.credentials
import google.oauth2.service_account
from google.auth import impersonated_credentials
import pytest

from kiarina.lib.google.auth import GoogleAuthSettings, get_credentials


@pytest.mark.xfail(
    not os.path.exists(
        os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    ),
    reason="ADC file not set",
)
def test_default():
    credentials = get_credentials(settings=GoogleAuthSettings())
    assert isinstance(
        credentials,
        (
            google.auth.compute_engine.credentials.Credentials,
            google.oauth2.service_account.Credentials,
            google.oauth2.credentials.Credentials,
        ),
    )


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE" not in os.environ,
    reason="GCP SA key file not set",
)
def test_service_account():
    credentials = get_credentials(
        settings=GoogleAuthSettings(
            type="service_account",
            service_account_file=os.environ[
                "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE"
            ],
        )
    )
    assert isinstance(credentials, google.oauth2.service_account.Credentials)


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE" not in os.environ,
    reason="GCP authorized user file not set",
)
def test_user_account():
    credentials = get_credentials(
        settings=GoogleAuthSettings(
            type="user_account",
            authorized_user_file=os.environ[
                "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_AUTHORIZED_USER_FILE"
            ],
            scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
        )
    )
    assert isinstance(credentials, google.oauth2.credentials.Credentials)


@pytest.mark.xfail(
    (
        "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE" not in os.environ
        or "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_IMPERSONATE_SA" not in os.environ
    ),
    reason="GCP SA key file not set",
)
def test_impersonate_service_account():
    credentials = get_credentials(
        settings=GoogleAuthSettings(
            type="service_account",
            service_account_file=os.environ[
                "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE"
            ],
            impersonate_service_account=os.environ[
                "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_IMPERSONATE_SA"
            ],
            scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
        )
    )
    assert isinstance(credentials, impersonated_credentials.Credentials)
