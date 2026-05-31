# 15 — Phase 2: Artemis & cislunar space

Phase 1 (notes 12) covered what's crewed today — LEO stations. Phase 2 is the
next human presence beyond LEO: **NASA's Artemis program.** And the architecture
just changed under us, which changes the rescue problem.

## What Artemis actually is now (verified May 2026)

The program was **restructured in February–March 2026**, so the cislunar picture
is different from what notes 08–09 assumed:

| Mission | Status / target | What it is |
|---------|-----------------|------------|
| **Artemis II** | **flew** (launched Apr 1, 2026; splashdown Apr 10) | Crewed lunar **free-return flyby** — first crew beyond LEO since Apollo 17 |
| **Artemis III** | ~late 2027 | **Restructured** to *Earth-orbit* lander tests — Orion docks with the SpaceX/Blue Origin landers in LEO, tests propulsion / life support / comms / suits. **No longer the first landing.** |
| **Artemis IV** | ~late 2028 | **First crewed lunar landing** |
| **Artemis V** | ~late 2028+ | Begins building a permanent (initially likely automated) **Moon base** |
| **Lunar Gateway** | **shelved (Mar 2026)** | The NRHO station is paused — **no permanent crewed node in cislunar space** |

> **Correction to earlier notes.** Notes 01, 02, 08, and 09 treated **NRHO /
> Gateway as the standing crewed cislunar node**. With Gateway shelved, that's no
> longer true: NRHO is now just a *staging orbit* for landers, not a place with
> people permanently in it. The orbital-mechanics analysis in those notes still
> holds (NRHO is still a real, nearly-stable orbit); only the "infrastructure /
> people are already there" premise is retired. This note supersedes it.

## What that does to the rescue problem

**There is no station to park lifeboats next to.** In Phase 2 the human presence
in cislunar space is **transient** — crews are out there only during Artemis
mission windows, until a surface base appears (~Artemis V). So Phase 2 is **not a
standing-coverage problem; it's an event-driven one** (note 11): you *surge*
guardians for each scheduled crewed flight and stand down between them.

And the physics is the unforgiving regime (note 09):
- **Phasing rescue is impossible.** Cislunar periods are *days* (NRHO ~6.5), so a
  co-orbital responder can't phase to a casualty inside any survival clock.
  Anything that helps must be **formation-flying / co-located** from the start.
- **No atmospheric decay** to bring a crippled ship home — the free LEO lifeboat
  is gone.
- **Deep gravity wells and big Δv gaps** mean a stranded crew's reachable set is
  tiny and nothing slow can get to them.

So Phase 2 leans entirely on the two cheapest tools we found: **trajectory-as-
lifeboat** (note 04 §E) and **pre-positioning at the scheduled burns** (note 11).

## The high-exposure moments to guard

Map the mission to its irreversible, predictable, catastrophic-on-failure events
— those are where pre-positioned guardians earn their keep (note 11 geometry):

| Event | Exposure | Coverage |
|-------|----------|----------|
| **TLI** (trans-lunar injection) | engine fails → wrong trajectory | Largely **free**: Orion flies free-return/hybrid trajectories (Artemis II did), so a failure loops the crew home. Add a hardware "no-burn guardian" on the original path as backup. |
| **LOI** (lunar orbit insertion) | miss it → fly past, no second chance | Pre-position a guardian / abort refuge near the nominal post-LOI orbit (frozen-LLO caveat, note 08). |
| **Powered descent / ascent** (Artemis IV+) | the single most exposed minutes; no abort-to-decay | A low-lunar-orbit abort refuge + a descent-abort guardian, pre-staged for the landing window. |
| **Earth-orbit lander tests** (Artemis III) | it's a LEO operation | Covered by **Phase-1** logic (notes 12) — co-orbital responders on the test orbit. |

The bright spot: because Orion's transit uses **free-return geometry**, the long,
scary cruise leg is mostly self-rescuing for free. The hardware burden concentrates
on **lunar-vicinity operations** (LOI, descent/ascent), which are exactly the
events you can pre-position for.

## Surface base (Artemis V+) and beyond

Once a surface base exists (~2028+), the pattern shifts to **surface caches at the
lunar south pole** — ice → water → O₂/H₂ (the base-annex pattern, notes 02/08).
And the **mass-driver delivery** idea (note 14 hook) becomes real only here: a
base with a mass driver can fling prepared emergency modules — including
would-be-boiloff propellant — fast to a cislunar casualty, attacking the *time*
budget by launch speed. That's **Phase 3.**

## Sizing Phase 2 (structural, not computed)

Quantitative cislunar reachability needs a three-body (CR3BP) model, which the
toolkit doesn't have yet (flagged in note 13). So this is structural:

- **Per crewed Artemis flight**, a surge package of pre-positioned, **expendable**
  guardians: a no-burn guardian on the free-return path, a formation lifeboat
  shadowing Orion, and — for landing missions — a low-lunar-orbit abort refuge
  plus a descent-abort guardian. Call it a **handful of stage-1s + one reentry-
  capable recovery vehicle** staged in cislunar.
- That fits comfortably in **well under one Starship launch** (note 14: ~12
  refuges or ~4 reentry lifeboats per flight). So the *launch* side of Phase 2 is
  one flight per Artemis window; the cost is in the cislunar-rated hardware and
  the CR3BP trajectory design, not the lift.

## Honest caveats
- **The schedule is fluid.** Artemis has slipped repeatedly and the Feb–Mar 2026
  restructuring (Gateway shelved, Artemis III re-scoped) is recent — treat dates
  as soft.
- **The numbers here are structural, not computed** — a CR3BP reachability module
  is the prerequisite for real cislunar Δv/time figures, and it's the clear next
  build (note 13).

---

## Sources (Artemis status, May 2026)
- [Artemis II — Wikipedia](https://en.wikipedia.org/wiki/Artemis_II)
- [Artemis III — Wikipedia](https://en.wikipedia.org/wiki/Artemis_III)
- [Artemis program — Wikipedia](https://en.wikipedia.org/wiki/Artemis_program)
- [NASA Outlines Preliminary Artemis III Mission Plans — NASA](https://www.nasa.gov/missions/artemis/artemis-3/nasa-outlines-preliminary-artemis-iii-mission-plans/)
