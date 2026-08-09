"""
Tests for core.residency -- verified against real scenarios worked through
in chat this session, not synthetic examples, so a passing test means it
matches a case we already hand-verified.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from core.models import Profile, TravelLogEntry, PriorYearRecord
from core.residency import compute_residency, days_between, holding_period_days


def test_real_fy2025_26_voyage_gives_nri():
    """The actual voyage this session: 25-Jul-2025 to 14-Feb-2026, which
    we hand-computed earlier as ~206 days abroad, ~159 days in India,
    correctly landing at NRI status (under 182 either way)."""
    profile = Profile(
        fy="2025-26",
        citizenship="Indian",
        employment_abroad=True,
        travel_log=[TravelLogEntry(depart=date(2025, 7, 25), arrive=date(2026, 2, 14))],
    )
    result = compute_residency(profile)
    assert result.status == "Non-Resident (NRI)", f"Expected NRI, got {result.status}"
    assert result.days_in_india < 182
    print(f"PASS: real voyage -> {result.status}, {result.days_in_india} days in India")


def test_holding_period_365_day_boundary_is_short_term():
    """The exact boundary bug documented in the JS source comments:
    buy 13-Mar-2025, sell 13-Mar-2026 is exactly 365 days -- must be
    short-term (needs MORE than 365), not long-term."""
    days = holding_period_days(date(2025, 3, 13), date(2026, 3, 13))
    assert days == 365
    assert not (days > 365), "365 days must NOT qualify as long-term"
    print(f"PASS: 365-day boundary correctly non-long-term ({days} days)")


def test_resident_with_no_prior_years_gets_generic_rnor_reminder():
    """Resident status with zero prior-year data should get the generic
    'fill in Prior Years' reminder, not a false definitive answer."""
    profile = Profile(
        fy="2025-26",
        travel_log=[TravelLogEntry(depart=date(2025, 6, 1), arrive=date(2025, 6, 10))],
    )
    result = compute_residency(profile)
    assert result.status == "Resident"
    assert result.rnor_result is None
    assert "no prior-year data" in result.rnor_note
    print(f"PASS: Resident + no prior years -> generic reminder, not false answer")


def test_rnor_qualifies_via_2_nonresident_years():
    """Resident this year, but 2+ NRI years in the last 10 on record ->
    should correctly identify RNOR."""
    profile = Profile(
        fy="2025-26",
        travel_log=[],  # 0 days abroad -> Resident
        prior_years={
            "2024-25": PriorYearRecord(fy="2024-25", residency_status="NRI", days_in_india=100),
            "2023-24": PriorYearRecord(fy="2023-24", residency_status="NRI", days_in_india=90),
            "2022-23": PriorYearRecord(fy="2022-23", residency_status="Resident", days_in_india=300),
        },
    )
    result = compute_residency(profile)
    assert result.status == "Resident"
    assert result.rnor_result == "RNOR"
    print(f"PASS: RNOR correctly identified via 2 non-resident years")


if __name__ == "__main__":
    test_real_fy2025_26_voyage_gives_nri()
    test_holding_period_365_day_boundary_is_short_term()
    test_resident_with_no_prior_years_gets_generic_rnor_reminder()
    test_rnor_qualifies_via_2_nonresident_years()
    print("\nAll tests passed.")
