
from abc import ABC, abstractmethod

class UserAgentServiceInterface(ABC):
    @abstractmethod
    def get_user_agent(self) -> str | None:
        """
        Fetch a user agent string from the service
        Returns:
            str | None: A user agent string if successful, None otherwise
        """
        pass