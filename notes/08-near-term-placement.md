# 08 — Where they actually go (near-term cislunar map)

Yes — we can name specific slots. The near-term theater is **Earth-Moon space
plus the Earth↔Moon transfer corridor** (and, stretching, the first crewed Mars
trajectories). Within that, the placement is not a free choice: it's driven by a
criterion I'd underweighted until now —

## The governing criterion: station-keeping cost

A fire-and-forget buoy that has to **burn propellant to hold its orbit** is slowly
eating the very reactant it's supposed to save for a rescue. So orbital
**stability is a primary selection filter**, not a footnote. Cislunar slots span a
wide range:

| Stability class | Station-keeping (order of magnitude) | Examples | Implication for a buoy |
|-----------------|--------------------------------------|----------|------------------------|
| **Truly stable** | ~0 for decades | DRO, EML4 / EML5 | Ideal "put it up and forget it." |
| **Nearly stable** | low, ~5–15 m/s/yr | NRHO | Cheap to hold; trivial for an ion bus. |
| **Unstable (saddle points)** | ~tens of m/s/yr, regular burns | EML1, EML2 halos | Great hubs, but they nibble propellant — less "forget it." |
| **Decaying** | continuous loss → reentry/impact | LEO, non-frozen LLO | Decay is a *feature* for crew return, a *bug* for buoy persistence. |

That table reorders the wish list: the slots that are best for *people* (NRHO,
EML1 — near the infrastructure) aren't always the slots best for *unattended
hardware* (DRO, the triangular points). The resolution is to use both kinds for
different jobs.

## The map

Roughly in priority order for the next decade or two.

| # | Slot | Stability | ~Δv to reach from LEO | What it serves | Variant (`07`) |
|---|------|-----------|----------------------|----------------|----------------|
| 1 | **Earth↔Moon transfer corridor** (TLI path) | n/a (a trajectory) | co-flown (breadcrumb) | every crewed lunar transit | corridor shelter |
| 2 | **NRHO** (lunar staging orbit) [†] | nearly stable | ~3.4–3.6 km/s + insertion | lunar staging | refuge |
| 3 | **LEO, on crewed-station planes** (ISS 51.6°, Tiangong ~41.5°, commercial) | decays | plane-matched (phasing only if co-planar) | crewed LEO stations | refuge |
| 4 | **EML1 halo** | unstable | ~3.77 km/s | Earth↔Moon staging hub, both directions | refuge / depot |
| 5 | **Frozen LLO** (i ≈ 27°, 50°, 76°, 86°) | quasi-stable *only* at frozen inclinations | ~4 km/s + | abort-to-orbit during descent / ascent | reentry-capable refuge |
| 6 | **DRO** (distant retrograde orbit) | truly stable (centuries) | higher than NRHO | the true set-and-forget strategic reserve | refuge, set-and-forget |
| 7 | **GEO belt** | very stable (slow drift) | ~3.9 km/s | comsats (uncrewed) | tug / refuel |
| 8 | **EML2 halo** | unstable | ~3.4–3.8 km/s | lunar far side, deep-space departures | refuge / relay |
| 9 | **EML4 / EML5** (triangular pts) | fully stable, ~0 | high, out of traffic | deep strategic reserve / staging depot | depot |
| 10 | **Lunar south-pole surface** | n/a (landed) | descent | base annex, ice→water→O2/H2 | base annex |

(Δv figures are order-of-magnitude, coplanar/ideal, from `napkin.py` §1 and the
standard cislunar Δv budget. Treat them as "which gap is bigger," not as mission
planning.)

## Notes per slot

- **The TLI corridor (#1) is the cheapest win and partly free.** Caches co-flown
  on a crewed lunar transfer (breadcrumb model, `04 §B`) are reachable by phasing.
  And **free-return trajectory design** (`04 §E`) is a *zero-hardware* lifeboat for
  the transit leg — Apollo 13's actual survival mechanism. Layer it in by default.
- **[†] Update (2026):** Gateway was **shelved in March 2026** (note 15), so NRHO
  is now a *staging orbit*, not a crewed node — the rescue demand there is
  transient (per-mission), not standing. The orbital mechanics below still hold.
- **NRHO (#2) is the anchor** *of the lander architecture*. It's nearly stable
  (~tens of m/s/yr at most). Co-locate refuge buoys with the traffic. Bonus: near-
  continuous Earth line-of-sight (good for the relay role) and south-pole access.
- **LEO (#3) is special.** Atmospheric decay is a built-in lifeboat (a dead ship
  comes home), so LEO doesn't need a *rescue-cache grid* — it needs **co-orbital
  safe havens on the specific planes where crewed stations fly.** One per busy
  plane; phasing covers the rest of that plane. This is the closest thing to a
  literal "lifeboat for the station next door," and there's historical precedent
  (the old ISS Crew Return Vehicle concept).
- **EML1 (#4) is the best *hub* but a mediocre *buoy site*** — it's a saddle
  point, so it needs regular station-keeping burns. Fine if it's a serviced depot;
  in tension with "forget it" if it's meant to be untended.
- **Frozen LLO (#5) has a trap:** ordinary low lunar orbits decay into the surface
  within months because of mascons (lunar gravity lumps). Only the *frozen*
  inclinations are quasi-stable. A buoy here must sit at a frozen inclination, or
  it violates the "don't put them on impacting trajectories" rule by accident.
- **DRO (#6) is the standout for the design philosophy.** It's stable for
  *centuries* with essentially no station-keeping — the purest "put it up and
  truly never think about it" slot. Higher Δv to reach than NRHO and a bit removed
  from surface traffic, so its role is the **deep-stable reserve**: park spare
  buoys here and let ion propulsion ferry them out to where they're needed.
- **GEO (#7)** is already a *commercial* reality (mission-extension vehicles tug
  and refuel dead comsats). It's uncrewed, so it's lower priority for the *human*
  rescue case, but it proves the tug-as-buoy economics today.
- **EML4/L5 (#9)** are free and perfectly stable but far from the action — strategic
  reserve, not first responders.

## Sequencing

1. **First (where people already are/going):** TLI-corridor breadcrumbs +
   free-return discipline, NRHO refuge buoys, LEO safe havens on crewed-station
   planes.
2. **Next (cislunar staging):** EML1 depot, frozen-LLO abort buoys, a DRO reserve
   pool that ion-ferries units outward.
3. **Later / commercial / strategic:** GEO tugs (already happening), EML2,
   EML4/L5 reserve, south-pole surface annex.

The pattern that falls out: **stage the standing reserve in the stable, boring
orbits (DRO, triangular points), and push working buoys into the busy-but-leaky
ones (NRHO, EML1, LEO planes) as traffic demands** — because the bus can move
itself (slowly) on ion, you don't have to launch each buoy directly to its final
post. You launch to the cheap stable parking lot and redistribute.

→ open problems (detection/wake, autonomy, Δv-vs-time, governance): `05`
