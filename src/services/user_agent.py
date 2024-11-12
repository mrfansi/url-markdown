import requests
from .logger import LoggerService
from ..interfaces.user_agent import UserAgentServiceInterface
import os
from dotenv import load_dotenv

class UserAgentService(UserAgentServiceInterface):
    def __init__(self):

        load_dotenv()
        
        self.logger = LoggerService()
        self.api_url = os.getenv('USER_AGENT_API_URL', 'https://api.apilayer.com/user_agent/generate')
        self.headers = {
            "apikey": os.getenv('USER_AGENT_API_KEY')
        }
        self.params = {
            "windows": "true",
            "linux": "true",
            "mac": "true"
        }
    
    def get_user_agent(self) -> str | None:
        try:
            self.logger.info(f"Fetching user agent from {self.api_url}")
            response = requests.get(self.api_url, headers=self.headers, params=self.params)
            response.raise_for_status()
            data = response.json()
            user_agent = data.get("ua")
            self.logger.info(f"Successfully fetched user agent: {user_agent}")
            return user_agent
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch user agent: {e}")
            return None

if __name__ == "__main__":
    service = UserAgentService()
    ua = service.get_user_agent()
    if ua:
        print(ua)
