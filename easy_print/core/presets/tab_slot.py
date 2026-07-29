import bmesh
from mathutils import Vector, Matrix


def _box_verts(bm, half_w, half_d, z_min, z_max):
    v0 = bm.verts.new((-half_w, -half_d, z_min))
    v1 = bm.verts.new(( half_w, -half_d, z_min))
    v2 = bm.verts.new(( half_w,  half_d, z_min))
    v3 = bm.verts.new((-half_w,  half_d, z_min))
    v4 = bm.verts.new((-half_w, -half_d, z_max))
    v5 = bm.verts.new(( half_w, -half_d, z_max))
    v6 = bm.verts.new(( half_w,  half_d, z_max))
    v7 = bm.verts.new((-half_w,  half_d, z_max))
    return [v0, v1, v2, v3, v4, v5, v6, v7]


def _box_faces(bm, v):
    bm.faces.new((v[0], v[3], v[2], v[1]))
    bm.faces.new((v[4], v[5], v[6], v[7]))
    bm.faces.new((v[0], v[1], v[5], v[4]))
    bm.faces.new((v[2], v[3], v[7], v[6]))
    bm.faces.new((v[1], v[2], v[6], v[5]))
    bm.faces.new((v[3], v[0], v[4], v[7]))


def build_tab_male(width=5.0, depth=5.0, height=5.0, fillet_radius=0.0):
    bm = bmesh.new()
    v = _box_verts(bm, width/2, depth/2, 0, height)
    _box_faces(bm, v)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def build_tab_female(width=5.0, depth=5.0, height=5.0, clearance=0.15):
    return build_tab_male(width + clearance, depth + clearance, height + clearance * 0.5)


def build_tab_pair(width=5.0, depth=5.0, height=5.0, fillet_radius=0.0, clearance=0.15):
    return build_tab_male(width, depth, height, fillet_radius), build_tab_female(width, depth, height, clearance)
