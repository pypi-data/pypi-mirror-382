import json
import os

import google.oauth2.service_account
import pytest

from kiarina.lib.google.auth import get_service_account_credentials


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE" not in os.environ,
    reason="GCP SA key file not set",
)
def test_file():
    credentials = get_service_account_credentials(
        service_account_file=os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE"]
    )
    assert isinstance(credentials, google.oauth2.service_account.Credentials)


def test_nonexistent_file():
    with pytest.raises(ValueError, match="Service account file does not exist"):
        get_service_account_credentials(
            service_account_file="/path/to/nonexistent/file.json"
        )


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_DATA" not in os.environ,
    reason="GCP SA key data not set",
)
def test_data():
    credentials = get_service_account_credentials(
        service_account_data=json.loads(
            os.environ["KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_DATA"]
        )
    )
    assert isinstance(credentials, google.oauth2.service_account.Credentials)
