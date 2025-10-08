import random
from datetime import datetime, timedelta
from decimal import Decimal


def random_decimal(from_value: Decimal, to_value: Decimal) -> Decimal:
    """Generate a random decimal between from_value and to_value.

    Uses integer arithmetic to preserve decimal precision instead of
    converting to float which would introduce rounding errors.

    Args:
        from_value: Minimum value (inclusive)
        to_value: Maximum value (inclusive)

    Returns:
        Random decimal in the specified range

    Raises:
        ValueError: If from_value > to_value
    """
    if from_value > to_value:
        raise ValueError("from_value must be <= to_value")

    # Work with integers to preserve precision
    from_exp = from_value.as_tuple().exponent
    to_exp = to_value.as_tuple().exponent
    from_scale = max(0, -from_exp if isinstance(from_exp, int) else 0)
    to_scale = max(0, -to_exp if isinstance(to_exp, int) else 0)
    scale = max(from_scale, to_scale)

    multiplier = 10**scale
    from_int = int(from_value * multiplier)
    to_int = int(to_value * multiplier)

    random_int = random.randint(from_int, to_int)  # nosec B311
    return Decimal(random_int) / Decimal(multiplier)


def random_datetime(
    from_time: datetime,
    *,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """Generate a random datetime within a specified time range.

    Returns a random datetime between from_time and from_time + offset,
    where offset is calculated from the provided hours, minutes, and seconds.

    Args:
        from_time: Base datetime (inclusive)
        hours: Maximum hours offset (default: 0)
        minutes: Maximum minutes offset (default: 0)
        seconds: Maximum seconds offset (default: 0)

    Returns:
        Random datetime in the specified range

    Raises:
        ValueError: If any offset value is negative
    """
    if hours < 0 or minutes < 0 or seconds < 0:
        raise ValueError("Range values must be non-negative")

    total_seconds = hours * 3600 + minutes * 60 + seconds
    if total_seconds == 0:
        return from_time

    random_seconds = random.uniform(0, total_seconds)  # nosec B311
    return from_time + timedelta(seconds=random_seconds)
