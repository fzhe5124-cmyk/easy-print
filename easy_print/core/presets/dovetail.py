import math
import bmesh
from mathutils import Vector, Matrix


def _build_rail(bm, rail_length, top_width, bottom_width, height):
    hl = rail_length / 2.0
    htw = top_width / 2.0
    hbw = bottom_width / 2.0
    v0 = bm.verts.new((-hl, -hbw, 0))
    v1 = bm.verts.new(( hl, -hbw, 0))
    v2 = bm.verts.new(( hl,  hbw, 0))
    v3 = bm.verts.new((-hl,  hbw, 0))
    v4 = bm.verts.new((-hl, -htw, height))
    v5 = bm.verts.new(( hl, -htw, height))
    v6 = bm.verts.new(( hl,  htw, height))
    v7 = bm.verts.new((-hl,  htw, height))
    bm.verts.ensure_lookup_table()
    bm.faces.new((v0, v3, v2, v1))
    bm.faces.new((v4, v5, v6, v7))
    bm.faces.new((v0, v1, v5, v4))
    bm.faces.new((v2, v3, v7, v6))
    bm.faces.new((v0, v4, v7, v3))
    bm.faces.new((v1, v2, v6, v5))
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))


def build_dovetail_male(width=5.0, depth=10.0, height=3.0, taper_angle_deg=20.0):
    taper = math.radians(taper_angle_deg)
    bottom_w = width - 2.0 * height * math.tan(taper)
    if bottom_w <= 0:
        bottom_w = width * 0.3
    bm = bmesh.new()
    _build_rail(bm, depth, width, bottom_w, height)
    return bm


def build_dovetail_female(width=5.0, depth=10.0, height=3.0, taper_angle_deg=20.0, clearance=0.10):
    taper = math.radians(taper_angle_deg)
    w = width + clearance
    h = height + clearance * 0.5
    d = depth + clearance * 2.0
    bottom_w = w - 2.0 * h * math.tan(taper)
    if bottom_w <= 0:
        bottom_w = w * 0.3
    bm = bmesh.new()
    _build_rail(bm, d, w, bottom_w, h)
    return bm


def build_dovetail_pair(width=5.0, depth=10.0, height=3.0, taper_angle_deg=20.0, clearance=0.10):
    return (build_dovetail_male(width, depth, height, taper_angle_deg),
            build_dovetail_female(width, depth, height, taper_angle_deg, clearance))
