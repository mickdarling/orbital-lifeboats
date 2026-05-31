# 06 — Failure modes (what are we actually rescuing?)

The first three notes quietly assumed the emergency is "out of propellant." It
usually isn't. A ship can be **fuel-rich and still doomed** — a slow O2 leak, a
medical crisis, a holed hab with the crew in suits on a countdown clock, stuck in
an orbit with no way down. Each failure mode demands a *different* capability from
the buoy, and propellant is only relevant to a minority of them.

That's the key reframing: **this is not a fuel-depot network. It's a survival-
capability network, and "fuel depot" is just one of the capabilities.** The most
broadly useful thing a buoy holds is the stay-alive kit, because almost every
failure mode needs it and only the propulsion failures need propellant.

## The taxonomy

Grouped by *what capability the ship has lost*, because that's what the buoy has
to supply.

| # | Failure mode | What's lost | What the buoy must provide | Architecture (`04`) |
|---|--------------|-------------|----------------------------|---------------------|
| **A. Propulsion / Δv** | | | | |
| A1 | Main engine failure | ability to maneuver/return | a **tug** to move them, or propellant if their engine works | D (tug), A/B (prop) |
| A2 | Propellant leak / tanks dry | Δv budget | propellant transfer **or** a tug to do the moving | A, B, D |
| A3 | Stuck in wrong orbit, no way down | a survivable reentry/landing path | a buoy that can **become the reentry vehicle** and carry them down | D + reference design (`07`) |
| **B. Life support / consumables** | | | | |
| B1 | O2 generation fail / leak | breathable air | O2 + a pressurized refuge | A (node depot) |
| B2 | CO2 scrubber failure | air *quality* (CO2 rising) | scrubber media / a working cabin to transfer into | A |
| B3 | Water loss | drinking water, electrolysis feedstock | water (the universal commodity) | A |
| B4 | Power loss | everything downstream (LS, thermal, comms) | power + a refuge that has its own | A |
| B5 | Thermal control failure | habitable temperature | a thermally-regulated refuge | A |
| B6 | Consumables exhausted (mission overrun, missed window) | time | resupply to extend the life-support clock | A, B (convoy) |
| **C. Habitat integrity** | | | | |
| C1 | Hull breach / depress (debris, MMOD, collision) | pressure; crew now in suits on a **suit-duration clock** | a nearby **pressurized shelter to evacuate into**, fast | A, D |
| C2 | Fire | a safe atmosphere | refuge + medical + breathable air | A |
| C3 | Toxic contamination (NH3, hydrazine, smoke) | habitable cabin | clean refuge | A |
| **D. Medical** | | | | |
| D1 | Injury / acute illness | crew capability | medical supplies, stabilized environment, **telemedicine relay** | A + comms |
| D2 | Radiation sickness (post-SPE) | crew health | medical + a shielded space | A + G |
| **E. Crew / human factors** | | | | |
| E1 | Crew incapacitated (all down) | the pilots | **autonomy / remote piloting** + a beacon so help finds them | D (buoy is the brain) |
| **F. Comms / navigation** | | | | |
| F1 | Lost high-gain antenna / pointing / power | ability to call for help | the buoy is the **radio**: receives the weak squawk, relays it | D |
| F2 | Lost navigation | knowing where you are / how to rendezvous | the buoy is the **beacon** to home on | D + nav network |
| **G. Radiation event** | | | | |
| G1 | Solar particle event in transit, no good shelter | a safe place during the storm | a **water/regolith-shielded storm cellar** reachable in hours | A (hardened) |
| **H. Trajectory / schedule** | | | | |
| H1 | Partial burn → off-nominal trajectory | the planned path | consumables to survive the longer ride, or a corrective tug | B, D |
| H2 | Missed launch/return window | a timely way home | extend consumables until the next window, or a ride | A, B |
| **I. Cascading** | | | | |
| I1 | Power → thermal → life support chain failure | multiple systems at once | a full refuge that supplies *all* of it | A + reference design |

## What the table is telling us

- **The stay-alive kit beats the fuel tank.** Categories B, C, D, G, I — the
  majority of rows — are solved by **refuge + air + water + power + medical +
  comms**, not propellant. Only A (and parts of H) need propellant or a tug. A
  network optimized as a fuel-depot grid would miss most of the ways people
  actually die.
- **"Can't get down" is its own category (A3, C1, I1) and it's nasty.** A ship
  fuel-rich but unable to reenter — or a crew that has to *abandon ship entirely*
  because the hab is gone — needs the buoy to be a **lifeboat in the literal
  sense: something you climb into that can carry you down.** That single
  requirement drives much of the reference design in `07`.
- **The crew may be unable to help themselves (E1, F1, F2).** So the buoy can't
  assume a functioning pilot or radio on the other end. It must be able to
  *detect, reach, and relay* on its own.
- **Time is the hidden axis.** A suit-duration clock (C1) is hours; a consumables
  overrun (B6) is weeks. The same network looks very different depending on how
  fast the buoy has to get there. This is the model `05` flags as missing.

→ the design that tries to cover all of this: `07-the-standard-buoy.md`
