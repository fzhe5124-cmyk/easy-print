import math
import bmesh
from mathutils import Vector, Matrix


def build_peg_male(radius: float, depth: float, segments: int = 32, chamfer_radius: float = 0.0) -> bmesh.types.BMesh:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius, depth=depth)
    if chamfer_radius > 0.0:
        top_z = depth * 0.5
        _bevel_top_ring(bm, top_z, chamfer_radius)
    return bm


def build_peg_female(radius: float, depth: float, segments: int = 32, clearance: float = 0.15) -> bmesh.types.BMesh:
    r = radius + clearance
    d = depth + clearance
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r, radius2=r, depth=d)
    return bm


def build_peg_pair(radius: float, depth: float, segments: int = 32, clearance: float = 0.15):
    male = build_peg_male(radius, depth, segments)
    female = build_peg_female(radius, depth, segments, clearance)
    return male, female


def _bevel_top_ring(bm: bmesh.types.BMesh, top_z: float, chamfer_radius: float) -> None:
    eps = 1e-8
    top_edges = set()
    for vert in bm.verts:
        if abs(vert.co.z - top_z) < eps:
            for edge in vert.link_edges:
                ov = edge.other_vert(vert)
                if abs(ov.co.z - top_z) < eps:
                    top_edges.add(edge)
    if not top_edges:
        return
    bmesh.ops.bevel(bm, geom=list(top_edges), offset=chamfer_radius, offset_type="OFFSET",
                    segments=3, profile=0.5, affect="EDGES", clamp_overlap=True, loop_slide=True)
