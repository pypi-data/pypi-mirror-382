"""
Module that manages OAuth2 functions for authentication
"""

import logging

import jwt
from jwt import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, PyJWKClient

from aixtools.utils import config

logger = logging.getLogger(__name__)


class AuthTokenError(Exception):
    """Exception raised for authentication token errors."""


# pylint: disable=too-few-public-methods
class AccessTokenVerifier:
    """
    Verifies Microsoft SSO JWT token against the configured Tenant ID, Audience, API ID and Issuer URL.
    """

    def __init__(self):
        tenant_id = config.APP_TENANT_ID
        self.api_id = config.APP_API_ID
        self.issuer_url = config.APP_ISSUER_URL
        # Azure AD endpoints
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self.jwks_client = PyJWKClient(
            uri=jwks_url,
            # cache keys url response to reduce SSO server network calls,
            # as public keys are not expected to change frequently
            cache_jwk_set=True,
            # cache resolved public keys
            cache_keys=True,
            # cache url response for 10 hours
            lifespan=36000,
        )

        logger.info("Using JWKS: %s", jwks_url)

    def verify(self, token: str) -> dict:
        """
        Verifies The JWT access token and returns decoded claims as a dictionary if the token is
        valid, otherwise raises an AuthTokenError
        """
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.api_id,
                issuer=self.issuer_url,
                # ensure audience verification is carried out
                options={"verify_aud": True},
            )
            return claims

        except ExpiredSignatureError as e:
            raise AuthTokenError("Token expired") from e
        except InvalidAudienceError as e:
            raise AuthTokenError(f"Token not for expected audience: {e}") from e
        except InvalidIssuerError as e:
            raise AuthTokenError(f"Token not for expected issuer: {e}") from e
        except jwt.exceptions.PyJWTError as e:
            raise AuthTokenError(f"Invalid token: {e}") from e
