"""
Orbital Lifeboats toolkit — calculators for an emergency-cache / rescue network.

Pure standard library. Modules:
  constants     bodies & physical constants
  astro         two-body mechanics + Lambert solver (validated)
  reachability  the two-budget (Δv + time) rescue model
  boiloff       storage timelines & solar-power falloff
  failures      failure-mode taxonomy with life-support clocks
  fleet         program sizing (stations -> fleet -> mass -> cost)
  presets       editable inputs (stations, design params, unit costs)
  svgplot       dependency-free SVG charting

Quick start:
  from orbital_lifeboats import reachability as R, presets
  R.max_reach_angle(6, 400, presets.STATIONS[0].radius)
"""

from . import (constants, astro, reachability, boiloff, failures, fleet,
               presets, svgplot)

__all__ = ["constants", "astro", "reachability", "boiloff", "failures",
           "fleet", "presets", "svgplot"]
