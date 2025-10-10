import json
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from .._types.credentials_cache import CredentialsCache


def get_user_account_credentials(
    *,
    authorized_user_file: str | os.PathLike[str] | None = None,
    authorized_user_data: dict[str, object] | None = None,
    scopes: list[str],
    cache: CredentialsCache | None = None,
) -> Credentials:
    if authorized_user_data:
        credentials = Credentials.from_authorized_user_info(  # type: ignore[no-untyped-call]
            authorized_user_data,
            scopes=scopes,
        )

        return _check_and_refresh_credentials(
            credentials,
            scopes=scopes,
            cache=cache,
        )

    elif authorized_user_file:
        authorized_user_file = os.path.expanduser(
            os.path.expandvars(os.fspath(authorized_user_file))
        )

        if not os.path.exists(authorized_user_file):
            raise ValueError(
                f"Authorized user file does not exist: {authorized_user_file}"
            )

        credentials = Credentials.from_authorized_user_file(  # type: ignore[no-untyped-call]
            authorized_user_file,
            scopes=scopes,
        )

        return _check_and_refresh_credentials(
            credentials,
            scopes=scopes,
            cache=cache,
        )

    else:
        raise ValueError("No valid user account credentials found.")


def _check_and_refresh_credentials(
    credentials: Credentials,
    *,
    scopes: list[str],
    cache: CredentialsCache | None = None,
) -> Credentials:
    if credentials.valid:
        return credentials

    if cache:
        if cached_json_str := cache.get():
            cached_credentials = Credentials.from_authorized_user_info(  # type: ignore[no-untyped-call]
                json.loads(cached_json_str),
                scopes=scopes,
            )

            if cached_credentials.valid:
                return cached_credentials  # type: ignore[no-any-return]

            credentials = cached_credentials

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())  # type: ignore[no-untyped-call]

        if cache:
            cache.set(credentials.to_json())  # type: ignore[no-untyped-call]

    return credentials
