"""Physical constants and bodies. Units: km, s, kg unless noted."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Body:
    name: str
    mu: float          # gravitational parameter, km^3/s^2
    radius: float      # mean radius, km
    orbit_au: float = 0.0   # heliocentric distance, AU (0 = not applicable)


# --- gravitational parameters (km^3/s^2) -----------------------------------
SUN   = Body("Sun",   1.327_124e11, 696_000.0)
EARTH = Body("Earth",     398_600.0,   6_378.0, 1.000)
MOON  = Body("Moon",        4_902.8,   1_737.4)
MARS  = Body("Mars",       42_828.0,   3_389.5, 1.524)
JUPITER = Body("Jupiter", 1.266_865e8, 69_911.0, 5.203)
SATURN  = Body("Saturn",  3.793_120e7, 58_232.0, 9.537)

AU = 1.495_979e8           # km
G0 = 9.80665               # m/s^2 (for Isp -> exhaust velocity)

# convenience
DAY = 86_400.0
HOUR = 3_600.0

# Earth-Moon geometry
EARTH_MOON_DIST = 384_400.0   # km
GEO_RADIUS = 42_164.0         # km
