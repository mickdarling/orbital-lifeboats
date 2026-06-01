#!/usr/bin/env python3
"""
Solar-Wind Turbine — coherent physical model.

A magnetic-sail "windmill": magnetic-bottle tips on counter-rotating cables,
fired as a couple so the rig spins (drives a generator) without leaving orbit.

ONE consistent chain (this is the rebuild — the earlier version mixed a fixed
bubble with a self-inflating one, which was incoherent):

  knobs:   bubble radius AT 1 AU (R1)  +  cable material (-> max tip speed)  +
           operating tip speed v_tip  +  sail scaling model  +  bottle type
  derived: at distance r, the bubble radius R(r) and force F(r) follow from the
           chosen scaling model; extracted power = drag turbine on that force;
           net power = extracted - bottle power.

Two sail scaling models (they scale DIFFERENTLY with distance — that was the
source of the confusion):
  * 'plasma_magnet' : wind-inflated, R grows ∝ r, so F = ram·area is CONSTANT
                      with distance (the celebrated Slough/Wind-Rider property).
  * 'dipole'        : rigid coil, pressure balance gives R ∝ r^(1/3), so
                      F ∝ r^(-4/3) (force FALLS as you go out).

Run the model:  python3 turbine.py      Validate the physics:  python3 test_turbine.py
"""

import math
from dataclasses import dataclass

# --- constants -------------------------------------------------------------
MP = 1.6726e-27          # proton mass, kg
AU = 1.495979e11         # m
G0 = 9.80665             # m/s^2
GM_SUN = 1.32712e20      # m^3/s^2
SOLAR_CONST_1AU = 1361.0 # W/m^2
YEAR = 3.156e7           # s

N0 = 5.0e6               # solar-wind protons / m^3 at 1 AU
V_SW = 4.0e5             # solar-wind speed, m/s (~constant with distance)
CD = 1.0                 # sail drag/reflection coefficient (order 1)


# --- solar wind environment ------------------------------------------------
def sw_number_density(r_au):
    return N0 / r_au ** 2

def sw_mass_density(r_au):
    return MP * sw_number_density(r_au)

def ram_pressure(r_au):
    """Solar-wind ram pressure rho*v^2 (momentum flux), Pa."""
    return sw_mass_density(r_au) * V_SW ** 2

def energy_flux(r_au):
    """Kinetic energy flux 1/2 rho v^3, W/m^2."""
    return 0.5 * sw_mass_density(r_au) * V_SW ** 3


# --- the magnetic sail -----------------------------------------------------
@dataclass(frozen=True)
class Sail:
    radius_1au_m: float                 # bubble radius at 1 AU (the size knob)
    model: str = "plasma_magnet"        # 'plasma_magnet' or 'dipole'

    def radius(self, r_au):
        if self.model == "plasma_magnet":
            return self.radius_1au_m * r_au           # R ∝ r  -> F constant
        elif self.model == "dipole":
            return self.radius_1au_m * r_au ** (1 / 3)  # pressure balance, B∝1/R^3
        raise ValueError(self.model)

    def area(self, r_au):
        return math.pi * self.radius(r_au) ** 2

    def force(self, r_au):
        """Sail force F = Cd * ram_pressure * area (N)."""
        return CD * ram_pressure(r_au) * self.area(r_au)


# --- the turbine (drag-type rotor) -----------------------------------------
def drag_cp(v_tip, v_rel, cd=CD):
    """Power coefficient of a drag rotor: Cd (1-lambda)^2 lambda, lambda=v_tip/v_rel.
    Peaks at lambda=1/3 (Cp=4Cd/27); zero once the tip outruns the wind."""
    lam = v_tip / v_rel
    return cd * (1 - lam) ** 2 * lam if 0 <= lam < 1 else 0.0

def extracted_power(force, v_tip, v_rel=V_SW):
    """Mechanical (=electrical) power a drag rotor pulls from the wind:
    P = 1/2 * F * v_tip * (1 - v_tip/v_rel)^2.  (-> 1/2 F v_tip for slow tips.)"""
    lam = v_tip / v_rel
    return 0.5 * force * v_tip * (1 - lam) ** 2 if 0 <= lam < 1 else 0.0


# --- materials: specific strength sets the tip-speed ceiling ---------------
@dataclass(frozen=True)
class Material:
    name: str
    sigma_pa: float
    rho: float
    @property
    def specific_strength(self):
        return self.sigma_pa / self.rho

MATERIALS = [
    Material("Steel (HS)",        2.0e9, 7800),
    Material("Kevlar",            3.6e9, 1440),
    Material("Carbon fiber",      6.4e9, 1800),
    Material("Zylon (PBO)",       5.8e9, 1560),
    Material("CNT (theoretical)", 60.0e9, 1340),
]

def tip_speed_limit(mat, safety=2.0):
    """Spinning-tether limit: hoop stress 1/2 rho v^2 <= sigma/SF."""
    return math.sqrt(2.0 * (mat.sigma_pa / safety) / mat.rho)


# --- bottle (field generator) power draw -----------------------------------
# --- buying bubble size with field power (resistive coil) ------------------
# Anchor: M2P2 reference, ~3 kW of coil power -> ~15 km bubble radius at 1 AU.
# Dipole pressure balance gives R ∝ (magnetic moment)^(1/3); a resistive coil's
# moment ∝ sqrt(power); and R ∝ rho^(-1/6) ∝ r^(1/3). Net: R ∝ P^(1/6) r^(1/3).
REF_FIELD_POWER_W = 3000.0
REF_RADIUS_M = 15000.0

def radius_from_field_power(p_field_w, r_au=1.0):
    """Bubble radius a RESISTIVE coil buys for p_field_w of continuous power."""
    return REF_RADIUS_M * (p_field_w / REF_FIELD_POWER_W) ** (1/6) * r_au ** (1/3)

def field_power_for_radius(radius_m, r_au=1.0):
    """Continuous coil power a RESISTIVE coil needs to hold a given bubble (∝ R^6)."""
    return REF_FIELD_POWER_W * (radius_m / (REF_RADIUS_M * r_au ** (1/3))) ** 6


def optimal_radius_resistive(r_au, v_tip):
    """Bubble radius that MAXIMIZES net power for a resistive coil, where harvest
    ∝ R^2 but the field bill ∝ R^6.  net = C R^2 - k R^6 -> R_opt = (C/3k)^(1/4).
    (Constant with distance; net_max falls as 1/r^2. No interior optimum exists
    for a superconducting coil, whose field cost is fixed -> net just grows ∝ R^2.)"""
    C = 0.5 * CD * ram_pressure(r_au) * math.pi * v_tip
    k = REF_FIELD_POWER_W / (REF_RADIUS_M ** 6 * r_au ** 2)
    return (C / (3 * k)) ** 0.25


def injection_density():
    """M2P2 reference: ~3 kW for a ~15 km bubble -> power per unit area (W/m^2)."""
    return 3000.0 / (math.pi * 7500.0 ** 2)

def bottle_power(area, bottle="superconducting", p_fixed=2000.0):
    """Power to maintain the field.
    'superconducting' (plasma magnet): ~fixed coil+cryo power, area-independent.
    'injection' (M2P2): continuous plasma feed -> scales with bubble area."""
    if bottle == "superconducting":
        return p_fixed
    elif bottle == "injection":
        return injection_density() * area
    raise ValueError(bottle)

def net_power(sail, v_tip, r_au=1.0, bottle="superconducting", p_fixed=2000.0,
              v_rel=V_SW):
    ext = extracted_power(sail.force(r_au), v_tip, v_rel)
    return ext - bottle_power(sail.area(r_au), bottle, p_fixed)


# --- structural: cable cross-section & mass --------------------------------
def cable_cross_section(mat, v_tip, arm_len, tip_mass, safety=2.0):
    sa = mat.sigma_pa / safety
    head = sa - 0.5 * mat.rho * v_tip ** 2          # strength left after self-load
    if head <= 0:
        return math.inf
    return tip_mass * v_tip ** 2 / (arm_len * head)

def cable_mass(mat, v_tip, arm_len, tip_mass, safety=2.0):
    a = cable_cross_section(mat, v_tip, arm_len, tip_mass, safety)
    return math.inf if a == math.inf else mat.rho * a * arm_len


# --- helpers ---------------------------------------------------------------
def kw(p):
    if p == math.inf:
        return "inf"
    return f"{p/1e6:.2f} MW" if abs(p) >= 1e6 else f"{p/1e3:.1f} kW"

def hr(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


# ---------------------------------------------------------------------------
def main():
    print(__doc__)
    BUBBLES_KM = [25, 50, 100, 200, 400]
    P_FIXED = 2000.0

    hr("1.  ENVIRONMENT vs DISTANCE")
    print(f"  {'r (AU)':>7} {'n (/cm^3)':>10} {'ram P (nPa)':>12} {'E-flux (W/m^2)':>15}")
    for r in (1, 5, 10, 30):
        print(f"  {r:>7} {sw_number_density(r)/1e6:>10.3f} {ram_pressure(r)*1e9:>12.4f}"
              f" {energy_flux(r):>15.2e}")

    hr("2.  TIP-SPEED CEILING BY MATERIAL  (v=sqrt(2*strength/SF), SF=2)")
    for m in MATERIALS:
        print(f"  {m.name:22} {tip_speed_limit(m)/1000:>6.2f} km/s")

    hr("3.  EXTRACTED POWER vs (cable material x bubble size)  [plasma magnet, 1 AU]")
    print("  This is the real 'what does it make' grid. Columns = bubble radius at")
    print("  1 AU; rows = tip speed at each material's limit. Power = 1/2 F v_tip.\n")
    hdr = "  " + f"{'material / bubble':22}" + "".join(f"{b:>9}km" for b in BUBBLES_KM)
    print(hdr)
    for m in MATERIALS:
        vt = tip_speed_limit(m)
        cells = []
        for bk in BUBBLES_KM:
            s = Sail(bk * 1000, "plasma_magnet")
            cells.append(kw(extracted_power(s.force(1.0), vt)))
        print(f"  {m.name:22}" + "".join(f"{c:>11}" for c in cells))

    hr(f"4.  NET POWER = extracted - bottle  [superconducting bottle ~{P_FIXED/1000:.0f} kW]")
    print("  Negative = the field costs more than the spin makes. Net positive needs")
    print("  enough bubble (force) and tip speed (material). THIS is the real metric.\n")
    print(hdr)
    for m in MATERIALS:
        vt = tip_speed_limit(m)
        cells = []
        for bk in BUBBLES_KM:
            s = Sail(bk * 1000, "plasma_magnet")
            net = extracted_power(s.force(1.0), vt) - bottle_power(s.area(1.0),
                                                                   "superconducting", P_FIXED)
            cells.append(("+" if net >= 0 else "") + kw(net))
        print(f"  {m.name:22}" + "".join(f"{c:>11}" for c in cells))

    hr("5.  WHY THE OLD 'FLAT 5.3 kW EVERYWHERE' WAS WRONG vs RIGHT")
    print("  It depends on the SAIL MODEL, and the bubble is NOT the same size at")
    print("  every distance. Carbon-fiber tips (1.89 km/s), 50 km bubble AT 1 AU:\n")
    s_pm = Sail(50_000, "plasma_magnet")
    s_di = Sail(50_000, "dipole")
    vt = tip_speed_limit(MATERIALS[2])
    print(f"  {'r(AU)':>6} | {'PLASMA MAGNET':^28} | {'RIGID DIPOLE':^28}")
    print(f"  {'':>6} | {'R(km)':>7}{'F(N)':>9}{'P_ext':>12} | {'R(km)':>7}{'F(N)':>9}{'P_ext':>12}")
    for r in (1, 5, 10, 30):
        pm_p = extracted_power(s_pm.force(r), vt)
        di_p = extracted_power(s_di.force(r), vt)
        print(f"  {r:>6} | {s_pm.radius(r)/1000:>7.0f}{s_pm.force(r):>9.1f}{kw(pm_p):>12}"
              f" | {s_di.radius(r)/1000:>7.0f}{s_di.force(r):>9.1f}{kw(di_p):>12}")
    print("\n  Plasma magnet: bubble GROWS (50->1500 km), force constant, power flat.")
    print("  Rigid dipole:  bubble grows slowly, force falls ~r^-4/3, power drops.")
    print("  The flat case is real (Wind Rider), but only because the bubble inflates;")
    print("  quoting '50 km' at every distance was the bug.")

    hr("6.  CAN IT POWER ITS OWN BOTTLES?")
    rho = sw_mass_density(1.0)
    hd = 0.5 * CD * rho * V_SW ** 2 * tip_speed_limit(MATERIALS[2])   # harvest W/m^2 at vt
    idn = injection_density()
    print(f"  harvest density (CF tips): {hd*1e6:.2f} uW/m^2")
    print(f"  M2P2 injection cost:       {idn*1e6:.2f} uW/m^2  -> "
          f"~{idn/hd:.0f}x short, NET NEGATIVE (can't self-power).")
    be = math.sqrt(P_FIXED / (hd * math.pi))
    print(f"  Superconducting (fixed {P_FIXED/1000:.0f} kW): break-even at "
          f"~{be/1000:.0f} km bubble; bigger = net positive.")

    hr("7.  BUYING A BIGGER BUBBLE WITH FIELD POWER (and why it must be ~free)")
    print("  You CAN inflate the bubble by dumping power into the coil -- even close")
    print("  to the Sun against the denser wind. But bubble radius grows only as the")
    print("  6th ROOT of power (R ∝ P^1/6), so a RESISTIVE coil's field bill explodes")
    print("  (∝ R^6) and net power craters. Anchored to M2P2 (~3 kW -> ~15 km @1 AU):\n")
    vt = tip_speed_limit(MATERIALS[2])
    print(f"  {'field power':>12} {'bubble R':>9} {'force':>8} {'P_ext':>9} {'net (resistive)':>16}")
    for pf in (1e3, 1e4, 1e5, 1e6, 1e7):
        R = radius_from_field_power(pf, 1.0)
        F = CD * ram_pressure(1.0) * math.pi * R ** 2
        pext = extracted_power(F, vt)
        print(f"  {kw(pf):>12} {R/1000:>7.0f}km {F:>7.1f}N {kw(pext):>9} {kw(pext-pf):>16}")
    print("\n  64x the power for 2x the bubble -- a resistive coil is a sucker's game.")
    print("  The field must be held ~FREE: a SUPERCONDUCTING coil (sustained with no")
    print("  ongoing power) or the PLASMA MAGNET (the wind inflates it). Then bubble")
    print("  size is a coil-design/MASS choice (the grid in §3-4), not a power drain --")
    print("  and you CAN build a big bubble close in; the denser wind just wants a")
    print("  stronger (heavier) coil, not more watts.")

    hr("8.  IS THERE AN OPTIMAL BUBBLE SIZE?")
    print("  Pure extraction: NO -- power ∝ area, so bigger is always more. An")
    print("  optimum appears only when the COST of size grows faster than the harvest.")
    print("  With a RESISTIVE coil (field bill ∝ R^6) net peaks then craters:\n")
    vt = tip_speed_limit(MATERIALS[2])
    for r in (1, 3, 10):
        ropt = optimal_radius_resistive(r, vt)
        F = CD * ram_pressure(r) * math.pi * ropt ** 2
        netmax = extracted_power(F, vt) - field_power_for_radius(ropt, r)
        print(f"    resistive @ {r:>2} AU: optimal R ~ {ropt/1000:4.1f} km, "
              f"net_max ~ {netmax:.0f} W")
    print("\n  -> SAME optimal radius at every distance; peak height falls as 1/r^2,")
    print("     and it's tiny -- which is the real lesson: resistive is a dead end.")
    print("  For a SUPERCONDUCTING coil (fixed field cost) there is NO interior")
    print("  optimum -- net grows as R^2 until cable structure / coil mass cap it.")
    print("  So 'best size' = the biggest bubble you can structurally build.")

    hr("BOTTOM LINE")
    print("""
  * Power is NOT one number -- it's a grid over (bubble size x tip speed). It runs
    from sub-kW (small bubble, steel) to multi-MW (big bubble, strong material).
  * With distance: plasma-magnet force is constant (power flat) ONLY because the
    bubble inflates; a rigid dipole's power falls ~r^-4/3. Pick a model and stick
    to it -- mixing them was the earlier garbage.
  * NET power (extracted - bottle) is the number that matters; M2P2 can't self-
    power, the superconducting plasma magnet can above a break-even bubble size.
  * Run test_turbine.py -- the scaling laws and energy limits are asserted there.
    """)


if __name__ == "__main__":
    main()
