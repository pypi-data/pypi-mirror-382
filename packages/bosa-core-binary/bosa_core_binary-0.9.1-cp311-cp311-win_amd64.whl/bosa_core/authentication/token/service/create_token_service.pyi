from _typeshed import Incomplete
from bosa_core.authentication.config import AuthenticationDbSettings as AuthenticationDbSettings
from bosa_core.authentication.token.repository.models import TokenComplete as TokenComplete
from bosa_core.authentication.user.repository.models import User as User
from bosa_core.cache.interface import CacheService as CacheService

class CreateTokenService:
    """Create Token Service."""
    cache_service: Incomplete
    def __init__(self, cache_service: CacheService) -> None:
        """Initialize the service.

        Args:
            cache_service (CacheService): The cache service
        """
    def create_token(self, user: User) -> TokenComplete:
        """Create token.

        Args:
            user: The user

        Returns:
            TokenComplete: The token complete
        """
