import time
from collections.abc import Callable
from typing import Any
import jwt
import requests
from django.conf import settings
from django.utils.translation import gettext
from jwt import PyJWTError, PyJWKClient
from requests import RequestException
from rest_framework.exceptions import ValidationError

_APPLE_ISSUER = "https://appleid.apple.com"
_APPLE_JWKS_URL = f"{_APPLE_ISSUER}/auth/keys"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

_session = requests.Session()
_apple_jwk_client = PyJWKClient(_APPLE_JWKS_URL)


def _get_user_from_apple_token(token: str) -> dict[str, Any]:
    try:
        signing_key = _apple_jwk_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS26"],
            audience=settings.APPLE_CLIENT_ID,
            issuer=_APPLE_ISSUER,
        )
    except PyJWTError:
        raise ValidationError(gettext("Invalid Apple token."))


def _get_user_from_google_token(token: str) -> dict[str, Any]:
    try:
        response = _session.get(_GOOGLE_USERINFO_URL, params={"access_token": token})
        response.raise_for_status()
        return response.json()
    except RequestException:
        raise ValidationError(gettext("Invalid Google token."))


_TOKEN_HANDLERS: dict[str, Callable[[str], dict[str, Any]]] = {
    "apple": _get_user_from_apple_token,
    "google": _get_user_from_google_token,
}


class OAuthUtils:
    @staticmethod
    def generate_client_secret() -> str:
        current_time = int(time.time())
        headers = {"alg": "ES256", "kid": settings.APPLE_KEY_ID}
        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": current_time,
            "exp": current_time + 3600,
            "aud": _APPLE_ISSUER,
            "sub": settings.APPLE_CLIENT_ID,
        }
        return jwt.encode(
            payload, settings.APPLE_PRIVATE_KEY, algorithm="ES256", headers=headers
        )

    @staticmethod
    def get_apple_public_key() -> dict[str, Any]:
        try:
            response = _session.get(_APPLE_JWKS_URL)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise ValidationError(gettext("Could not retrieve Apple public keys.")) from e

    @staticmethod
    def user_from_token(token: str, driver: str) -> dict[str, Any]:
        if settings.DEBUG and token == getattr(
            settings, "TEST_USER_SOCIAL_TOKEN", None
        ):
            return {
                "email": settings.TEST_USER_EMAIL,
                "name": settings.TEST_USER_FULL_NAME,
            }

        handler = _TOKEN_HANDLERS.get(driver)
        if not handler:
            raise ValidationError(gettext("Invalid social driver."))

        return handler(token)