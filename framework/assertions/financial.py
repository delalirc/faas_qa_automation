"""
Financial calculation assertions for FAAS QA Testing

Provides assertions specifically for financial calculations.
"""

from decimal import Decimal
from typing import Union


def assert_currency_precision(amount: Decimal, expected_decimals: int = 2):
    """
    Assert that a currency amount has correct precision

    Args:
        amount: Amount to check
        expected_decimals: Expected number of decimal places (default 2)

    Raises:
        AssertionError: If precision is incorrect
    """
    # Check that amount has at most expected_decimals decimal places
    exponent = amount.as_tuple().exponent
    assert exponent >= -expected_decimals, \
        f"Amount {amount} has {abs(exponent)} decimal places, expected at most {expected_decimals}"


def assert_calculation_accuracy(
    actual: Decimal,
    expected: Decimal,
    tolerance: Decimal = Decimal('0.01'),
    message: str = "Calculation accuracy"
):
    """
    Assert that a calculation result is within tolerance of expected

    Args:
        actual: Actual calculation result
        expected: Expected calculation result
        tolerance: Acceptable difference (default 0.01)
        message: Error message prefix

    Raises:
        AssertionError: If difference exceeds tolerance
    """
    difference = abs(actual - expected)
    assert difference <= tolerance, \
        f"{message}: Expected {expected}, got {actual}, difference {difference} exceeds tolerance {tolerance}"


def assert_positive_amount(amount: Decimal, message: str = "Amount must be positive"):
    """
    Assert that an amount is positive

    Args:
        amount: Amount to check
        message: Error message

    Raises:
        AssertionError: If amount is not positive
    """
    assert amount > 0, f"{message}: {amount} is not positive"


def assert_percentage_range(
    percentage: Decimal,
    min_value: Decimal = Decimal('0'),
    max_value: Decimal = Decimal('100'),
    message: str = "Percentage out of range"
):
    """
    Assert that a percentage is within valid range

    Args:
        percentage: Percentage to check
        min_value: Minimum valid value (default 0)
        max_value: Maximum valid value (default 100)
        message: Error message

    Raises:
        AssertionError: If percentage is out of range
    """
    assert min_value <= percentage <= max_value, \
        f"{message}: {percentage} is not between {min_value} and {max_value}"


def assert_reconciliation(
    total: Decimal,
    components: list[Decimal],
    tolerance: Decimal = Decimal('0.01'),
    message: str = "Reconciliation failed"
):
    """
    Assert that a total reconciles with its components

    Args:
        total: Total amount
        components: List of component amounts
        tolerance: Acceptable difference (default 0.01)
        message: Error message prefix

    Raises:
        AssertionError: If components don't sum to total
    """
    sum_components = sum(components)
    difference = abs(total - sum_components)
    assert difference <= tolerance, \
        f"{message}: Total {total} does not match sum of components {sum_components}, difference {difference}"
