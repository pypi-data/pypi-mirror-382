from _typeshed import Incomplete
from bosa_core.authentication.client.service.client_aware_service import ClientAwareService as ClientAwareService
from bosa_core.authentication.config import AuthenticationDbSettings as AuthenticationDbSettings
from bosa_core.cache.interface import CacheService as CacheService
from bosa_core.exception import InvalidClientException as InvalidClientException, UnauthorizedException as UnauthorizedException
from uuid import UUID

class VerifyTokenService:
    """Verify Token Service."""
    client_aware_service: Incomplete
    cache_service: Incomplete
    def __init__(self, client_aware_service: ClientAwareService, cache_service: CacheService) -> None:
        """Initialize the service.

        Args:
            client_aware_service (ClientAwareService): The client aware service
            cache_service (CacheService): The cache service
        """
    def verify_token_and_get_user_id(self, api_key: str, access_token: str) -> UUID:
        """Verify token and get user ID.

        Args:
            api_key (str): The API key for client authentication
            access_token (str): The JWT access token to verify

        Returns:
            UUID: The user ID

        Raises:
            InvalidClientException: If the client is not found
            JWTClaimsError: If the token claims are invalid
            ExpiredSignatureError: If the token has expired
        """
