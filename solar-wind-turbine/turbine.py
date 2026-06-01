#!/usr/bin/env python3
"""
Solar-Wind Turbine — napkin math.

A separate concept from the lifeboat network (kept in its own folder), though it
lives in the same repo because it could power a deep-system cache.

THE MACHINE (Mick's design):
  A vertical-axis "windmill" in solar orbit. Spin axis points north-south
  (perpendicular to the ecliptic); a generator sits at the central hub. Two (or
  more) long counter-rotating cable-arms lie in the orbital plane, each tipped
  with a switchable magnetic-sail "bottle" (M2P2 / plasma-magnet style) that the
  solar wind pushes on.

  You fire the tip-sails as a FORCE COUPLE (opposite arms pushed in opposite
  tangential directions). A couple is pure torque with ZERO net translational
  force, so the rig spins up and drives the generator WITHOUT being blown out of
  its orbit. You toggle the bottles on/off through each rotation to keep the
  couple driving the spin, switching to the inbound tips as the arms swing past.

KEY PHYSICS THIS SCRIPT QUANTIFIES:
  * Extracted power is torque x omega = F_tip x v_tip (drag-type turbine).
  * Tip speed is capped by the CABLE, not the wind: a spinning tether fails when
    hoop stress 1/2 * rho_material * v_tip^2 exceeds its strength, so
    v_tip_max = sqrt(2 * specific_strength). That's the master limit.
  * Longer cables let you reach a target v_tip at lower spin rate omega
    (easier sail toggling, lower per-tip centrifugal load) for the same power.
  * The magnetic bubble SELF-SCALES (grows as the wind thins), so in the
    plasma-magnet "constant-force" regime the available power is ~FLAT with
    distance from the Sun -- unlike solar panels, which fall as 1/r^2.
  * Dual use: the same rig can generate power, sail (net thrust if you fire
    asymmetrically), feed an ion drive, and provide 1 g spin-gravity at the
    radius where omega^2 * r = g.

Two-body / order-of-magnitude. Run:  python3 turbine.py
"""

import math
from dataclasses import dataclass

# --- constants -------------------------------------------------------------
MP = 1.6726e-27          # proton mass, kg
AU = 1.495979e11         # m
GM_SUN = 1.32712e20      # m^3/s^2
G0 = 9.80665             # m/s^2
SOLAR_CONST_1AU = 1361.0 # W/m^2 (for the PV comparison)
YEAR = 3.156e7           # s

# Typical solar wind at 1 AU
N0 = 5.0e6               # protons / m^3  (5 /cm^3)
V_SW = 4.0e5             # m/s  (400 km/s), ~constant with distance
CD = 1.0                 # sail drag coefficient (order 1)
CAPTURE = 0.5            # geometric/duty efficiency of the couple over a rev


# --- solar wind environment ------------------------------------------------
def sw_number_density(r_au):
    return N0 / r_au**2

def sw_mass_density(r_au):
    return MP * sw_number_density(r_au)

def ram_pressure(r_au):
    """Solar-wind ram (dynamic) pressure rho*v^2 -- the momentum flux."""
    return sw_mass_density(r_au) * V_SW**2

def energy_flux(r_au):
    """Kinetic energy flux of the wind, 1/2 rho v^3 (W/m^2)."""
    return 0.5 * sw_mass_density(r_au) * V_SW**3


# --- the magnetic sail / bubble --------------------------------------------
def bubble_force(radius_m, r_au):
    """Force on a magnetic bubble of given radius at distance r_au."""
    area = math.pi * radius_m**2
    return CD * ram_pressure(r_au) * area

def bubble_radius_for_force(force_n, r_au):
    """Inverse: bubble radius needed to get `force_n` at r_au."""
    area = force_n / (CD * ram_pressure(r_au))
    return math.sqrt(area / math.pi)


# --- drag-turbine power coefficient ----------------------------------------
def drag_cp(tip_speed, rel_wind, cd=CD):
    """Power coefficient of a drag-type rotor: Cp = Cd (1-lambda)^2 lambda,
    lambda = v_tip / v_rel. Peaks at lambda=1/3 (Cp = 4Cd/27 ~ 0.148). Zero once
    the tip outruns the wind (lambda>=1)."""
    lam = tip_speed / rel_wind
    return cd * (1 - lam) ** 2 * lam if 0 <= lam < 1 else 0.0


def relative_wind(craft_speed_fraction):
    """Relative wind seen by a craft moving outbound at fraction f of wind speed."""
    return V_SW * (1 - craft_speed_fraction)


# --- materials (specific strength sets the tip-speed limit) ----------------
@dataclass(frozen=True)
class Material:
    name: str
    sigma_pa: float     # tensile strength
    rho: float          # density kg/m^3
    @property
    def specific_strength(self):       # J/kg
        return self.sigma_pa / self.rho

MATERIALS = [
    Material("Steel (HS)",        2.0e9, 7800),
    Material("Kevlar",            3.6e9, 1440),
    Material("Carbon fiber",      6.4e9, 1800),
    Material("Zylon (PBO)",       5.8e9, 1560),
    Material("CNT (theoretical)", 60.0e9, 1340),
]

def tip_speed_limit(mat, safety=2.0):
    """Max tip speed for a spinning cable: hoop stress 1/2 rho v^2 <= sigma/SF."""
    return math.sqrt(2.0 * (mat.sigma_pa / safety) / mat.rho)


# --- the turbine -----------------------------------------------------------
@dataclass
class Turbine:
    bubble_radius_m: float = 50_000      # 50 km bubble at the reference distance
    ref_au: float = 1.0                  # distance the bubble is sized at
    arm_length_m: float = 10_000         # 10 km cable arm
    tip_mass_kg: float = 1000            # mass of each tip bottle-generator
    tip_speed_ms: float = 1000           # operating tip speed (<= material limit)
    material: Material = MATERIALS[2]     # carbon fiber
    safety: float = 2.0
    fill_time_s: float = 3.0             # plasma bottle on/off switching time

    # derived ----------------------------------------------------------------
    def force(self, r_au=None):
        """Tip force. Constant-force (plasma-magnet) regime: F set at ref_au."""
        return bubble_force(self.bubble_radius_m, self.ref_au)

    def omega(self):
        return self.tip_speed_ms / self.arm_length_m

    def rotation_period(self):
        return 2 * math.pi / self.omega()

    def mech_power(self, r_au=None):
        """Extracted mechanical (=electrical) power: capture * F * v_tip."""
        return CAPTURE * self.force(r_au) * self.tip_speed_ms

    def available_power(self, r_au):
        return energy_flux(r_au) * math.pi * self.bubble_radius_m**2

    def capture_fraction(self, r_au):
        return self.mech_power(r_au) / self.available_power(r_au)

    def hub_stress(self):
        """Hoop stress at the hub from cable self-mass + tip mass."""
        rho = self.material.rho
        self_term = 0.5 * rho * self.tip_speed_ms**2          # per unit area, /A cancels
        return self_term  # dominant, area-independent term (Pa-equivalent)

    def cable_cross_section(self):
        """Cross-section needed to carry self-mass + tip mass within strength."""
        sa = self.material.sigma_pa / self.safety
        self_stress = 0.5 * self.material.rho * self.tip_speed_ms**2
        head = sa - self_stress
        if head <= 0:
            return math.inf          # tip speed exceeds material limit
        # tip-mass tension = m * v^2 / L ; stress = that / A  -> A = m v^2 /(L*head)
        return self.tip_mass_kg * self.tip_speed_ms**2 / (self.arm_length_m * head)

    def cable_mass_per_arm(self):
        A = self.cable_cross_section()
        return math.inf if A == math.inf else self.material.rho * A * self.arm_length_m

    def toggle_quarter_time(self):
        return self.rotation_period() / 4.0

    def radius_1g(self):
        """Radius along the arm where centripetal accel = 1 g."""
        return G0 / self.omega()**2

    def sail_dv_per_year(self, craft_mass_kg):
        """If fired asymmetrically as a pure sail: net thrust -> dv/year."""
        return self.force() / craft_mass_kg * YEAR

    def ion_thrust(self, isp_s=3000, eff=0.7):
        """Thrust if the generated power runs an ion drive instead."""
        ve = isp_s * G0
        return 2 * eff * self.mech_power() / ve


def pv_power(r_au, area_m2, eff=0.3):
    return SOLAR_CONST_1AU / r_au**2 * eff * area_m2


# ---------------------------------------------------------------------------
def hr(t):
    print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


def main():
    print(__doc__)
    t = Turbine()

    hr("1.  SOLAR WIND ENVIRONMENT vs DISTANCE")
    print(f"  {'r (AU)':>7} {'n (/cm^3)':>10} {'ram P (nPa)':>12} {'E-flux (W/m^2)':>15}")
    for r in (1, 2, 5, 10, 30):
        print(f"  {r:>7} {sw_number_density(r)/1e6:>10.3f} "
              f"{ram_pressure(r)*1e9:>12.4f} {energy_flux(r):>15.2e}")
    print("  Note: the wind speed stays ~constant; only the density thins (1/r^2).")

    hr("2.  TIP-SPEED LIMIT BY MATERIAL  (v_max = sqrt(2 * strength/SF))")
    print(f"  safety factor {t.safety:g}")
    print(f"  {'material':22} {'spec.strength (MJ/kg)':>21} {'v_tip_max (km/s)':>17}")
    for m in MATERIALS:
        print(f"  {m.name:22} {m.specific_strength/1e6:>21.2f} "
              f"{tip_speed_limit(m, t.safety)/1000:>17.2f}")
    print("  This is the classic spinning-tether limit. It caps extracted power,")
    print("  because P_mech = F x v_tip.")

    hr("3.  WORKED DESIGN POINT")
    F = t.force()
    print(f"  bubble radius     : {t.bubble_radius_m/1000:.0f} km  (sized at {t.ref_au:g} AU)")
    print(f"  -> tip force      : {F:.1f} N")
    print(f"  cable arm length  : {t.arm_length_m/1000:.0f} km")
    print(f"  material          : {t.material.name} (limit "
          f"{tip_speed_limit(t.material, t.safety)/1000:.2f} km/s)")
    print(f"  tip speed         : {t.tip_speed_ms/1000:.2f} km/s "
          f"(omega {t.omega():.4f} rad/s)")
    print(f"  rotation period   : {t.rotation_period():.0f} s "
          f"-> toggle window ~{t.toggle_quarter_time():.0f} s vs "
          f"{t.fill_time_s:g}s fill  "
          f"[{'OK' if t.toggle_quarter_time() > t.fill_time_s else 'TOO FAST'}]")
    print(f"  cable x-section   : {t.cable_cross_section()*1e4:.2f} cm^2 per arm")
    print(f"  cable mass        : {t.cable_mass_per_arm():.0f} kg per arm")
    print(f"  --> MECH POWER    : {t.mech_power()/1000:.1f} kW")
    print(f"      available flux : {t.available_power(t.ref_au)/1e6:.2f} MW "
          f"through the bubble")
    print(f"      capture        : {t.capture_fraction(t.ref_au)*100:.3f}% of available")
    print(f"  1-g spin-gravity at radius {t.radius_1g():.0f} m along the arm "
          f"(habitat shell)")

    hr("4.  THE HEADLINE: POWER IS ~FLAT WITH DISTANCE (vs PV which craters)")
    print("  Plasma-magnet 'constant-force' regime: the bubble grows as the wind")
    print("  thins, so tip force (and extracted power) stays ~constant. Compare to")
    print("  a 1000 m^2, 30%-efficient solar array.\n")
    print(f"  {'r (AU)':>7} {'turbine (kW)':>14} {'solar PV (kW)':>14} {'PV/turbine':>12}")
    pv_area = 1000
    for r in (1, 5, 10, 30):
        pw = t.mech_power() / 1000
        pv = pv_power(r, pv_area) / 1000
        print(f"  {r:>7} {pw:>14.1f} {pv:>14.2f} {pv/pw:>11.2f}x")
    cross = math.sqrt(pv_power(1, pv_area) / t.mech_power())
    print(f"  Crossover at ~{cross:.1f} AU (near Saturn): inside that PV wins, beyond")
    print("  it the turbine does, and by 30 AU it's not close. (Crossover moves out")
    print("  if you compare against a bigger solar array.)")

    hr("5.  SCALING THE BUBBLE: you can buy megawatts with size")
    print("  Power = capture * F * v_tip, and F scales with bubble AREA, so make")
    print("  the bubble bigger. (Tip speed fixed at the design value.)\n")
    print(f"  {'bubble R (km)':>14} {'force (N)':>11} {'mech power':>14}")
    for rk in (50, 150, 500, 1500):
        f = bubble_force(rk * 1000, t.ref_au)
        p = CAPTURE * f * t.tip_speed_ms
        pstr = f"{p/1e6:.2f} MW" if p >= 1e6 else f"{p/1e3:.0f} kW"
        print(f"  {rk:>14} {f:>11.1f} {pstr:>14}")
    print("  A few-hundred-km bubble is large but plausible for a plasma magnet")
    print("  far from the Sun (where it self-inflates anyway).")

    hr("6.  DUAL USE: generator <-> sail <-> ion <-> spin-gravity")
    craft = 8000
    print(f"  As a pure SAIL (fire one side): {F:.1f} N on a {craft/1000:.0f} t craft")
    print(f"     -> {t.sail_dv_per_year(craft)/1000:.0f} km/s of dv per year. "
          "Strong propulsion -- go any direction by phasing the bottles.")
    print(f"  Turbine power -> ION drive (Isp 3000s): only {t.ion_thrust():.2f} N thrust.")
    print(f"     => Direct sailing beats ion-from-turbine for THRUST; the generated")
    print(f"        power is better spent on the habitat, instruments, and the bottles.")
    print(f"  SPIN-GRAVITY: 1 g occurs at {t.radius_1g():.0f} m from the hub -- put a")
    print(f"     small always-on bubble + habitat module there for free 1-g living.")

    hr("7.  RIDING OUTBOUND: relative wind drops toward the tip speed")
    print("  As the craft sails outbound at fraction f of the wind speed, the wind")
    print("  it WORKS AGAINST is only v_rel = v_wind*(1-f). Your fixed (material-")
    print("  capped) tip speed becomes a bigger fraction of that -> the drag-turbine")
    print("  efficiency Cp climbs toward its lambda=1/3 optimum. BUT the available")
    print("  power falls as v_rel^3, and extracted power ~ v_rel^2 for a fixed tip.\n")
    area = math.pi * t.bubble_radius_m ** 2
    rho = sw_mass_density(t.ref_au)
    f_opt = 1 - 3 * t.tip_speed_ms / V_SW                  # lambda = 1/3
    print(f"  {'craft speed':>12} {'v_rel (km/s)':>13} {'lambda':>8} {'Cp':>8} "
          f"{'extracted':>12}")
    for f in (0.0, 0.5, 0.9, 0.99, f_opt):
        vr = relative_wind(f)
        lam = t.tip_speed_ms / vr
        cp = drag_cp(t.tip_speed_ms, vr)
        avail = 0.5 * rho * vr ** 3 * area
        ext = cp * avail
        tag = "  <- lambda=1/3 (peak Cp)" if abs(f - f_opt) < 1e-9 else ""
        estr = f"{ext/1000:.1f} kW" if ext >= 1000 else f"{ext:.2f} W"
        print(f"  {f*100:>10.2f}% {vr/1000:>13.1f} {lam:>8.3f} {cp:>8.4f} "
              f"{estr:>12}{tag}")
    print(f"\n  So your observation is exactly right: outbound, v_tip -> v_rel and the")
    print(f"  turbine becomes EFFICIENT (Cp 0.0025 -> 0.148, ~60x). The catch: the")
    print(f"  wind it's sipping has almost no power left, so ABSOLUTE output collapses.")
    print(f"  Upshot: a POWER STATION wants MAX relative wind -> stay put (orbit), where")
    print(f"  extracted power ~ v_rel^2 is greatest. The efficient-turbine regime is")
    print(f"  the bonus mode of a wind-RIDER near terminal speed: once it has stopped")
    print(f"  accelerating (no thrust left), it can still scavenge that faint residual")
    print(f"  wind at near-optimal efficiency to keep its own lights on.")

    hr("8.  ON AN EARTH-MARS CYCLER: power, and the mandatory drag")
    peri, apo = 1.0, 1.524
    a_au = (peri + apo) / 2
    a_m = a_au * AU
    def vis_viva_sun(r_au):
        return math.sqrt(GM_SUN * (2 / (r_au * AU) - 1 / a_m))
    vp, va = vis_viva_sun(peri), vis_viva_sun(apo)
    # max radial speed ~ on the leg; estimate from energy/momentum (order km/s)
    L = peri * AU * vp
    r_mid = a_au
    v_mid = vis_viva_sun(r_mid)
    v_tan_mid = L / (r_mid * AU)
    v_rad_mid = math.sqrt(max(v_mid**2 - v_tan_mid**2, 0))
    print(f"  Cycler ellipse {peri}-{apo} AU: v_peri {vp/1000:.1f} km/s, "
          f"v_apo {va/1000:.1f} km/s, peak radial ~{v_rad_mid/1000:.1f} km/s.")
    print(f"  Solar wind is {V_SW/1000:.0f} km/s; the craft's ~{v_rad_mid/1000:.0f} km/s "
          f"inbound barely dents it:")
    print(f"     inbound relative wind ~ {(V_SW+v_rad_mid)/1000:.1f} km/s "
          f"(+{v_rad_mid/V_SW*100:.1f}%), outbound ~ {(V_SW-v_rad_mid)/1000:.1f} km/s.")
    print(f"  => You're in the FULL-relative-wind regime everywhere on the cycle, so:")
    p_cf = t.mech_power() / 1000                                  # constant-force
    p_apo = CAPTURE * (t.force() / apo**2) * t.tip_speed_ms / 1000  # 1/r^2 at apo
    print(f"     extractable power ~ {p_apo:.1f}-{p_cf:.1f} kW "
          f"(1/r^2 worst-case at Mars .. constant-force), ~flat across the leg.")

    hr("    ...AND YES, IT ACTS AS DRAG (it has to)")
    F = t.force()
    for mass in (8000, 100_000):
        acc = F / mass
        half_leg = math.pi * math.sqrt(a_m**3 / GM_SUN)            # half-period
        dv = acc * half_leg
        print(f"  craft {mass/1000:.0f} t: sail force {F:.1f} N -> a={acc:.1e} m/s^2 "
              f"-> ~{dv/1000:.0f} km/s over the {half_leg/3.156e7:.2f}-yr inbound leg")
    print("""
  Momentum theory is brutal here: you CANNOT take energy from a flow without
  pushing back on it. Extracting power means slowing wind particles, and that
  reaction is a net ANTI-SUNWARD (downwind) force -- the magsail thrust itself.
  On the inbound leg that force directly opposes your sunward fall: real drag,
  exactly as expected. Two consequences:

  * The drag is there whether or not you spin the rotor -- it's the price of
    being a magnetic sail at all. Since v_tip (1 km/s) << wind (400 km/s),
    harvesting the kW barely changes the force, so the POWER is nearly free
    relative to the orbital perturbation you're already paying.
  * That perturbation is LARGE for a light craft (tens of km/s over a leg) --
    so a big power bubble doesn't 'ride' a cycler ballistically, it SAILS. You
    either run a small bubble to coast the cycle, or accept that you're now an
    active sail and steer the trajectory with the bottles (propellant-free).
    Same knob: dial the bubbles for power, station-keeping, or orbit changes.
""")

    hr("BOTTOM LINE")
    print("""
  * Tip speed is capped by the CABLE (spinning-tether limit), not the wind:
    at safety factor 2, ~0.5 km/s steel, ~1.9 km/s carbon fiber, ~6.7 km/s for
    theoretical CNT (roughly sqrt(2) higher with no margin).
  * Because P = F x v_tip and force scales with bubble area, you reach kW with a
    50 km bubble and MW with a few-hundred-km bubble -- you 'buy' power with size.
  * You only skim a tiny FRACTION of the wind's energy flux (tips are slow vs
    400 km/s), but the self-scaling bubble makes that power ~FLAT with distance,
    so it crushes solar panels in the outer system.
  * Longer cables = lower spin rate for the same tip speed = easier sail toggling
    and lower per-tip load, paid for in cable mass.
  * Same rig is a generator, a sail, an ion-power source, and a 1-g habitat.
    """)


if __name__ == "__main__":
    main()
