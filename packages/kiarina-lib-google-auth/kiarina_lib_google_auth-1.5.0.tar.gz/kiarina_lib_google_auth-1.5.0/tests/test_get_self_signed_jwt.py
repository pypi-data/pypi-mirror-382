import os

import pytest

from kiarina.lib.google.auth import GoogleAuthSettings, get_self_signed_jwt


@pytest.mark.xfail(
    "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE" not in os.environ,
    reason="GCP SA key file not set",
)
def test_get_self_signed_jwt():
    jwt = get_self_signed_jwt(
        settings=GoogleAuthSettings(
            type="service_account",
            service_account_file=os.environ[
                "KIARINA_LIB_GOOGLE_AUTH_TEST_GCP_SA_KEY_FILE"
            ],
        ),
        audience="https://blazeworks.jp/",
    )
    assert jwt.count(".") == 2
