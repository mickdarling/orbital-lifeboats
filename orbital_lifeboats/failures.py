"""
Failure-mode taxonomy (note 06), each tagged with its life-support CLOCK and the
echelon/response it drives. The clock is what decides reachability, so it's the
field that matters most for staging.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureMode:
    id: str
    name: str
    category: str        # Propulsion / LifeSupport / Habitat / Medical / Comms / Radiation / Trajectory
    clock_h: float       # nominal time-to-loss-of-crew if unaided (hours)
    needs: str           # what the buoy must supply
    echelon: str         # primary responding stage


FAILURE_MODES = [
    FailureMode("C1", "Hull breach / depress (suits)", "Habitat", 6,
                "pressurized refuge, fast", "Stage-1 (close/formation)"),
    FailureMode("C2", "Fire", "Habitat", 3,
                "clean refuge + air", "Stage-1 (close/formation)"),
    FailureMode("C3", "Toxic contamination", "Habitat", 4,
                "clean refuge", "Stage-1 (close/formation)"),
    FailureMode("B1", "O2 generation fail / leak", "LifeSupport", 24,
                "O2 + refuge", "Stage-1 then Stage-2"),
    FailureMode("B2", "CO2 scrubber failure", "LifeSupport", 12,
                "scrubber media / refuge", "Stage-1 then Stage-2"),
    FailureMode("B4", "Power loss", "LifeSupport", 18,
                "power + refuge", "Stage-1 then Stage-2"),
    FailureMode("B5", "Thermal control failure", "LifeSupport", 20,
                "thermal refuge / radiators", "Stage-2"),
    FailureMode("D1", "Acute medical / injury", "Medical", 24,
                "medical + telemedicine relay", "Stage-1 + comms"),
    FailureMode("G1", "Solar particle event, no shelter", "Radiation", 8,
                "shielded storm cellar", "Stage-1 (shielded)"),
    FailureMode("B6", "Consumables overrun / missed window", "LifeSupport", 240,
                "resupply to extend", "Stage-2"),
    FailureMode("A1", "Main engine failure", "Propulsion", 240,
                "tug to move them", "Stage-3 (tug)"),
    FailureMode("A3", "Stuck, no way down", "Propulsion", 240,
                "reentry-capable vehicle", "Stage-3 (reentry)"),
    FailureMode("H1", "Partial burn -> off-nominal arc", "Trajectory", 72,
                "corrective tug or consumables", "Stage-2 / Stage-3"),
]


def by_category():
    out = {}
    for f in FAILURE_MODES:
        out.setdefault(f.category, []).append(f)
    return out
