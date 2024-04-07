from decimal import Decimal
from typing import NamedTuple

class PaymentBalance(NamedTuple):
    """ Payment Balance class

    Args:
        NamedTuple (_type_): _description_
    """
    car_identity: str
    available_credit: Decimal