import logging
from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class JobScheduler(ApiClient):
    """
    Class for making API calls to the Job Scheduler Service.

    Args:
    user (str): The user for whom the API calls are being made.
    """

    def __init__(self, user, tenant_id: str = None):
        """
        Initialize the Job Scheduler object.

        Args:
        user (str): The user for whom the API calls are being made.
        """
        super().__init__(user)
        self.base_url = self.get_base_url(Services.JOB_SCHEDULER.value)
        self.api_key = self.get_api_key(Services.JOB_SCHEDULER.value)
        self.name = Services.JOB_SCHEDULER.value
        self.tenant_id = tenant_id
        self.urls = {
            "process_user_profile": "taskmanager/process/user-portfolios/"
        }

    def _headers(self):
        """
        Prepares headers for API calls.

        Returns:
            dict: Headers
        """
        self.headers.update({
            'Content-Type': 'application/json',
            **({'X-Tenant-ID': self.tenant_id} if self.tenant_id else {}),
            'x-api-key': self.api_key
        })

    def process_user_profile(self, data):
        """
        Send a request to process a user profile.

        This method prepares the required headers and sends a POST request
        to the `process_user_profile` endpoint with the provided user data.

        Args:
            data (dict): A dictionary containing user profile information
                to be sent in the request body.

        Returns:
            None: The method does not return a value.
        """
        logger.info(f"In - process_user_profile {self.user =}")
        self._headers()
        self._post(url=self.base_url, endpoint=self.urls.get('process_user_profile'), json=data)
        logger.info(f"Out - process_user_profile")