"""portfolio_catalogue.py

Client wrapper for interacting with the Portfolio-Catalogue Service API.

This module exposes `PortfolioCatalogue`, a thin abstraction over the
shared :class:`bw_essentials.services.api_client.ApiClient` that collates
all URL templates and common logic required to communicate with the
Portfolio-Catalogue micro-service responsible for portfolio construction
and rebalancing operations.

Features
--------
- Centralised mapping of service endpoints.
- Uniform request/response logging using the shared API client helper.
- Simple, type-hinted public interface that hides low-level HTTP calls.

Example
-------
>>> from bw_essentials.services.portfolio_catalogue import PortfolioCatalogue
>>> client = PortfolioCatalogue(service_user="system")
>>> data = {
  "portfolioId": "BASKE_e3f7fc",
  "startDate": "2025-07-01",
  "endDate": "2025-07-10",
  "status": "active",
  "createdBy": "KP",
  "constituents": [
    {
      "symbol": "EROSMEDIA",
      "weight": 0.5,
      "isin": "INE416L01017",
      "status": "active",
      "rationale": "Hello"
    },
    {
      "symbol": "IDEA",
      "weight": 0.5,
      "isin": "INE669E01016",
      "status": "active",
      "rationale": "Hello"
    }
  ]
}
>>> response = client.create_rebalance(json=data)
>>> print(response)
"""

import logging
from typing import Optional, Dict, Any

from bw_essentials.constants.services import Services, PortfolioStatus
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class PortfolioCatalogue(ApiClient):
    """High-level client for the Portfolio-Catalogue Service.

    This class bundles together the logic for generating fully-qualified
    endpoint URLs and executing authenticated HTTP requests for
    portfolio rebalancing workflows.

    Attributes
    ----------
    base_url : str
        Resolved base URL for the Portfolio-Catalogue service obtained
        from configuration or environment variables.
    name : str
        Canonical service identifier used for logging and telemetry.
    urls : dict[str, str]
        Mapping of human-readable keys to relative endpoint paths.
    """

    def __init__(self, service_user: str):
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.PORTFOLIO_CATALOGUE.value)
        self.name = Services.PORTFOLIO_CATALOGUE.value
        self.urls = {
            "rebalance": "rebalance",
            "get_rebalance": "rebalance",
            "subscriptions_by_ids": "subscription-plan/list",
            "otp_subscriptions_by_ids": "one-time-plans/list"
        }

    def create_rebalance(self, json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit a rebalance request.

        Parameters
        ----------
        json : dict
            Request payload describing the rebalance parameters and
            portfolio metadata.

        Returns
        -------
        dict
            Parsed JSON response returned by the service.
        """
        logger.info("In - create_rebalance %s", json)
        data = self._post(
            url=self.base_url,
            endpoint=self.urls["rebalance"],
            json=json,
        )
        logger.info("%s", data)
        return data

    def rebalance(self, portfolio_id, status):
        """Fetch the latest rebalance record for a portfolio.

        Parameters
        ----------
        portfolio_id : str
            Portfolio identifier.
        status : str
            Portfolio status filter.

        Returns
        -------
        dict
            The first record from the service response's 'data' list.
        """
        logger.info("In - rebalance portfolio_id=%s status=%s", portfolio_id, status)
        data = self._get(
            url=self.base_url,
            endpoint=self.urls["get_rebalance"],
            params={'portfolioId': portfolio_id, 'status': status}
        )
        logger.info("rebalance response: %s", data)
        return data.get('data')[0]

    def get_rebalance_due_date(self, portfolio_id, status):
        """Return the next rebalance date for an active portfolio, else None.

        Parameters
        ----------
        portfolio_id : str
            Portfolio identifier.
        status : str
            Portfolio status.

        Returns
        -------
        str | None
            The next rebalance date string if available; otherwise None.
        """
        logger.info(
            "In - get_rebalance_due_date portfolio_id=%s status=%s",
            portfolio_id,
            status,
        )
        if status in PortfolioStatus.ACTIVE_FOR_SUBSCRIBED_USER.value:
            rebalance_history = self.rebalance(portfolio_id, status)
            next_rebalance_date = (
                rebalance_history.get('nextRebalanceDate') if rebalance_history else None
            )
            logger.info("nextRebalanceDate=%s", next_rebalance_date)
            return next_rebalance_date
        logger.info("get_rebalance_due_date not applicable for status=%s", status)
        return None

    def get_subscriptions_by_ids(self, plans_ids: list):
        """
        Fetch multiple subscriptions by their plan IDs.

        This method constructs the request URL using the configured base URL
        and the `subscriptions_by_ids` endpoint. It sends a POST request with
        the given list of `plans_ids` in the request body, logs the process,
        and returns the subscription data.

        Args:
            plans_ids (list[str] | list[int]): A list of subscription plan IDs
                to fetch details for.

        Returns:
            list[dict]: A list of subscription data dictionaries if available,
            otherwise an empty list.
        """
        logger.info(f"In get_subscriptions_by_ids {plans_ids =}")
        url = f"{self.base_url}"
        payload = {
            "planId": plans_ids
        }
        response = self._post(url=url, endpoint=self.urls.get('subscriptions_by_ids'), json=payload)
        logger.info(f"Successfully fetched subscriptions by ids data. {response =}")
        return response.get('data', [])

    def get_otp_subscriptions_by_ids(self, plans_ids: list):
        """
        Fetch OTP subscription details for multiple plan IDs.

        This method sends a POST request to the `otp_subscriptions_by_ids`
        endpoint with the given list of plan IDs in the request body.
        It logs the request and response flow and returns the extracted
        subscription data.

        Args:
            plans_ids (list[str] | list[int]): A list of OTP subscription plan IDs
                to retrieve details for.

        Returns:
            list[dict]: A list of OTP subscription data dictionaries if available,
            otherwise an empty list.
        """
        logger.info(f"In get_otp_subscriptions_by_ids {plans_ids =}")
        url = f"{self.base_url}"
        payload = {
            "id": plans_ids
        }
        response  = self._post(url=url, endpoint=self.urls.get('otp_subscriptions_by_ids'), json=payload)
        logger.info(f"Successfully fetched otp subscriptions by ids data. {response =}")
        return response.get('data', [])