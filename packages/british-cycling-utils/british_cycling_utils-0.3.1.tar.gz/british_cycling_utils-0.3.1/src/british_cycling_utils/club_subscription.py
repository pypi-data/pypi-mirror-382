"""Module containing `ClubSubscription` class and associated code."""

import csv
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Self

from attrs import define, field
from cattrs import Converter
from cattrs.gen import make_dict_structure_fn


def _convert_bc_date(value: str, type_: date) -> date | None:  # noqa: ARG001
    """Convert from string in BC data to date or None."""
    return (
        datetime.strptime(value, "%d/%m/%Y").astimezone(UTC).date() if value else None
    )


@define(kw_only=True, frozen=True)
class ClubSubscription:
    """Represents a subscription record in the BC Club Management Tool."""

    # Other column names: dob, emergency_contact_name, emergency_contact_number,
    # primary_club, membership_type, membership_status, valid_to_dt, age_category,
    # Address 1, Address 2, Address 3, Address 4, Address 5, Address 6, Country,
    # Road & Track Licence Cat

    first_name: str
    """Required, appears always populated in CSV.
    CSV column: same name.
    BC UI column: 'Forename'."""

    last_name: str
    """Required, appears always populated in CSV.
    CSV column: same name.
    BC UI column: 'Surname'."""

    email: str
    """Required, appears always populated in CSV.
    CSV column: same name.
    BC UI column: 'Email'."""

    telephone: str = field(alias="telephone_day")
    """Required, appears always populated in CSV.
    CSV column: same name
    BC UI column: 'Telephone'."""

    british_cycling_membership_number: int = field(alias="membership_number")
    """Required, appears always populated in CSV.
    This is a really a BC profile/login id, not limited to current BC members.
    CSV column: 'membership_number'.
    BC UI column: 'British Cycling Member', but blank if not a current BC member."""

    club_membership_expiry: date | None = field(alias="end_dt")
    """Optional, observed not always populated in CSV.
    CSV column: 'end_dt'.
    BC UI column: 'Club Membership Expiry'."""

    @classmethod
    def from_bc_data(cls, bc_data: Mapping[str, Any]) -> Self:
        """Create instance from BC data.

        Aliases and converts fields; ignores non-implemented fields.
        """
        c = Converter(use_alias=True)
        c.register_structure_hook(date, _convert_bc_date)
        hook = make_dict_structure_fn(cls, c)
        c.register_structure_hook(cls, hook)
        return c.structure(bc_data, cls)

    @classmethod
    def list_from_bc_csv(cls, file_path: Path) -> list[Self]:
        """Take a CSV export from the BC system and return a list of instances."""
        if not Path(file_path).is_file():
            err_msg = f"`{file_path}`."
            raise FileNotFoundError(err_msg)

        with file_path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [cls.from_bc_data(row) for row in reader]
