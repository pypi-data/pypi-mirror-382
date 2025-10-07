import logging
from bw_essentials.services.api_client import ApiClient
from bw_essentials.constants.services import Services

logger = logging.getLogger(__name__)


class Payment(ApiClient):

    def __init__(self, service_user: str):
        super().__init__(service_user)
        self.urls = {
            "get_subscription": "user-subscription",
        }
        self.name = Services.PAYMENT.value
        self.base_url = self.get_base_url(Services.PAYMENT.value)

    def get_subscription(self, user_id):
        """
        Fetch subscription details for a given user.

        This method constructs the request URL using the configured base URL
        and the `get_subscription` endpoint. It sends a GET request with
        the provided `user_id` as a query parameter, logs the process,
        and returns the subscription data payload.

        Args:
            user_id (str | int): Unique identifier of the user whose
                subscription details need to be fetched.

        Returns:
            dict | None: A dictionary containing the subscription data if
            available, otherwise `None`.
        """
        logger.info(f"Received request to get subscription with {user_id =}")
        url = f"{self.base_url}"
        subscription = self._get(url=url, endpoint=self.urls.get('get_subscription'), params={'userId': user_id})
        logger.info(f"Successfully fetched subscription data. {subscription =}")
        return subscription.get('data')