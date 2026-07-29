import bpy
import bmesh
from mathutils import Vector
from ..utils.bmesh_helpers import (
    is_face_on_plane, get_bmesh, plane_distance, transform_bmesh,
)


def _copy_faces_to_new_bmesh(source_faces: list[bmesh.types.BMFace]) -> bmesh.types.BMesh:
    new_bm = bmesh.new()
    vert_map = {}
    for face in source_faces:
        new_verts = []
        for vert in face.verts:
            if vert not in vert_map:
                new_vert = new_bm.verts.new(vert.co.copy())
                vert_map[vert] = new_vert
            new_verts.append(vert_map[vert])
        if len(set(new_verts)) >= 3:
            try:
                new_bm.faces.new(new_verts)
            except ValueError:
                pass
    new_bm.verts.ensure_lookup_table()
    new_bm.edges.ensure_lookup_table()
    new_bm.faces.ensure_lookup_table()
    return new_bm


def _remove_loose_geometry(bm: bmesh.types.BMesh):
    loose_verts = [v for v in bm.verts if not v.link_faces]
    while loose_verts:
        bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')
        bm.verts.ensure_lookup_table()
        loose_verts = [v for v in bm.verts if not v.link_faces]


def _get_perimeter_edges(bm: bmesh.types.BMesh) -> list[bmesh.types.BMEdge]:
    return [e for e in bm.edges if len(e.link_faces) == 1]


def _build_local_plane_basis(plane_no: Vector):
    if abs(plane_no.dot(Vector((1, 0, 0)))) < 0.999:
        arbitrary = Vector((1, 0, 0))
    else:
        arbitrary = Vector((0, 1, 0))
    u = (arbitrary - arbitrary.project(plane_no)).normalized()
    v = plane_no.cross(u).normalized()
    return u, v


def _order_perimeter_vertices(bm: bmesh.types.BMesh, perimeter_edges: list[bmesh.types.BMEdge]) -> list[bmesh.types.BMVert]:
    if not perimeter_edges:
        return []
    vert_edges = {}
    for edge in perimeter_edges:
        for v in edge.verts:
            vert_edges.setdefault(v, []).append(edge)
    visited = set()
    ordered = []
    for start_edge in perimeter_edges:
        if start_edge in visited:
            continue
        loop = []
        current_edge = start_edge
        current_vert = current_edge.verts[0]
        loop.append(current_vert)
        while current_edge not in visited:
            visited.add(current_edge)
            other = current_edge.verts[1] if current_edge.verts[0] == current_vert else current_edge.verts[0]
            loop.append(other)
            current_vert = other
            candidates = [e for e in vert_edges.get(current_vert, []) if e not in visited]
            if not candidates:
                break
            current_edge = candidates[0]
        if len(loop) > 1 and loop[0] == loop[-1]:
            loop.pop()
        ordered.extend(loop)
    return ordered


def project_to_plane_2d(points: list[Vector], plane_co: Vector, plane_no: Vector) -> list[Vector]:
    n = plane_no.normalized()
    u, v = _build_local_plane_basis(n)
    result = []
    for pt in points:
        projected = pt - plane_distance(pt, plane_co, n) * n
        delta = projected - plane_co
        result.append(Vector((delta.dot(u), delta.dot(v))))
    return result


def extract_cut_faces(half_a: bpy.types.Object, half_b: bpy.types.Object, cut_plane_co: Vector, cut_plane_no: Vector, distance_epsilon: float = 0.001, angle_epsilon: float = 0.001) -> dict:
    cut_no = cut_plane_no.normalized()
    result = {}
    for key, half in [('A', half_a), ('B', half_b)]:
        src_bm = get_bmesh(half, use_evaluated=True)
        mat_inv = half.matrix_world.inverted()
        local_co = mat_inv @ cut_plane_co
        local_no = (mat_inv.to_3x3() @ cut_no).normalized()
        cut_faces = [f for f in src_bm.faces if is_face_on_plane(f, local_co, local_no, distance_epsilon, angle_epsilon)]

        if not cut_faces:
            src_bm.free()
            empty_bm = bmesh.new()
            result[key] = {'bm': empty_bm, 'faces': [], 'vertices': [], 'edges': [], 'orientation': 0}
            continue

        avg_dot = sum(f.normal.dot(cut_no) for f in cut_faces) / len(cut_faces)
        orientation = 1 if avg_dot >= 0 else -1
        cut_bm = _copy_faces_to_new_bmesh(cut_faces)
        transform_bmesh(cut_bm, half.matrix_world)
        _remove_loose_geometry(cut_bm)
        result[key] = {'bm': cut_bm, 'faces': list(cut_bm.faces), 'vertices': list(cut_bm.verts), 'edges': list(cut_bm.edges), 'orientation': orientation}
        src_bm.free()
    return result


def get_cut_surface_bounds(cut_bmesh: bmesh.types.BMesh, plane_co: Vector = None, plane_no: Vector = None) -> dict:
    if not cut_bmesh.faces:
        return {'center': Vector((0, 0, 0)), 'bounds_2d': [], 'perimeter_edges': [], 'area': 0.0}

    all_verts = list(cut_bmesh.verts)
    center = sum((v.co for v in all_verts), Vector()) / len(all_verts)

    if plane_no is None:
        plane_no = sum((f.normal for f in cut_bmesh.faces), Vector())
        if plane_no.length > 0: plane_no.normalize()
        else: plane_no = Vector((0, 0, 1))
    else:
        plane_no = plane_no.normalized()
    if plane_co is None: plane_co = center

    perimeter_edges = _get_perimeter_edges(cut_bmesh)
    perimeter_verts = _order_perimeter_vertices(cut_bmesh, perimeter_edges)
    bounds_2d = project_to_plane_2d([v.co for v in perimeter_verts], plane_co, plane_no)
    total_area = sum(f.calc_area() for f in cut_bmesh.faces)

    return {'center': center, 'bounds_2d': bounds_2d, 'perimeter_edges': perimeter_edges, 'area': total_area}
