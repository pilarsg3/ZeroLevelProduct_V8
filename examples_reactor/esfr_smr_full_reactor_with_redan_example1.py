"""
esfr_smr_full_reactor_with_redan_example1.py
─────────────────────────────────────────────
Full-reactor (skeleton) assembly demonstrating the new `redan` component,
built the ZLP way: every component is a SPEC DICT, assembled through
assemble_objects().

The redan's three anchor points are derived from the surrounding components,
exactly as described in the sketch:

    A = intersection of the reactor top plate and the inner wall of the RPV
          → radius = RPV inner radius,  z = RPV straight height (top plate bottom)
    B = where the top of the core starts
          → radius = redan lower-cylinder radius,  z = core top
    C = the bottom of the core, but the shell extends down to rest on the
        strongback
          → radius = redan lower-cylinder radius,  z = strongback top

All lengths are in metres.  The redan wall thickness is 0.025 m (= 25 mm).

Registration
------------
The dict interface dispatches via PREMADE_BUILDERS, calling the registered
entry as builder(spec_dict).  Since create_redan() takes keyword arguments
(like every other create_* function), register a dict-unpacking wrapper.
Add this once to components_premade/__init__.py, alongside the existing
component registrations:

    from .components_premade_redan import create_redan

    _REDAN_META = {"obj_type", "obj_id", "operation", "name", "color",
                   "center_coords", "center_coords_pol", "rotation_angles",
                   "insert_into", "material", "material_tag", "manual_placement"}

    def _build_redan(obj):
        return create_redan(**{k: v for k, v in obj.items()
                               if k not in _REDAN_META})

    PREMADE_BUILDERS["redan"] = _build_redan

The defensive register below lets this script run even before you edit it.
"""

from __future__ import annotations

import math

from assemble import assemble_objects

# ── Make `redan` available to the dict-driven builder ─────────────────────
# build_premade_component() calls PREMADE_BUILDERS[obj_type](obj), passing the
# WHOLE spec dict as one positional argument — so the registered entry must be
# a dict-unpacking wrapper, not the kwargs-based create_redan() directly.
from components_premade import PREMADE_BUILDERS
from components_premade.components_premade_redan import create_redan

_REDAN_META = {"obj_type", "obj_id", "operation", "name", "color",
               "center_coords", "center_coords_pol", "rotation_angles",
               "insert_into", "material", "material_tag", "manual_placement"}


def _build_redan(obj):
    return create_redan(**{k: v for k, v in obj.items() if k not in _REDAN_META})


PREMADE_BUILDERS.setdefault("redan", _build_redan)


# ════════════════════════════════════════════════════════════════════════
#  1.  Shared reactor geometry (metres)
# ════════════════════════════════════════════════════════════════════════

# ── Reactor vessel ────────────────────────────────────────────────────────
RPV_INNER_D    = 4.72
RPV_INNER_R    = RPV_INNER_D / 2.0          # 2.36
RPV_WALL_T     = 0.04
RPV_STRAIGHT_H = 5.50                       # shell runs z = 0 → 5.50
TOP_PLATE_T    = 0.10                        # plate bottom flush at z = 5.50

# ── Strongback (support; rests near the vessel bottom) ────────────────────
SB_Z_BOTTOM = -1.00
SB_HEIGHT   = 0.90
SB_TOP      = SB_Z_BOTTOM + SB_HEIGHT       # -0.10   (← redan point C sits here)

# ── Diagrid (sits on the strongback) ──────────────────────────────────────
DIAGRID_DIAM  = 2.80                        # r = 1.40
DIAGRID_THICK = 0.70
DIAGRID_Z_BOT = SB_TOP                      # -0.10
DIAGRID_TOP   = DIAGRID_Z_BOT + DIAGRID_THICK   # 0.60

# ── Core (hexagonal prism, sits on the diagrid) ───────────────────────────
CORE_R     = 1.20                           # circumscribed radius
CORE_H     = 1.00
CORE_Z_BOT = DIAGRID_TOP                    # 0.60
CORE_Z_TOP = CORE_Z_BOT + CORE_H            # 1.60   (← redan point B sits here)

# ── Redan ─────────────────────────────────────────────────────────────────
REDAN_LOWER_R    = 1.50                     # clears core (1.20) and diagrid (1.40)
REDAN_THICKNESS  = 0.025                    # 25 mm
REDAN_SHOULDER_Z = 3.00                     # top cylindrical section ends here

# ── Derived redan anchors ─────────────────────────────────────────────────
A = (RPV_INNER_R,   RPV_STRAIGHT_H)         # (2.36,  5.50)
B = (REDAN_LOWER_R, CORE_Z_TOP)             # (1.50,  1.60)
C = (REDAN_LOWER_R, SB_TOP)                 # (1.50, -0.10)


# ════════════════════════════════════════════════════════════════════════
#  2.  Component spec dicts  (this is the "dictionary input")
# ════════════════════════════════════════════════════════════════════════

specs = [
    {
        "operation": "primitive",
        "obj_type":  "reactor_vessel",
        "obj_id":    "rpv",
        "inner_d":    RPV_INNER_D,
        "wall_t":     RPV_WALL_T,
        "straight_h": RPV_STRAIGHT_H,
        "bottom_head_type":   "ellipsoidal",
        "bottom_head_params": {"head_depth": 1.0},
        "top_plate_thickness": TOP_PLATE_T,
        "top_plate_hole_groups": [
            {"hole_diameter": 0.52, "layout": "custom_angles",
             "angles_deg": [0.0, 90.0, 180.0, 270.0], "placement_radius": 1.85},
        ],
    },
    {
        "operation": "primitive",
        "obj_type":  "strongback",
        "obj_id":    "strongback",
        "total_height":       SB_HEIGHT,
        "flange_radius":      1.60,          # >= redan outer radius so the
                                             # redan ring can rest on it
        "skirt_outer_radius": 1.00,
        "skirt_inner_radius": 0.70,
        "skirt_height":       0.40,
        "taper_bottom_z":     0.30,
        "bore_radius":            0.30,
        "small_hole_radius":      0.07,
        "small_hole_count":       6,
        "small_hole_placement_r": 1.10,
        "z_bottom": SB_Z_BOTTOM,
    },
    {
        "operation": "primitive",
        "obj_type":  "diagrid",
        "obj_id":    "diagrid",
        "diameter":  DIAGRID_DIAM,
        "thickness": DIAGRID_THICK,
        "z_bottom":  DIAGRID_Z_BOT,
    },
    {
        "operation": "primitive",
        "obj_type":  "reactor_core",
        "obj_id":    "core",
        "radius":   CORE_R,
        "height":   CORE_H,
        "z_bottom": CORE_Z_BOT,
        "n_sides":  6,
    },
    {
        "operation": "primitive",
        "obj_type":  "redan",
        "obj_id":    "redan",
        "r_top":    A[0],          # A
        "z_top":    A[1],          # A
        "r_lower":  REDAN_LOWER_R, # B, C
        "z_knee":   B[1],          # B
        "z_bottom": C[1],          # C
        "thickness":      REDAN_THICKNESS,
        "z_shoulder":     REDAN_SHOULDER_Z,
        "thickness_side": "in",    # A–B–C is the OUTER surface
    },
]


# ════════════════════════════════════════════════════════════════════════
#  3.  Assemble + export  (STEP gets per-part obj_id names)
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Redan anchors:")
    print(f"  A (top plate ∩ RPV inner wall) = {A}")
    print(f"  B (top of core)                = {B}")
    print(f"  C (strongback top)             = {C}")

    assembly = assemble_objects(
        specs,
        export_path="output/esfr_smr_with_redan.step",
    )

    try:
        from ocp_vscode import show
        show(assembly)
    except Exception as exc:   # viewer unavailable — STEP is still saved
        print(f"(viewer unavailable: {exc})")