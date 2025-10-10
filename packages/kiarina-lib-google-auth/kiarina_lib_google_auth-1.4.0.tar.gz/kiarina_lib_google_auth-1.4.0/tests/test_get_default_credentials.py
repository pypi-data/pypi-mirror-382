import os

import google.oauth2.credentials
import google.oauth2.service_account
import pytest

from kiarina.lib.google.auth._utils.get_default_credentials import (
    get_default_credentials,
)


@pytest.mark.xfail(
    not os.path.exists(
        os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    ),
    reason="ADC file not set",
)
def test_adc():
    credentials = get_default_credentials()
    print(f"Obtained credentials of type: {type(credentials)}")
    assert isinstance(credentials, google.oauth2.credentials.Credentials)


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE" not in os.environ,
    reason="GCP SA key file not set",
)
def test_service_account():
    # Set the environment variable to point to a service account key file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(
        os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE"]
    )

    credentials = get_default_credentials()
    print(f"Obtained service account credentials of type: {type(credentials)}")
    assert isinstance(credentials, google.oauth2.service_account.Credentials)
