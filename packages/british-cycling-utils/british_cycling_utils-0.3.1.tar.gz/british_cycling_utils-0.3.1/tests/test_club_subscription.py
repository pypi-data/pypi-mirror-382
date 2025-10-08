"""Tests for 'BC' functions."""

from datetime import date

from british_cycling_utils.club_subscription import ClubSubscription

bc_data = {
    "first_name": "Julia",
    "last_name": "Roberts",
    "membership_number": "12345",
    "email": "julia@example.com",
    "end_dt": "19/12/2024",
    "telephone_day": "+441234567890",
}

bc_data_with_blank = {
    "first_name": "Kevin",
    "last_name": "Bacon",
    "membership_number": "54321",
    "email": "kevin@example.com",
    "end_dt": "",
    "telephone_day": "+441234567890",
}


def test_from_bc_data__happy_path() -> None:
    """Test that a `ClubSubscription` instance is created from BC data."""
    sub = ClubSubscription.from_bc_data(bc_data)
    assert sub.email == "julia@example.com"
    assert sub.first_name == "Julia"
    assert sub.last_name == "Roberts"
    assert sub.telephone == "+441234567890"
    assert sub.british_cycling_membership_number == 12345
    assert sub.club_membership_expiry
    assert sub.club_membership_expiry == date(2024, 12, 19)


def test_from_bc_data__blank_fields() -> None:
    """Test that a `ClubSubscription` instance is created when fields are blank."""
    sub = ClubSubscription.from_bc_data(bc_data_with_blank)
    assert sub.club_membership_expiry is None
