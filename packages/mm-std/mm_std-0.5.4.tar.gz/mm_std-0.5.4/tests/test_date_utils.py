from datetime import UTC, datetime, timedelta

import pytest

from mm_std import parse_date, utc_delta, utc_now


class TestUtcNow:
    def test_returns_utc_datetime(self):
        result = utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC

    def test_consecutive_calls_increase(self):
        first = utc_now()
        second = utc_now()
        assert second >= first


class TestUtcDelta:
    def test_positive_days(self):
        base_time = utc_now()
        result = utc_delta(days=5)
        expected_min = base_time + timedelta(days=5)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_positive_hours(self):
        base_time = utc_now()
        result = utc_delta(hours=3)
        expected_min = base_time + timedelta(hours=3)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_positive_minutes(self):
        base_time = utc_now()
        result = utc_delta(minutes=30)
        expected_min = base_time + timedelta(minutes=30)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_positive_seconds(self):
        base_time = utc_now()
        result = utc_delta(seconds=45)
        expected_min = base_time + timedelta(seconds=45)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_negative_values_for_past_time(self):
        base_time = utc_now()
        result = utc_delta(days=-2, hours=-5)
        expected_max = base_time - timedelta(days=2, hours=5) + timedelta(seconds=1)
        expected_min = expected_max - timedelta(seconds=2)
        assert expected_min <= result <= expected_max

    def test_combined_parameters(self):
        base_time = utc_now()
        result = utc_delta(days=1, hours=2, minutes=3, seconds=4)
        expected_min = base_time + timedelta(days=1, hours=2, minutes=3, seconds=4)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_none_values_ignored(self):
        base_time = utc_now()
        result = utc_delta(days=None, hours=1, minutes=None, seconds=None)
        expected_min = base_time + timedelta(hours=1)
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_zero_values(self):
        base_time = utc_now()
        result = utc_delta(days=0, hours=0, minutes=0, seconds=0)
        expected_min = base_time
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max

    def test_all_none_parameters(self):
        base_time = utc_now()
        result = utc_delta()
        expected_min = base_time
        expected_max = expected_min + timedelta(seconds=1)
        assert expected_min <= result <= expected_max


class TestParseDate:
    def test_iso_format_with_microseconds_and_timezone(self):
        result = parse_date("2023-12-25 14:30:45.123456+02:00")
        expected = datetime(2023, 12, 25, 14, 30, 45, 123456, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected

    def test_iso_t_format_with_microseconds_and_timezone(self):
        result = parse_date("2023-12-25T14:30:45.123456+02:00")
        expected = datetime(2023, 12, 25, 14, 30, 45, 123456, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected

    def test_iso_format_with_microseconds_no_timezone(self):
        result = parse_date("2023-12-25 14:30:45.123456")
        expected = datetime(2023, 12, 25, 14, 30, 45, 123456)
        assert result == expected

    def test_iso_t_format_with_timezone(self):
        result = parse_date("2023-12-25T14:30:45+02:00")
        expected = datetime(2023, 12, 25, 14, 30, 45, 0, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected

    def test_basic_format_with_timezone(self):
        result = parse_date("2023-12-25 14:30:45+02:00")
        expected = datetime(2023, 12, 25, 14, 30, 45, 0, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected

    def test_basic_format_no_timezone(self):
        result = parse_date("2023-12-25 14:30:45")
        expected = datetime(2023, 12, 25, 14, 30, 45)
        assert result == expected

    def test_format_with_minutes_and_timezone(self):
        result = parse_date("2023-12-25 14:30+02:00")
        expected = datetime(2023, 12, 25, 14, 30, 0, 0, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected

    def test_format_with_minutes_no_timezone(self):
        result = parse_date("2023-12-25 14:30")
        expected = datetime(2023, 12, 25, 14, 30)
        assert result == expected

    def test_date_only_format(self):
        result = parse_date("2023-12-25")
        expected = datetime(2023, 12, 25)
        assert result == expected

    def test_slash_date_format(self):
        result = parse_date("2023/12/25")
        expected = datetime(2023, 12, 25)
        assert result == expected

    def test_z_suffix_conversion(self):
        result = parse_date("2023-12-25T14:30:45Z")
        expected = datetime(2023, 12, 25, 14, 30, 45, 0, UTC)
        assert result == expected

    def test_lowercase_z_suffix_conversion(self):
        result = parse_date("2023-12-25T14:30:45z")
        expected = datetime(2023, 12, 25, 14, 30, 45, 0, UTC)
        assert result == expected

    def test_ignore_tz_parameter_with_timezone(self):
        result = parse_date("2023-12-25T14:30:45+02:00", ignore_tz=True)
        expected = datetime(2023, 12, 25, 14, 30, 45)
        assert result == expected
        assert result.tzinfo is None

    def test_ignore_tz_parameter_without_timezone(self):
        result = parse_date("2023-12-25 14:30:45", ignore_tz=True)
        expected = datetime(2023, 12, 25, 14, 30, 45)
        assert result == expected
        assert result.tzinfo is None

    def test_ignore_tz_parameter_false_preserves_timezone(self):
        result = parse_date("2023-12-25T14:30:45+02:00", ignore_tz=False)
        expected = datetime(2023, 12, 25, 14, 30, 45, 0, datetime.strptime("+02:00", "%z").tzinfo)
        assert result == expected
        assert result.tzinfo is not None

    def test_invalid_format_raises_value_error(self):
        with pytest.raises(ValueError, match="Time data 'invalid-date' does not match any known format"):
            parse_date("invalid-date")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError, match="Time data '' does not match any known format"):
            parse_date("")

    def test_partial_match_raises_value_error(self):
        with pytest.raises(ValueError, match="Time data '2023-13-45' does not match any known format"):
            parse_date("2023-13-45")
