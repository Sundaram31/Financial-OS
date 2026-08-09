"""
Residency status calculator (Sec 6, Income Tax Act) -- pure Python port of
the JS ResidencyModule.computeResidency() from itrgenie/index.html.

Ported first because it's the gate module: almost every other module (House
Property occupancy treatment, Foreign Assets residency gate, Capital Gains
taxability) depends on residency status being correct before anything else
makes sense. Same reasoning as why it's Module 01 in the JS app.

Rules encoded here (unchanged from JS, just translated):
- Standard test: 182+ days in India this FY -> Resident.
- Secondary test: for a citizen leaving India for employment abroad
  (seafarers, this app's original use case), the usual 60-day secondary
  threshold is replaced with 182 days -- so for that group, only the
  primary test applies, effectively.
- RNOR test: qualifies if Non-Resident in >=2 of the last 10 FYs on record,
  OR days in India over the last 4 FYs (including current) <= 729.
"""
from __future__ import annotations
from datetime import date
from .models import Profile, ResidencyResult, TravelLogEntry

STANDARD_DAY_THRESHOLD = 182
STANDARD_SECONDARY_THRESHOLD = 60
CITIZEN_LEAVING_FOR_EMPLOYMENT_THRESHOLD = 182
RNOR_MIN_NONRESIDENT_YEARS = 2
RNOR_STAY_LAST_4_YEARS_MAX = 729


def days_between(d1: date, d2: date) -> int:
    """Inclusive day count for TRAVEL/PRESENCE purposes -- both the
    departure and return day count as a day 'in' India, matching standard
    practice and the JS daysBetween() function. Do NOT reuse this for
    capital gains holding-period math (see holding_period_days below) --
    that needs a different, non-inclusive calculation, which was a real
    bug caught and fixed in the JS version (see itrgenie source comments)."""
    return (d2 - d1).days + 1


def holding_period_days(d1: date, d2: date) -> int:
    """Sec 2(42A) holding period for capital gains classification --
    deliberately NOT the same as days_between(). Must be a raw calendar
    difference (no +1): a purchase on 13-Mar-2025 sold on 13-Mar-2026 is
    exactly 365 days elapsed, which is NOT 'more than 365' and must
    classify as short-term. Kept here alongside days_between specifically
    so the distinction isn't lost again during the port, as it was
    originally in the JS source."""
    return (d2 - d1).days


def compute_residency(profile: Profile) -> ResidencyResult:
    total_days_abroad = 0
    for entry in profile.travel_log:
        if entry.depart and entry.arrive:
            total_days_abroad += days_between(entry.depart, entry.arrive)

    days_in_india = max(0, 365 - total_days_abroad)

    is_citizen_leaving_for_employment = (
        profile.citizenship == "Indian" and profile.employment_abroad
    )
    secondary_threshold = (
        CITIZEN_LEAVING_FOR_EMPLOYMENT_THRESHOLD
        if is_citizen_leaving_for_employment
        else STANDARD_SECONDARY_THRESHOLD
    )

    basis_lines = [
        f"Days in India this FY (computed): {days_in_india}",
        f"Applicable secondary threshold: {secondary_threshold} days "
        f"({'seafarer/citizen-leaving-for-employment exception applied' if is_citizen_leaving_for_employment else 'standard test'})",
    ]

    if days_in_india >= STANDARD_DAY_THRESHOLD:
        status = "Resident"
    elif days_in_india >= secondary_threshold:
        status = "Resident (via secondary test)"
    else:
        status = "Non-Resident (NRI)"

    basis_lines.append(
        f"Primary test: 182+ days in India -> "
        f"{'MET' if days_in_india >= STANDARD_DAY_THRESHOLD else 'not met'}"
    )
    basis_lines.append(
        f"Secondary test: {secondary_threshold}+ days in India "
        f"(with 4-year lookback >=365 days, not yet captured here) -> "
        f"{'MET' if days_in_india >= secondary_threshold else 'not met'}"
    )

    rnor_note = None
    rnor_result = None

    if status.startswith("Resident"):
        fy_keys = sorted(profile.prior_years.keys(), reverse=True)

        if len(fy_keys) == 0:
            rnor_note = (
                "You may qualify as RNOR (taxed like NRI on foreign income) if "
                "you were Non-Resident in 9 of the last 10 FYs, or present in "
                "India <=729 days over the last 4 FYs -- but no prior-year data "
                "is on file yet. Fill in Prior Years to get an actual answer "
                "instead of this generic reminder."
            )
        else:
            last10 = fy_keys[:10]
            non_resident_count = sum(
                1 for fy in last10
                if profile.prior_years[fy].residency_status.strip().lower() != "resident"
            )
            last4 = fy_keys[:4]
            days_last4 = sum(
                (profile.prior_years[fy].days_in_india or 0) for fy in last4
            ) + days_in_india
            has_4year_data = len(last4) >= 4
            has_10year_data = len(last10) >= 10

            test1_met = non_resident_count >= RNOR_MIN_NONRESIDENT_YEARS
            test2_met = has_4year_data and days_last4 <= RNOR_STAY_LAST_4_YEARS_MAX

            if test1_met or test2_met:
                rnor_result = "RNOR"
                reason = (
                    f"Non-Resident in {non_resident_count} of the last {len(last10)} FY(s) on file (needs >=2)"
                    if test1_met
                    else f"{days_last4} days in India over the last 4 FYs + this one (needs <=729)"
                )
                rnor_note = (
                    f"Qualifies as RNOR: {reason}. RNOR income is taxed like "
                    f"NRI -- foreign income generally stays exempt, with the "
                    f"usual exception for foreign income derived from an "
                    f"Indian business/profession."
                )
            elif not has_10year_data and not has_4year_data:
                rnor_result = "Insufficient data"
                rnor_note = (
                    f"Can't be determined yet -- only {len(last10)} of the last "
                    f"10 years' residency history is on file (need either 2+ "
                    f"Non-Resident years among the full 10, or the full "
                    f"4-year day count). The {non_resident_count} Non-Resident "
                    f"year(s) recorded so far don't rule RNOR in OR out -- add "
                    f"more years for a real answer, rather than trusting a "
                    f"'does not qualify' verdict built on an incomplete window."
                )
            else:
                rnor_result = "Ordinarily Resident"
                rnor_note = (
                    f"Does not qualify as RNOR based on data on file: only "
                    f"{non_resident_count} Non-Resident year(s) in the last "
                    f"{len(last10)} on record (needs >=2), and "
                    f"{f'{days_last4} days in India over the last 4 FYs (needs <=729)' if has_4year_data else 'incomplete 4-year day data'}. "
                    f"Worldwide income is taxable as an Ordinarily Resident."
                )

    return ResidencyResult(
        days_in_india=days_in_india,
        total_days_abroad=total_days_abroad,
        status=status,
        basis_lines=basis_lines,
        rnor_note=rnor_note,
        rnor_result=rnor_result,
    )
