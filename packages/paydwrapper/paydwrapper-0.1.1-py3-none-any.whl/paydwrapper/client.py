import base64
import logging

import requests

from paydwrapper.models import Transaction, User

logger: logging.Logger = logging.getLogger(__name__)


class PaydClient:
    """A client for interacting with the Payd API.

    Args:
        username (str): The username for authentication.
        password (str): The password for authentication.
        payd_user (str): Username used to authenticate with payd. (@top right corner)
    """

    def __init__(self, username, password, payd_user):
        self.acc_username = username
        self.acc_password = password
        self.payd_username = payd_user

    def build_auth_headers(self) -> dict:
        """Builds the authentication headers for API requests.

        Returns:
            dict: A dictionary containing the authentication headers.
        """
        creds = f"{self.acc_username}:{self.acc_password}"
        encoded_creds = base64.b64encode(creds.encode())
        return {"Authorization": f"Basic {encoded_creds.decode()}"}

    def trigger_card_payment(self, user: User, transaction: Transaction) -> dict:
        """Triggers a card payment.

        Args:
            user (User): The user making the payment. The following attributes are required:
                - email (str)
                - first_name (str)
                - last_name (str)
                - location (str)
                - username (str)
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - provider (str)
                - callback_url (str)
                - narration (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v1/payments"
        paylod = {
            "amount": transaction.amount,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "location": user.location,
            "username": self.payd_username,
            "payment_method": "card",
            "provider": transaction.provider,
            "callback_url": transaction.callback_url,
            "reason": transaction.narration,
            "phone": user.phone_number,
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def trigger_p2p_payment(self, user: User, transaction: Transaction) -> dict:
        """Triggers a peer-to-peer payment.

        Args:
            user (User): The user making the payment. The following attributes are required:
                - username (str)
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - narration (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v2/p2p"
        paylod = {
            "amount": transaction.amount,
            "receiver_username": user.username,
            "narration": transaction.narration,
            "phone_number": user.phone_number,
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def trigger_payment_request(self, user: User, transaction: Transaction) -> dict:
        """Triggers a payment request.

        Args:
            user (User): The user to request payment from. The following attributes are required:
                - username (str)
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - narration (str)
                - currency (str)
                - callback_url (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v2/payments"
        paylod = {
            "username": self.payd_username,
            "channel": "MPESA",
            "amount": transaction.amount,
            "phone_number": user.phone_number,
            "narration": transaction.narration,
            "currency": transaction.currency,
            "callback_url": transaction.callback_url,
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def trigger_paybill_request(self, user: User, transaction: Transaction) -> dict:
        """Triggers a paybill request.

        Args:
            user (User): The user making the payment. The following attributes are required:
                - username (str)
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - currency (str)
                - narration (str)
                - business_account (str)
                - business_number (str)
                - callback_url (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v3/withdrawal"
        paylod = {
            "username": self.payd_username,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "phone_number": user.phone_number,
            "narration": transaction.narration,
            "transaction_channel": "bank",
            "channel": "bank",
            "business_account": transaction.business_account,
            "business_number": transaction.business_number,
            "callback_url": transaction.callback_url,
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def trigger_till_request(self, user: User, transaction: Transaction) -> dict:
        """Triggers a till request.

        Args:
            user (User): The user making the payment. The following attributes are required:
                - username (str)
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - currency (str)
                - narration (str)
                - business_account (str)
                - callback_url (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v3/withdrawal"
        paylod = {
            "username": self.payd_username,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "phone_number": user.phone_number,
            "narration": transaction.narration,
            "transaction_channel": "bank",
            "channel": "bank",
            "business_account": transaction.business_account,
            "callback_url": transaction.callback_url,
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def trigger_withdrawal_request(self, user: User, transaction: Transaction) -> dict:
        """Triggers a withdrawal request.

        Args:
            user (User): The user making the withdrawal. The following attributes are required:
                - phone_number (str)
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - narration (str)
                - callback_url (str)

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v2/withdrawal"
        paylod = {
            "amount": transaction.amount,
            "phone_number": user.phone_number,
            "narration": transaction.narration,
            "callback_url": transaction.callback_url,
            "channel": "MPESA",
        }
        headers = self.build_auth_headers()
        response = requests.post(url, data=paylod, headers=headers)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def query_transactions(self) -> dict:
        """Queries the transaction history.

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v1/accounts/transaction-requests"
        payload = {}
        headers = self.build_auth_headers()
        response = requests.get(url, headers=headers, data=payload)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()

    def query_transaction_cost(self, transaction: Transaction) -> dict:
        """Queries the cost of a transaction.

        Args:
            transaction (Transaction): The transaction details. The following attributes are required:
                - amount (int)
                - trans_type (str): One of 'withdrawal', 'receipt', or 'remittance'.
                - channel (str): One of 'mobile', 'bank', 'card', or 'payd'.

        Returns:
            dict: The API response.
        """
        url = "https://api.mypayd.app/api/v1/transaction-costs"
        params = {
            "amount": transaction.amount,
            "type": transaction.trans_type,
            "channel": transaction.channel,
        }
        headers = self.build_auth_headers()
        response = requests.get(url, headers=headers, params=params)
        if not response.ok:
            logger.error(f"{response.status_code}: {response.text}")
            if not response.json():
                return {}
        return response.json()
