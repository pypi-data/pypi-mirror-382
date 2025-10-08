from decimal import Decimal
from typing import Union
from .warnings import get_warn_once_func

Numberish = Union[int, float, Decimal, str]

warn_once = get_warn_once_func()


def _to_decimal(number: Numberish) -> Decimal:
    if isinstance(number, Decimal):
        return number
    if isinstance(number, int):
        return Decimal(number)
    if isinstance(number, float):
        warn_once(f"Converting float ({number}) to Decimal. This may result in loss of precision.")
        return Decimal(str(number))
    return Decimal(str(number))


def is_multiple_of_tick(price: Numberish, tick_size: Numberish) -> bool:
    """
    Checks if the price is a multiple of the tick size.

    All the numbers are converted to Decimal before the operation is performed.

    :param price: The price to check.
    :param tick_size: The tick size to check against.
    :return: True if the price is a multiple of the tick size, False otherwise.
    """
    price = _to_decimal(price)
    tick_size = _to_decimal(tick_size)
    # tick_size == 0 means infinite precision, where all numbers are multiples of each other
    if tick_size == 0:
        return True
    return price % tick_size == 0


def floor_to_tick(price: Numberish, tick_size: Numberish) -> Decimal:
    """
    Rounds the price down to the nearest possible price that is a multiple of the tick size.

    All the numbers are converted to Decimal before the operation is performed.

    :param price: The price to round down.
    :param tick_size: The tick size to round to.
    :return: The rounded down price.
    """
    price = _to_decimal(price)
    tick_size = _to_decimal(tick_size)
    if is_multiple_of_tick(price, tick_size):
        return price
    return price // tick_size * tick_size


def ceil_to_tick(price: Numberish, tick_size: Numberish) -> Decimal:
    """
    Rounds the price up to the nearest possible price that is a multiple of the tick size.

    All the numbers are converted to Decimal before the operation is performed.

    :param price: The price to round up.
    :param tick_size: The tick size to round to.
    :return: The rounded up price.
    """
    price = _to_decimal(price)
    tick_size = _to_decimal(tick_size)
    if is_multiple_of_tick(price, tick_size):
        return price
    return price // tick_size * tick_size + tick_size


def round_to_tick(price: Numberish, tick_size: Numberish) -> Decimal:
    """
    Rounds the price to the nearest possible price that is a multiple of the tick size.

    All the numbers are converted to Decimal before the operation is performed.

    :param price: The price to round.
    :param tick_size: The tick size to round to.
    :return: The rounded price.
    """
    price = _to_decimal(price)
    tick_size = _to_decimal(tick_size)
    if is_multiple_of_tick(price, tick_size):
        return price
    return round(price / tick_size) * tick_size
