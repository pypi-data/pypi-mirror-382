from dataclasses import dataclass


@dataclass
class User:
    """A class representing a user.

    Args:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        username (str): The user's username.
        email (str): The user's email address.
        phone_number (str): The user's phone number.
        location (str): The user's location.
    """

    first_name: str = ""
    last_name: str = ""
    username: str = ""
    email: str = ""
    phone_number: str = ""
    location: str = ""


@dataclass
class Transaction:
    """A class representing a transaction.

    Args:
        amount (int): The transaction amount.
        payment_method (str, optional): The payment method. Defaults to "".
        callback_url (str, optional): The callback URL. Defaults to "".
        currency (str, optional): The currency. Defaults to "KES".
        narration (str, optional): The transaction narration. Defaults to "".
        provider (str, optional): The payment provider. Defaults to "".
        channel (str, optional): The transaction channel. Defaults to "".
        business_account (str, optional): The business account. Defaults to "".
        business_number (str, optional): The business number. Defaults to "".
        trans_type (str, optional): The transaction type. Defaults to "".
    """

    amount: int
    payment_method: str = ""
    callback_url: str = ""
    currency: str = "KES"
    narration: str = ""
    provider: str = ""
    channel: str = ""
    business_account: str = ""
    business_number: str = ""
    trans_type: str = ""
