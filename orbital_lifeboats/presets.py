"""
Editable inputs — the "plug in the values" surface. Stations, design assumptions,
and unit mass/cost. Change these and re-run generate_figures.py.
"""

from dataclasses import dataclass, field
from .constants import EARTH


@dataclass
class Station:
    name: str
    inclination_deg: float
    altitude_km: float
    crew: int

    @property
    def radius(self):
        return EARTH.radius + self.altitude_km


# What is presently in continuous human habitation (verified May 2026).
# Add commercial stations here as they're crewed (Haven-1 ~2027, Axiom ~2028).
STATIONS = [
    Station("ISS",      51.6, 417.0, 7),
    Station("Tiangong", 41.5, 389.0, 3),
]


@dataclass
class DesignParams:
    # shortest life-support clock we insure against (hours) — a bad depress
    design_clock_h: float = 6.0
    # stage-1 chemical responder Δv budget (m/s)
    stage1_budget_ms: float = 400.0
    # formation lifeboats per station (zero-phasing, common-cause robustness)
    formation_per_station: int = 2
    # stage-2 / stage-3 per plane
    sustain_per_plane: int = 1
    recover_per_plane: int = 1
    spares_margin: float = 0.30

    # per-unit mass (tonnes) and early-production cost ($B) by echelon
    unit_mass_t: dict = field(default_factory=lambda: {1: 3.0, 2: 6.0, 3: 10.0})
    unit_cost_b: dict = field(default_factory=lambda: {1: 0.08, 2: 0.12, 3: 0.25})
    launch_cost_b_per_t: float = 0.0025   # ~$2.5k/kg to LEO
    dev_cost_full_b: float = 1.0
    dev_cost_lean_b: float = 0.6


DEFAULT = DesignParams()


@dataclass(frozen=True)
class Launcher:
    name: str
    leo_capacity_t: float      # mass to LEO per launch
    cost_b_per_t: float        # $B per tonne to LEO
    bay_volume_m3: float       # usable payload volume


# Approximate, order-of-magnitude. Reusable configs where applicable.
LAUNCHERS = {
    "Falcon 9":       Launcher("Falcon 9 (reusable)",        17.5, 0.0030,   90),  # ~$3.0k/kg
    "Falcon Heavy":   Launcher("Falcon Heavy (reusable)",    30.0, 0.0015,   90),  # ~$1.5k/kg
    "Starship":       Launcher("Starship (credible early)", 100.0, 0.0005, 1000),  # ~$0.5k/kg
    "Starship (goal)":Launcher("Starship (aspirational)",   150.0, 0.00015,1000),  # ~$150/kg
}

# Exhaust efficiency (specific impulse, s) by propellant class.
ISP_S = {"storable": 320, "methalox": 360, "ion": 3000}


@dataclass(frozen=True)
class Lifeboat:
    name: str
    mass_t: float        # launch mass per unit
    volume_m3: float     # stowed volume per unit
    crew: int            # seats / refuge capacity


# Three representative recovery-vehicle ("lifeboat") designs, low to high capability.
LIFEBOATS = {
    "compact pod":      Lifeboat("Compact refuge pod (squeezed)",     3.0, 25.0, 3),
    "standard refuge":  Lifeboat("Standard refuge (Starship-relaxed)", 8.0, 50.0, 4),
    "reentry lifeboat": Lifeboat("Reentry lifeboat (brings crew home)",25.0, 80.0, 6),
}
