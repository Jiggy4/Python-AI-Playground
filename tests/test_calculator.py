import math

import pytest

from app import evaluate_expression


def test_basic_arithmetic():
    assert evaluate_expression("2 + 3 * 4") == 14


def test_parentheses_and_power():
    assert evaluate_expression("(2 + 3)^2") == 25


def test_trigonometry_and_logs():
    assert evaluate_expression("sin(pi / 2)") == pytest.approx(1.0)
    assert evaluate_expression("log(100)") == pytest.approx(2.0)
    assert evaluate_expression("ln(e)") == pytest.approx(1.0)


def test_root_and_constant_helpers():
    assert evaluate_expression("sqrt(9)") == pytest.approx(3.0)
    assert evaluate_expression("cbrt(27)") == pytest.approx(3.0)
    assert evaluate_expression("pow(2, 3)") == pytest.approx(8.0)
