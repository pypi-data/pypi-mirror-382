"""
JWT Authentication and Verification for EGRC Platform.

This module provides comprehensive JWT verification, validation, and caching
for Keycloak OIDC integration with RS256 signature verification.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidKeyError,
    InvalidSignatureError,
    InvalidTokenError,
)

from ..cache import SecurityCache
from ..config.settings import settings
from ..exceptions.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    TokenRevokedError,
)


logger = logging.getLogger(__name__)


class JWKSCache:
    """
    JWKS (JSON Web Key Set) cache for efficient JWT verification.

    Caches public keys from Keycloak's JWKS endpoint to avoid
    repeated network calls during JWT verification.
    """

    def __init__(self, jwks_url: str, cache_ttl: int = 3600):
        """
        Initialize JWKS cache.

        Args:
            jwks_url: URL to Keycloak's JWKS endpoint
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.jwks_url = jwks_url
        self.cache_ttl = cache_ttl
        self._jwks_client = PyJWKClient(jwks_url, cache_ttl=cache_ttl)
        self._cache = SecurityCache()
        self._last_fetch = 0

    def get_signing_key(self, token: str) -> Any:
        """
        Get signing key for JWT verification.

        Args:
            token: JWT token

        Returns:
            Signing key for verification

        Raises:
            InvalidKeyError: If key cannot be found or is invalid
        """
        try:
            return self._jwks_client.get_signing_key_from_jwt(token)
        except Exception as e:
            logger.error(f"Failed to get signing key: {e}")
            raise InvalidKeyError(f"Could not find signing key: {e}")

    def refresh_keys(self) -> None:
        """Force refresh of JWKS keys."""
        try:
            self._jwks_client.get_signing_keys()
            self._last_fetch = time.time()
            logger.info("JWKS keys refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to refresh JWKS keys: {e}")
            raise


class TokenValidator:
    """
    JWT token validator with comprehensive validation rules.

    Validates JWT tokens against Keycloak OIDC standards including
    signature verification, expiration, audience, issuer, and custom claims.
    """

    def __init__(
        self,
        issuer: str,
        audience: Union[str, List[str]],
        algorithms: List[str] = None,
        clock_skew: int = 30,
    ):
        """
        Initialize token validator.

        Args:
            issuer: Expected JWT issuer (Keycloak realm URL)
            audience: Expected JWT audience(s)
            algorithms: Allowed signing algorithms (default: RS256)
            clock_skew: Clock skew tolerance in seconds
        """
        self.issuer = issuer
        self.audience = audience if isinstance(audience, list) else [audience]
        self.algorithms = algorithms or ["RS256"]
        self.clock_skew = clock_skew

    def validate_token(
        self,
        token: str,
        signing_key: Any,
        verify_signature: bool = True,
        verify_exp: bool = True,
        verify_aud: bool = True,
        verify_iss: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate JWT token.

        Args:
            token: JWT token to validate
            signing_key: Key for signature verification
            verify_signature: Whether to verify signature
            verify_exp: Whether to verify expiration
            verify_aud: Whether to verify audience
            verify_iss: Whether to verify issuer

        Returns:
            Decoded JWT payload

        Raises:
            TokenExpiredError: If token is expired
            InvalidTokenError: If token is invalid
            InvalidAudienceError: If audience is invalid
            InvalidIssuerError: If issuer is invalid
        """
        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_signature": verify_signature,
                    "verify_exp": verify_exp,
                    "verify_aud": verify_aud,
                    "verify_iss": verify_iss,
                },
                leeway=self.clock_skew,
            )
            return payload

        except ExpiredSignatureError as e:
            logger.warning(f"Token expired: {e}")
            raise TokenExpiredError("Token has expired")

        except InvalidAudienceError as e:
            logger.warning(f"Invalid audience: {e}")
            raise InvalidTokenError(f"Invalid audience: {e}")

        except InvalidIssuerError as e:
            logger.warning(f"Invalid issuer: {e}")
            raise InvalidTokenError(f"Invalid issuer: {e}")

        except InvalidSignatureError as e:
            logger.warning(f"Invalid signature: {e}")
            raise InvalidTokenError(f"Invalid signature: {e}")

        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise InvalidTokenError(f"Invalid token: {e}")

        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}")
            raise InvalidTokenError(f"Token validation failed: {e}")

    def validate_custom_claims(self, payload: Dict[str, Any]) -> None:
        """
        Validate custom claims specific to EGRC platform.

        Args:
            payload: Decoded JWT payload

        Raises:
            InvalidTokenError: If custom claims are invalid
        """
        # Validate required custom claims
        required_claims = ["sub", "preferred_username", "tenant_id"]
        for claim in required_claims:
            if claim not in payload:
                raise InvalidTokenError(f"Missing required claim: {claim}")

        # Validate tenant_id format
        tenant_id = payload.get("tenant_id")
        if tenant_id and not isinstance(tenant_id, str):
            raise InvalidTokenError("tenant_id must be a string")

        # Validate roles claim
        roles = payload.get("realm_access", {}).get("roles", [])
        if not isinstance(roles, list):
            raise InvalidTokenError("roles must be a list")

        # Validate resource access claims
        resource_access = payload.get("resource_access", {})
        if not isinstance(resource_access, dict):
            raise InvalidTokenError("resource_access must be a dictionary")


class TokenRevocationManager:
    """
    Token revocation manager for handling token blacklisting.

    Manages revoked tokens using Redis cache with TTL based on
    token expiration time.
    """

    def __init__(self, cache: SecurityCache):
        """
        Initialize token revocation manager.

        Args:
            cache: Security cache instance
        """
        self.cache = cache
        self.revocation_prefix = "revoked_token:"

    def revoke_token(
        self, token: str, expiration_time: Optional[datetime] = None
    ) -> None:
        """
        Revoke a token by adding it to the blacklist.

        Args:
            token: JWT token to revoke
            expiration_time: Token expiration time (if known)
        """
        try:
            # Create a hash of the token for storage
            token_hash = self._hash_token(token)

            # Calculate TTL based on expiration time
            ttl = self._calculate_ttl(expiration_time)

            # Store revoked token
            self.cache.set(f"{self.revocation_prefix}{token_hash}", "revoked", ttl=ttl)

            logger.info(f"Token revoked: {token_hash[:8]}...")

        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            raise

    def is_token_revoked(self, token: str) -> bool:
        """
        Check if a token is revoked.

        Args:
            token: JWT token to check

        Returns:
            True if token is revoked, False otherwise
        """
        try:
            token_hash = self._hash_token(token)
            return self.cache.exists(f"{self.revocation_prefix}{token_hash}")

        except Exception as e:
            logger.error(f"Failed to check token revocation: {e}")
            return False

    def _hash_token(self, token: str) -> str:
        """Create a hash of the token for storage."""
        import hashlib

        return hashlib.sha256(token.encode()).hexdigest()

    def _calculate_ttl(self, expiration_time: Optional[datetime]) -> int:
        """
        Calculate TTL for revoked token storage.

        Args:
            expiration_time: Token expiration time

        Returns:
            TTL in seconds
        """
        if expiration_time:
            # TTL until token expires + buffer
            ttl = int((expiration_time - datetime.utcnow()).total_seconds())
            return max(ttl, 0)
        else:
            # Default TTL of 24 hours
            return 86400


class JWTVerifier:
    """
    Main JWT verification class that orchestrates token validation.

    Combines JWKS caching, token validation, and revocation checking
    for comprehensive JWT verification.
    """

    def __init__(
        self,
        keycloak_url: str,
        realm: str,
        client_id: str,
        cache: Optional[SecurityCache] = None,
        jwks_cache_ttl: int = 3600,
    ):
        """
        Initialize JWT verifier.

        Args:
            keycloak_url: Keycloak server URL
            realm: Keycloak realm name
            client_id: Client ID for audience validation
            cache: Security cache instance
            jwks_cache_ttl: JWKS cache TTL in seconds
        """
        self.keycloak_url = keycloak_url
        self.realm = realm
        self.client_id = client_id
        self.cache = cache or SecurityCache()

        # Construct URLs
        self.issuer = f"{keycloak_url}/realms/{realm}"
        self.jwks_url = f"{self.issuer}/protocol/openid-connect/certs"

        # Initialize components
        self.jwks_cache = JWKSCache(self.jwks_url, jwks_cache_ttl)
        self.token_validator = TokenValidator(
            issuer=self.issuer,
            audience=client_id,
        )
        self.revocation_manager = TokenRevocationManager(self.cache)

    def verify_token(
        self,
        token: str,
        verify_signature: bool = True,
        verify_exp: bool = True,
        verify_aud: bool = True,
        verify_iss: bool = True,
        check_revocation: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify JWT token with comprehensive validation.

        Args:
            token: JWT token to verify
            verify_signature: Whether to verify signature
            verify_exp: Whether to verify expiration
            verify_aud: Whether to verify audience
            verify_iss: Whether to verify issuer
            check_revocation: Whether to check token revocation

        Returns:
            Decoded and validated JWT payload

        Raises:
            AuthenticationError: If token verification fails
            TokenExpiredError: If token is expired
            TokenRevokedError: If token is revoked
        """
        try:
            # Check token revocation first
            if check_revocation and self.revocation_manager.is_token_revoked(token):
                raise TokenRevokedError("Token has been revoked")

            # Get signing key
            signing_key = self.jwks_cache.get_signing_key(token)

            # Validate token
            payload = self.token_validator.validate_token(
                token=token,
                signing_key=signing_key,
                verify_signature=verify_signature,
                verify_exp=verify_exp,
                verify_aud=verify_aud,
                verify_iss=verify_iss,
            )

            # Validate custom claims
            self.token_validator.validate_custom_claims(payload)

            # Cache validated token for performance
            self._cache_validated_token(token, payload)

            logger.debug(
                f"Token verified successfully for user: {
                    payload.get('preferred_username')}"
            )
            return payload

        except (TokenExpiredError, TokenRevokedError, InvalidTokenError) as e:
            logger.warning(f"Token verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            raise AuthenticationError(f"Token verification failed: {e}")

    def revoke_token(self, token: str) -> None:
        """
        Revoke a token.

        Args:
            token: JWT token to revoke
        """
        try:
            # Get token expiration from payload
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = payload.get("exp")
            expiration_time = (
                datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            )

            # Revoke token
            self.revocation_manager.revoke_token(token, expiration_time)

        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            raise

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Get user information from token.

        Args:
            token: JWT token

        Returns:
            User information dictionary
        """
        try:
            payload = self.verify_token(token)
            return {
                "user_id": payload.get("sub"),
                "username": payload.get("preferred_username"),
                "email": payload.get("email"),
                "first_name": payload.get("given_name"),
                "last_name": payload.get("family_name"),
                "tenant_id": payload.get("tenant_id"),
                "roles": payload.get("realm_access", {}).get("roles", []),
                "client_roles": payload.get("resource_access", {}),
                "groups": payload.get("groups", []),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise AuthenticationError(f"Failed to get user info: {e}")

    def _cache_validated_token(self, token: str, payload: Dict[str, Any]) -> None:
        """
        Cache validated token for performance.

        Args:
            token: JWT token
            payload: Decoded token payload
        """
        try:
            # Calculate cache TTL based on token expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                exp_time = datetime.fromtimestamp(exp_timestamp)
                ttl = int((exp_time - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    token_hash = self.revocation_manager._hash_token(token)
                    self.cache.set(
                        f"validated_token:{token_hash}",
                        payload,
                        ttl=min(ttl, 300),  # Cache for max 5 minutes
                    )
        except Exception as e:
            logger.warning(f"Failed to cache validated token: {e}")

    def get_cached_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get cached validated token.

        Args:
            token: JWT token

        Returns:
            Cached token payload or None
        """
        try:
            token_hash = self.revocation_manager._hash_token(token)
            return self.cache.get(f"validated_token:{token_hash}")
        except Exception as e:
            logger.warning(f"Failed to get cached token: {e}")
            return None


# Global JWT verifier instance
_jwt_verifier: Optional[JWTVerifier] = None


def get_jwt_verifier() -> JWTVerifier:
    """
    Get global JWT verifier instance.

    Returns:
        JWT verifier instance
    """
    global _jwt_verifier
    if _jwt_verifier is None:
        _jwt_verifier = JWTVerifier(
            keycloak_url=settings.keycloak.url,
            realm=settings.keycloak.realm,
            client_id=settings.keycloak.client_id,
        )
    return _jwt_verifier


def verify_jwt_token(token: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to verify JWT token.

    Args:
        token: JWT token to verify
        **kwargs: Additional verification options

    Returns:
        Decoded and validated JWT payload
    """
    verifier = get_jwt_verifier()
    return verifier.verify_token(token, **kwargs)
