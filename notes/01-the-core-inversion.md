# 01 — The core inversion

## The Channel buoy works because water is forgiving

A pilot in the Channel can swim in any direction. Effort buys motion. The buoy
sits still, anchored, and the swimmer closes the gap under his own power. The
sea doesn't carry the buoy away at 8 km/s.

Space removes every one of those forgiving properties:

- **You can't "swim."** A spacecraft moves only by expending reaction mass. A
  ship that is *out of propellant* — the exact scenario that makes a lifeboat
  necessary — has a reachable set of essentially **zero**. It coasts on its
  current conic section and stays there.
- **Nothing is anchored.** A buoy in orbit is itself moving at orbital velocity.
  Two objects on different orbits have a large *relative* velocity even when
  they're spatially close.
- **"Close" is meaningless; Δv is the metric.** Two craft can pass within meters
  and need kilometers-per-second to actually match orbits and dock. Proximity is
  not reachability.

Run `napkin.py` §4: a ship with 100 m/s left in the tank can raise its LEO
apoapsis by all of ~365 km. With 500 m/s, ~2,100 km. The crippled ship cannot
come to the buoy. So either the buoy is *already where the ship will be*, or
something with fuel must go to the ship.

## Two regimes

### Nodes — the buoy works as intended

Some places in space are **low-relative-velocity congregation points**:

- **Lagrange points** (especially Earth-Moon L1 and L2): quasi-stable, cheap to
  hold station, and everything transiting cislunar space passes nearby at low
  relative speed.
- **Halo / NRHO orbits** (where Gateway lives): same idea, a natural parking
  loop.
- **Planetary parking orbits, the GEO belt, sun-synchronous**: traffic clusters
  here and shares planes/energies.

At a node, a nearby ship needs only a small Δv — often just a phasing maneuver
(§3, tens to ~hundred m/s) — to close in. **This is where passive "swim-to-it"
buoys genuinely work.** Park caches at nodes.

### Corridors — the buoy must come to you

Interplanetary transfers are the opposite. On an Earth→Mars trajectory you're on
a heliocentric ellipse moving ~30 km/s, and anything not on your *exact* ellipse
is moving km/s relative to you. A randomly-placed buoy in the corridor is
unreachable for a healthy ship, never mind a crippled one (§2: even a 10° plane
change is 1.3 km/s in LEO; heliocentric plane changes are worse).

Two ways to make a corridor lifeboat real, neither of which is a passive buoy:

1. **Breadcrumb / convoy model.** Launch caches *ahead of the crew on the
   identical transfer trajectory*, in the same launch window. Now the cache and
   the ship share an orbit, and reaching it collapses to a cheap phasing
   problem. The cache is a passive object, but its placement is anything but
   random — it's co-flown. (See `04-architectures.md`.)
2. **Rescue tug.** A cache *with its own propulsion and an active power source*
   that maneuvers to intercept a stricken ship. This is the real generalization
   of the Channel buoy to open space — except the buoy now swims to *you*. It's
   a coast-guard cutter, not a float.

## The reframed thesis

> In the Channel, the lifeboat is passive and the survivor is mobile.
> In open space, the survivor is immobile and the lifeboat must be mobile —
> *unless* you place the cache where the survivor was always going to be.

And the corollary that follows from "the survivor is immobile": **whatever Δv,
power, comms, and navigation the rescue needs has to live in the rescuer, not the
victim.** The crippled party may be a bare survival capsule or a tank-dry stage
with literally zero maneuvering left and a dead antenna. So the active "buoy"
isn't just a supply cache that happens to have an engine — it's the element that
*owns the capability the victim has lost*: it does the moving, it does the
calling-for-help, and it's the beacon the help homes in on. The capsule's only
job is to keep its crew alive and be findable. (Developed in
`04-architectures.md` §D.)

Everything else in this repo is working out **where the survivor was always
going to be** (the nodes and the planned corridors), because those are the only
places a *passive* cache earns its mass.

→ next: `02-where-buoys-work.md`
