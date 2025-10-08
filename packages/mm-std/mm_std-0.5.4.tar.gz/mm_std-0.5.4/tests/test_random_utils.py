from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from mm_std import random_datetime, random_decimal


class TestRandomDecimal:
    def test_generates_value_in_range(self) -> None:
        from_val = Decimal("1.5")
        to_val = Decimal("2.5")

        for _ in range(100):
            result = random_decimal(from_val, to_val)
            assert from_val <= result <= to_val
            assert isinstance(result, Decimal)

    def test_equal_values_returns_same_value(self) -> None:
        value = Decimal("3.14159")
        result = random_decimal(value, value)
        assert result == value

    def test_preserves_decimal_precision(self) -> None:
        # Test with high precision values
        from_val = Decimal("1.123456789")
        to_val = Decimal("1.987654321")

        result = random_decimal(from_val, to_val)
        # Result should maintain precision, not be rounded to float precision
        assert len(str(result).split(".")[-1]) >= 6

    def test_handles_different_scales(self) -> None:
        from_val = Decimal("1.5")  # 1 decimal place
        to_val = Decimal("2.555")  # 3 decimal places

        result = random_decimal(from_val, to_val)
        assert from_val <= result <= to_val
        # Should use the higher precision (3 decimal places)
        str_result = str(result)
        if "." in str_result:
            decimal_places = len(str_result.split(".")[-1])
            assert decimal_places <= 3

    def test_raises_error_when_from_greater_than_to(self) -> None:
        with pytest.raises(ValueError, match="from_value must be <= to_value"):
            random_decimal(Decimal(10), Decimal(5))

    def test_works_with_negative_values(self) -> None:
        from_val = Decimal("-5.5")
        to_val = Decimal("-1.1")

        result = random_decimal(from_val, to_val)
        assert from_val <= result <= to_val

    def test_works_with_large_values(self) -> None:
        from_val = Decimal("1000000.123")
        to_val = Decimal("9999999.999")

        result = random_decimal(from_val, to_val)
        assert from_val <= result <= to_val


class TestRandomDatetime:
    def test_zero_offset_returns_original_time(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        result = random_datetime(base_time)
        assert result == base_time

    def test_generates_time_within_hours_range(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        max_time = base_time + timedelta(hours=5)

        for _ in range(50):
            result = random_datetime(base_time, hours=5)
            assert base_time <= result <= max_time

    def test_generates_time_within_minutes_range(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        max_time = base_time + timedelta(minutes=30)

        for _ in range(50):
            result = random_datetime(base_time, minutes=30)
            assert base_time <= result <= max_time

    def test_generates_time_within_seconds_range(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        max_time = base_time + timedelta(seconds=45)

        for _ in range(50):
            result = random_datetime(base_time, seconds=45)
            assert base_time <= result <= max_time

    def test_combines_all_offset_types(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        max_time = base_time + timedelta(hours=2, minutes=30, seconds=45)

        for _ in range(50):
            result = random_datetime(base_time, hours=2, minutes=30, seconds=45)
            assert base_time <= result <= max_time

    def test_raises_error_for_negative_hours(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        with pytest.raises(ValueError, match="Range values must be non-negative"):
            random_datetime(base_time, hours=-1)

    def test_raises_error_for_negative_minutes(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        with pytest.raises(ValueError, match="Range values must be non-negative"):
            random_datetime(base_time, minutes=-1)

    def test_raises_error_for_negative_seconds(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0)
        with pytest.raises(ValueError, match="Range values must be non-negative"):
            random_datetime(base_time, seconds=-1)

    def test_works_with_microseconds_precision(self) -> None:
        base_time = datetime(2025, 6, 6, 12, 0, 0, 123456)

        result = random_datetime(base_time, seconds=1)
        # Should preserve microseconds in base time when no additional offset
        assert result >= base_time
