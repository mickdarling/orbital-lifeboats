# 05 — Open questions & rabbit holes

The fun unresolved parts. Roughly: physics, systems, economics, then the weird.

## Physics / trajectory
- **Phasing cost, done properly.** `napkin.py` §3 uses a crude single-burn
  phasing model. Do the real Lambert-solver version: given a buoy at a known
  phase on the same orbit and a ship with budget Δv and time T, what's the actual
  rendezvous cost curve? Where's the knee?
- **Low-thrust changes the whole game.** Everything here assumes impulsive
  chemical burns. A crippled ship with a working *ion/solar-electric* engine has
  a tiny thrust but potentially large total Δv given months. Does electric
  propulsion make off-node buoys reachable after all? (Probably yes for cargo,
  no for "we have 36 hours of O2 left.")
- **Three-body richness.** Real cislunar space has low-energy transfers (weak
  stability boundary / ballistic capture, the "Interplanetary Transport
  Network"). These could let a nearly-dead ship drift between nodes for almost no
  Δv — but slowly (weeks-months). Survival-time vs. Δv is the trade. Map it.
- **What's the actual reachable set of a real stranded ship?** Not "circular LEO
  + one burn" but: given a believable failure (lost main engine, RCS only; or
  half a tank; or full tank but a holed habitat) on a real trajectory, compute
  the set of caches reachable within the *life-support clock*, not just the Δv
  budget. Time is the second axis and this repo barely touches it.

## Systems / engineering
- **The standardization problem.** A cache helps a stranded ship only if they can
  physically connect and exchange. Whose docking standard? Whose propellant?
  Whose data/comms protocol? Is **water** the universal currency (everyone can
  use it; electrolyze for O2/propellant with power) the way to dodge propellant
  incompatibility?
- **Cache integrity over years.** How do you *know* a buoy you've never visited
  still has full tanks, working comms, and no micrometeorite holes? Self-
  reporting telemetry + periodic robotic inspection. A lifeboat you can't trust
  is worse than none (you route to it and it's empty).
- **The cooler-is-the-heartbeat problem.** Any active cryo cache lives or dies by
  its power+cooling chain running untended for years. Reliability budget? Or just
  accept passive storables for *emergency* tier and reserve active cryo for
  *routine refuel* depots that are serviced often?
- **Orbit maintenance.** Even "stable" nodes need station-keeping (L-points are
  saddle points; NRHO needs periodic burns). An unattended buoy must hold its
  published orbit for years or it isn't where the rescue plan says it is.
  Self-station-keeping = propellant the cache spends on itself = less for you.

## Economics / governance
- **Who pays for insurance nobody wants to use?** A buoy network is pure
  overhead until the day it saves a crew. WWII had a wartime state footing the
  bill. In a commercial/multi-national solar system, is this a treaty obligation
  (like maritime SOLAS / coast-guard duty-to-rescue), an insurance-funded
  consortium, or a public utility?
- **Duty to rescue, in space.** Maritime law obliges ships to aid those in
  distress. Is there / should there be an analogous **space duty-to-rescue**, and
  does that change the buoy-vs-tug math (every passing ship is a potential
  rescuer, so maybe you cache *propellant* for *them*, not refuge for the victim)?
- **Marginal buoy value.** Each added buoy covers more failure cases but at
  declining marginal value. Is there a clean curve: P(survival) vs. network size,
  for a given traffic model? That's the number that decides how big the network
  should be.

## The weird and the fun
- **Buoys as more than lifeboats.** A network of known-location, powered,
  comms-equipped nodes is also: a deep-space relay/navigation constellation (a
  solar-system GPS), a science platform network, propellant depots for routine
  ops, and emergency caches — all the same hardware. The lifeboat case may be the
  *justification* but not the *primary daily use*. Does dual-use change where you
  put them?
- **Reverse buoys / "message in a bottle."** Should a stranded crew be able to
  *release* a small high-Δv beacon/sample-return capsule toward a node even if the
  main ship can't move? Decouple "save the data/the message" from "save the ship."
- **Self-propelled smart caches.** Cheap, slow, electric-propulsion caches that
  *reposition themselves* to follow predicted traffic or drift toward a developing
  emergency. Blurs B/D — a buoy that slowly swims.
- **The grim actuarial question.** At what traffic volume does a rescue network
  become cheaper (in expected lives + ships) than just flying with bigger
  margins? Early on, the answer is probably "fly with margins and free-return
  trajectories"; the network earns out only at scale. Where's the crossover?

## Things to build next in this repo
- A proper Lambert/phasing rendezvous-cost calculator.
- A time-axis model: life-support clock vs. reachable caches.
- A toy "traffic + failures → P(survival) vs. network size" Monte Carlo.
- Real boiloff numbers per tank size (surface/volume scaling) instead of flat
  %/day.
