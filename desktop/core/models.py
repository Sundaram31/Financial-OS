"""
Core data models for Financial OS.

Design principle (established 2026-08-07): these models and every function in
core/ have ZERO dependency on any UI framework. They don't know whether
they're being called from a pywebview desktop app, a future FastAPI cloud
backend, or a test script. This is what makes "add a cloud layer later"
mean "wrap these functions in an API," not "rewrite the calculations."

Mirrors the JS `profile` object structure from itrgenie/index.html, so
porting each module is a faithful translation, not a redesign.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class TravelLogEntry:
    """One departure/return pair from India, for residency day-counting."""
    depart: date
    arrive: date


@dataclass
class PriorYearRecord:
    """One prior FY's residency status + carried-forward losses -- feeds
    the RNOR 10-year lookback and loss set-off, same as the JS Prior Years
    module."""
    fy: str
    residency_status: str  # "Resident" | "RNOR" | "NRI"
    days_in_india: Optional[int] = None
    carried_forward_loss_st: float = 0.0
    carried_forward_loss_lt: float = 0.0


@dataclass
class ResidencyResult:
    """Mirrors the JS computeResidency() return shape exactly, so the
    Python and JS versions can be cross-checked against each other during
    the port -- same field names, same semantics."""
    days_in_india: int
    total_days_abroad: int
    status: str  # "Resident" | "Resident (via secondary test)" | "Non-Resident (NRI)"
    basis_lines: list[str] = field(default_factory=list)
    rnor_note: Optional[str] = None
    rnor_result: Optional[str] = None  # "RNOR" | "Ordinarily Resident" | "Insufficient data" | None


@dataclass
class Profile:
    """The top-level container -- mirrors the JS `profile` object.
    Only the fields needed for the modules ported so far are included;
    add fields here as each additional module gets ported, same pattern
    as the JS defaultProfile() function grew module by module."""
    fy: str = "2025-26"
    citizenship: str = "Indian"
    employment_abroad: bool = True
    travel_log: list[TravelLogEntry] = field(default_factory=list)
    prior_years: dict[str, PriorYearRecord] = field(default_factory=dict)
    residency_result: Optional[ResidencyResult] = None
