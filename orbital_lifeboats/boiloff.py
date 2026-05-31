"""
What a cache can keep: passive boiloff timelines and solar-power falloff.
Order-of-magnitude; passive rates depend strongly on tank size & sun exposure.
"""

from dataclasses import dataclass
from .constants import AU


@dataclass(frozen=True)
class Commodity:
    name: str
    boiloff_pct_day: float   # passive %/day (0 = effectively stable)
    temp_k: float            # storage temperature
    note: str


# Representative passive (MLI-only) commodities.
COMMODITIES = [
    Commodity("Liquid hydrogen (LH2)", 1.00, 20,  "brutal heat leak; days-weeks"),
    Commodity("Liquid methane (LCH4)", 0.10, 112, "manageable with good MLI"),
    Commodity("Liquid oxygen (LOX)",   0.10, 90,  "manageable"),
    Commodity("Storables (N2H4/NTO)",  0.00, 290, "years-decades, no cooling"),
    Commodity("Water / gas / food",    0.00, 290, "indefinite if sealed"),
]


def fraction_remaining(boiloff_pct_day, days):
    """Linear-loss fraction of a tank remaining after `days` (clamped to 0)."""
    return max(0.0, 1.0 - boiloff_pct_day / 100.0 * days)


def days_to_lose(boiloff_pct_day, fraction):
    """Days to lose `fraction` (0..1) of a tank. inf if stable."""
    if boiloff_pct_day <= 0:
        return float("inf")
    return fraction * 100.0 / boiloff_pct_day


def solar_fraction(distance_au):
    """Sunlight intensity as a fraction of Earth's (1/r^2)."""
    return (1.0 / distance_au) ** 2 if distance_au > 0 else 0.0
