from _typeshed import Incomplete
from bosa_core.authentication.client.service.client_aware_service import ClientAwareService as ClientAwareService
from bosa_core.authentication.config import AuthenticationDbSettings as AuthenticationDbSettings
from bosa_core.cache.interface import CacheService as CacheService
from bosa_core.exception import InvalidClientException as InvalidClientException

class RevokeTokenService:
    """Revoke Token Service."""
    client_aware_service: Incomplete
    cache_service: Incomplete
    def __init__(self, client_aware_service: ClientAwareService, cache_service: CacheService) -> None:
        """Initialize the service.

        Args:
            client_aware_service (ClientAwareService): The client aware service
            cache_service (CacheService): The cache service
        """
    def revoke_token(self, api_key: str, access_token: str) -> bool:
        """Revoke a token.

        Args:
            api_key: The API key for client authentication
            access_token: The JWT access token to revoke

        Returns:
            bool: True if token was found and revoked, False otherwise

        Raises:
            InvalidClientException: If client is not found or token is invalid
        """
