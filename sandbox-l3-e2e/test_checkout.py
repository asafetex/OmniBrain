import checkout


def test_validate_order_accepts_valid_payload():
    assert checkout.validate_order(10, "tok_12345", "BRL")


def test_validate_order_accepts_lowercase_currency():
    assert checkout.validate_order(10, "tok_12345", "brl")


def test_validate_order_rejects_non_positive_total():
    assert not checkout.validate_order(0, "tok_12345", "BRL")


def test_validate_order_rejects_invalid_token():
    assert not checkout.validate_order(15, "short", "BRL")


def test_validate_order_rejects_token_without_prefix():
    assert not checkout.validate_order(15, "abcd1234", "BRL")


def test_validate_order_rejects_token_with_newline():
    assert not checkout.validate_order(15, "tok_12\n345", "BRL")


def test_validate_order_accepts_token_with_dash_and_underscore():
    assert checkout.validate_order(15, "tok_abcd-1234_xyz", "BRL")


def test_validate_order_rejects_unsupported_currency():
    assert not checkout.validate_order(20, "tok_12345", "BTC")


def test_validate_order_rejects_nan_total():
    assert not checkout.validate_order(float("nan"), "tok_12345", "BRL")


def test_validate_order_rejects_infinite_total():
    assert not checkout.validate_order(float("inf"), "tok_12345", "BRL")


def test_validate_order_rejects_boolean_total():
    assert not checkout.validate_order(True, "tok_12345", "BRL")


def test_validate_order_accepts_large_integer_without_overflow():
    assert checkout.validate_order(10**1000, "tok_12345", "BRL")


def test_validate_order_rejects_non_string_currency():
    assert not checkout.validate_order(20, "tok_12345", ["BRL"])


def test_validate_order_accepts_two_decimal_places():
    assert checkout.validate_order(10.25, "tok_12345", "BRL")


def test_validate_order_rejects_more_than_two_decimal_places():
    assert not checkout.validate_order(10.257, "tok_12345", "BRL")


def test_validate_order_handles_huge_float_without_exception():
    result = checkout.validate_order(1e307, "tok_12345", "BRL")
    assert isinstance(result, bool)


def test_validate_order_accepts_large_two_decimal_float():
    assert checkout.validate_order(10000000.05, "tok_12345", "BRL")


def test_validate_order_rejects_sub_cent_float():
    assert not checkout.validate_order(1e-11, "tok_12345", "BRL")


def test_validate_order_rejects_float_artifact_with_many_decimals():
    assert not checkout.validate_order(0.1 + 0.2, "tok_12345", "BRL")
