# 10 — The triage swarm: echeloned response, not a single buoy

Stop thinking about "a buoy" (or a lifeboat, or a tug). Think about a **staged
sequence of inbound assistance modules** that converge on a casualty in waves —
a triage process. This reframing isn't just tidier; it **dissolves the central
contradiction** the reachability math exposed.

## The contradiction it resolves

Note 09 trapped the single-buoy concept: to be useful it had to be *close, fast,
and light* (to beat the life-support clock) **and** *heavy and complete* (to
actually fix the problem). Those fight. A do-everything buoy dense enough to be
close everywhere is unaffordable; a complete one is too heavy to scatter.

Staging breaks the trap, because **the first module's product isn't supplies —
it's time.** It stems the bleeding, the clock extends, and everything slower
becomes reachable. The two-budget problem (Δv *and* time) that had no single-
buoy solution turns into a *solvable sequence*.

`reachability.py` §5 shows the cascade concretely: a 6-hour LEO emergency only
admits a co-orbital responder within ~100° (or a formation lifeboat alongside).
But once stage 1 adds ~5 days of consumables, the clock is ~120 h — and now the
full co-orbital ring is reachable cheaply, an ion tug can deliver ~200–400 m/s
(so it can come from a node), and ordinary Hohmann transfers fit. **Buying time
turns the whole network from "unreachable" to "converging."**

## The echelons (with the medic/coast-guard analogy)

This is exactly **echelons of care** in emergency medicine and the military
(Role 1 → 4: point-of-injury first aid → forward stabilization → field hospital →
definitive care). Each echelon trades arrival speed against capability.

| Stage | Name | Arrives | Triage function | Propulsion | Payload | Distribution |
|-------|------|---------|-----------------|-----------|---------|-------------|
| **1** | **Connect** | minutes–hours | *Stem the bleeding.* Physically link up, open a comms relay, push emergency O2 / power / pressure, give the crew a shelter and a clock extension. **Diagnoses the failure** and reports it. | chemical (fast) | minimal, universal | **most numerous**, pre-staged *close* / formation-flying with crewed assets |
| **2** | **Sustain** | hours–days | *Stabilize.* Deliver the *specific* resources the diagnosed emergency needs — fuel, power, radiators, O₂, scrubbers, medical — composed to the case. | chemical or fast electric | modular, **diagnosis-driven** | fewer, staged at nodes |
| **3** | **Recover** | days–weeks | *Repair → recover → return.* The heavy element: full repair capability, a tug to move them, or the reentry vehicle to bring them home. The "homing event" where resources converge. | ion (slow now OK) | heavy, complete | **rare**, from the stable reserve (DRO, L4/5) |

The user's phase sequence maps straight onto it: **stem the bleeding** (stage 1)
→ **stabilize** (stage 2) → **repair → recovery → return** (stage 3).

## Why this is the efficient architecture

- **You replicate only the cheap capability.** The thing that must be dense and
  everywhere is *stage 1* — small, light, mass-produced, chemical. The expensive,
  heavy *stage 3* capability can be **rare**, because once stage 1 has bought time,
  stage 3 can come slowly from far away. You stop paying to put a complete
  hospital next to every patient; you put a medic next to every patient and one
  hospital in the region.
- **It generalizes note 09's fleet split.** That note found two roles (chemical
  responder / ion repositioner). The triage swarm is the richer n-echelon version:
  stage 1 *is* the chemical first responder, stage 3 *is* the ion reserve, and
  stage 2 is the middle tier the two-role model was missing.
- **The modules are the plug-in payloads from note 07**, now *dispatched in
  waves* instead of pre-integrated. The common bus is the same; what differs is
  which modules fly when, decided by the diagnosis.

## Diagnosis-driven dispatch + convergence

Stage 1's connect-and-report step is the linchpin. The failure-mode taxonomy
(note 06) isn't known in advance — stage 1 *determines* it on arrival (O₂ leak?
power loss? holed hab? medical? stuck-no-way-down?). That diagnosis:
- composes **stage 2's payload** (radiators for a thermal failure; scrubbers for
  CO₂; propellant for a Δv loss; meds for an injury),
- decides whether **stage 3** is even needed, and *which* stage 3 (a tug to move
  them vs. a reentry vehicle to bring them down vs. a repair rig).

Then the **convergence / "homing event"**: from the distributed network, the
nearest-reachable-in-time element of each needed echelon is tasked to flow toward
the casualty. The stricken ship becomes, briefly, the node the whole local
network orbits-toward. This is a many-to-one routing-and-scheduling problem layered
on top of the reachability math — *who can get there, with what, by when.*

## What it changes in the numbers

- **Stage-1 density** is the real cost driver (it has the hard proximity + clock
  constraint). But stage 1 is the *cheapest* unit, so dense stage-1 coverage on
  crewed orbits is affordable — and per note 09, even a 6-hour LEO clock needs
  only ~2 co-orbital stage-1s per crewed plane (plus formation lifeboats at
  GEO/NRHO where the period floor bites).
- **Stage-3 scarcity** is now acceptable: maybe a handful in the whole cislunar
  system, parked in stable reserve orbits, ion-ferried to wherever a stabilized
  casualty waits. The expensive capability stops needing to be everywhere.
- Net: the program cost reshapes from "N complete lifeboats" to "many cheap
  medics + some mid-tier resupply + a few heavy recovery rigs" — almost certainly
  cheaper for the same survival coverage.

## New open questions this raises
- **Command of the convergence.** Who/what coordinates a multi-module, multi-
  origin response in seconds, possibly with a silent or incapacitated crew? An
  autonomous "incident commander" function has to live *somewhere* — stage 1, the
  network, or the ground (with light-lag caveats deep in cislunar space).
- **Graceful degradation.** What if stage 2 can't make it, or arrives partial?
  The echelons need to fail soft — stage 1 should buy *enough* time that a missed
  stage 2 isn't fatal, and stage 3 should be able to substitute for a failed
  stage 2 (at the cost of speed).
- **Stage-1 sizing is now a clock-extension problem,** not a supply problem: how
  many days of life support must "Connect" deliver to guarantee the slowest
  necessary stage-3 can still arrive? That product — *time bought vs. stage-3
  reach* — is the key sizing equation, and it's the natural next calculation.
