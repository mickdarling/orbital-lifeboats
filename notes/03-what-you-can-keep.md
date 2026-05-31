# 03 — What you can actually keep in a cache

A lifeboat is only useful if its supplies are still good when you arrive — which
might be **years** after it was placed. This is where physics quietly vetoes the
obvious choices. Run `napkin.py` §5 for the timeline table.

## The boiloff hierarchy

Heat always leaks in. For a cryogen, leaked heat = boiloff = lost propellant
(and rising tank pressure you must vent). Passive insulation (multi-layer
insulation, MLI, plus sunshades) slows it but never stops it. Roughly, from
worst to best for a *passive* cache:

| Commodity | Storage temp | Passive lifetime | Verdict for an emergency cache |
|-----------|-------------|------------------|-------------------------------|
| Liquid hydrogen (LH2) | 20 K | days–weeks | **Avoid.** Low density, tiny molecule, huge heat leak. Loses ~1%/day passively. A multi-year LH2 cache is a slow leak with extra steps. |
| Liquid methane (LCH4) | 112 K | months | Plausible with good MLI. ~0.1%/day. Co-stores well with LOX (similar temps). |
| Liquid oxygen (LOX) | 90 K | months | Same class as methane. The oxidizer half of a methalox cache. |
| **Storables** (hydrazine, MMH/NTO) | ambient | **years–decades** | **The default for passive caches.** Zero boiloff, flight-proven on multi-year missions. Lower performance (Isp ~320 s vs ~360 methalox), toxic, but they're *there when you arrive.* |
| **Water** | ambient | indefinite | The MVP commodity. Drink it, breathe it (electrolysis → O2), shield with it, and — given power — split it into H2/O2 propellant on demand. |
| **Gases** (O2, N2, high-pressure) | ambient | indefinite | Heavy tanks, but trivially storable. Life support's core need. |
| Food, CO2 scrubber media, spares | ambient | years | Packaging-limited, not physics-limited. |

## The key design fork: passive vs. active

**Passive cache** (MLI + sunshade, no power for cooling):
- Holds storables / water / gas indefinitely; cryogens only briefly.
- Cheap, simple, nothing to fail, nothing to keep alive.
- This is what a *true* emergency buoy should be — you can't assume a cooler has
  been running flawlessly for the 4 years since deployment.

**Active / zero-boiloff cache** (cryocoolers, needs continuous power):
- Holds methalox/hydrolox indefinitely — high performance on tap.
- Requires power that never quits, and power is the single point of failure.
- Solar power falls off as 1/r² (§5): 100% at Earth, 43% at Mars, **3.7% at
  Jupiter, 1.1% at Saturn**. Past the belt, "active" means **nuclear** (RTG or
  fission), not solar.

## The pragmatic cache loadout

A sensible emergency buoy probably carries a **layered** inventory by storability:

1. **Tier 1 — always good (passive):** water, O2/N2, food, CO2 scrubbers, a
   pressurized refuge, comms relay, medical, a charged battery, docking adapter.
   This is the "stay alive and call home" kit. Pure Channel-buoy.
2. **Tier 2 — storable propellant:** hydrazine / NTO-MMH for attitude control
   and modest maneuvers. Lets a stranded ship stabilize and nudge, or lets a
   rescue craft top off. Good for years.
3. **Tier 3 — high-performance propellant (active only, node locations only):**
   methalox/hydrolox with ZBO cooling, at cislunar/Mars nodes where solar power
   is strong and the cache is regularly serviced. This is the "fill the tanks
   and continue the mission" kit, not the "survive" kit.

## Things that bite

- **Pressure, not just mass.** Even slow boiloff raises tank pressure; a passive
  cryo cache must vent, which is *more* loss and a tiny thrust that perturbs its
  orbit over years. Storables sidestep this entirely.
- **Radiation degrades stuff.** Food, polymers, electronics, batteries all age
  under GCR/SPE exposure. Water/regolith shielding helps and is dual-use.
- **Propellant compatibility.** A hydrolox ship can't use a methalox cache. A
  storables-only cache helps everyone for life support but only storables-burning
  craft for propulsion. Standardization (or water-as-universal-feedstock +
  on-site electrolysis) is a real architectural question.
- **The cooler is the cache's heartbeat.** Any active cache is really a small
  power plant that happens to hold propellant. Its reliability *is* the cache's
  reliability.

→ next: `04-architectures.md`
