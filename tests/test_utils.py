import pytest

from src.utils import find_miles, find_model, find_year

MODELS = {"accord", "camry", "civic", "corolla"}


class TestFindModel:
    def test_basic(self):
        assert find_model("my honda accord", MODELS) == "accord"

    def test_case_insensitive(self):
        assert find_model("my honda Accord", MODELS) == "accord"

    def test_non_model(self):
        assert find_model("Harley", MODELS) is None


class TestFindYear:
    def test_basic(self):
        assert find_year("hello 1999") == 1999

    def test_skip_too_low(self):
        # 1979 is outside the valid range; 2014 is returned
        assert find_year("1979 2014") == 2014

    def test_return_first(self):
        assert find_year("2013 2014") == 2013

    def test_return_none_for_out_of_range(self):
        assert find_year("1979") is None

    def test_recent_year(self):
        assert find_year("2022 Honda Civic") == 2022


class TestFindMiles:
    def test_basic(self):
        assert find_miles("I have 20000 miles") == 20000

    def test_case_insensitive(self):
        assert find_miles("I have 20000 Miles") == 20000

    def test_comma(self):
        assert find_miles("I have 20,000 miles") == 20000

    def test_miles_label(self):
        assert find_miles("my miles: 20,000") == 20000

    def test_mileage_label(self):
        assert find_miles("my mileage: 20,000 xx") == 20000

    def test_spaces(self):
        assert find_miles("mileage  20,000 adsfadsf") == 20000

    def test_characters1(self):
        assert find_miles("mileage,, 20,000 adsfadsf") == 20000

    def test_characters2(self):
        assert find_miles("20,000 .?miles") == 20000

    def test_k_suffix(self):
        assert find_miles("20k .?miles") == 20000

    def test_standalone_number_no_match(self):
        assert find_miles("20,000") is None
