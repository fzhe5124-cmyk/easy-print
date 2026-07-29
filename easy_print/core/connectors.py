from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Optional

import bmesh
import bpy
from mathutils import Matrix, Vector

from ..utils.bmesh_helpers import (
    apply_all_modifiers, duplicate_object, get_bmesh,
    move_to_collection, transform_bmesh, write_bmesh,
)
from .presets.dovetail import build_dovetail_female, build_dovetail_male
from .presets.peg_hole import build_peg_female, build_peg_male
from .presets.tab_slot import build_tab_female, build_tab_male
from .surface_extractor import extract_cut_faces, get_cut_surface_bounds

logger = logging.getLogger(__name__)

_PC_PREFIX = "_pc_ctemp"
_CONNECTOR_RESULTS = "Cut Results"


@dataclass
class ConnectorConfig:
    connector_type: str = "TAB_SLOT"
    width: float = 5.0
    depth: float = 5.0
    height: float = 5.0
    clearance: float = 0.05
    count: int = -1
    margin: float = 2.0
    seed_face: str = "A"

    taper_angle_deg: float = 20.0
    fillet_radius: float = 0.5
    segments: int = 32
    chamfer_radius: float = 0.0

    _VALID_TYPES = ("TAB_SLOT", "DOVETAIL", "PEG_HOLE")

    def __post_init__(self):
        ct = self.connector_type.upper()
        if ct not in self._VALID_TYPES:
            raise ValueError(f"connector_type must be one of {self._VALID_TYPES}, got '{self.connector_type}'")
        self.connector_type = ct
        if self.width < 0: raise ValueError(f"width must be ≥ 0, got {self.width}")
        if self.depth < 0: raise ValueError(f"depth must be ≥ 0, got {self.depth}")
        if self.height < 0: raise ValueError(f"height must be ≥ 0, got {self.height}")
        if self.margin < 0: raise ValueError(f"margin must be ≥ 0, got {self.margin}")
        if self.seed_face.upper() not in ("A", "B"):
            raise ValueError(f"seed_face must be 'A' or 'B', got '{self.seed_face}'")
        self.seed_face = self.seed_face.upper()


@dataclass
class _Placement:
    position: Vector
    tangent: Vector
    normal: Vector


def _build_local_plane_basis(plane_no: Vector):
    n = plane_no.normalized()
    if abs(n.dot(Vector((1.0, 0.0, 0.0)))) < 0.999:
        arbitrary = Vector((1.0, 0.0, 0.0))
    else:
        arbitrary = Vector((0.0, 1.0, 0.0))
    u = (arbitrary - arbitrary.project(n)).normalized()
    v = n.cross(u).normalized()
    return u, v


def _project_2d_to_3d(uv: Vector, plane_co: Vector, u: Vector, v: Vector) -> Vector:
    return plane_co + uv.x * u + uv.y * v


def _build_connector_pair(config: ConnectorConfig):
    ct = config.connector_type
    gap = max(config.width * config.clearance, 0.03)
    if ct == "TAB_SLOT":
        male = build_tab_male(width=config.width, depth=config.depth, height=config.height, fillet_radius=config.fillet_radius)
        female = build_tab_female(width=config.width, depth=config.depth, height=config.height, clearance=gap)
    elif ct == "DOVETAIL":
        male = build_dovetail_male(width=config.width, depth=config.depth, height=config.height, taper_angle_deg=config.taper_angle_deg)
        female = build_dovetail_female(width=config.width, depth=config.depth, height=config.height, taper_angle_deg=config.taper_angle_deg, clearance=gap)
    else:
        male = build_peg_male(radius=config.width / 2.0, depth=config.height, segments=config.segments, chamfer_radius=config.chamfer_radius)
        female = build_peg_female(radius=config.width / 2.0, depth=config.height, segments=config.segments, clearance=gap)
    return male, female


def _compute_perimeter_length(bounds_2d: list[Vector]) -> float:
    n = len(bounds_2d)
    if n < 2: return 0.0
    total = 0.0
    for i in range(n):
        total += (bounds_2d[i] - bounds_2d[(i + 1) % n]).length
    return total


def _determine_count(bounds: dict, config: ConnectorConfig) -> int:
    if config.connector_type == 'DOVETAIL': return 1
    if config.count > 0: return config.count
    area = bounds.get("area", 0.0)
    if area <= 0: return 1
    return max(1, int(area / 50.0))


def _auto_size(area: float, config: ConnectorConfig, thickness: float = 0) -> ConnectorConfig:
    char_len = math.sqrt(max(area, 1.0))
    auto_w = max(char_len * 0.15, 0.5)
    auto_h = max(char_len * 0.15, 0.5)
    if thickness > 0:
        raw = thickness * 0.06
        auto_h = max(min(raw, 4.0), 1.0)
        auto_w = max(min(raw, 4.0), 1.0)
    if config.connector_type == 'DOVETAIL':
        return config
    return ConnectorConfig(
        connector_type=config.connector_type,
        width=config.width if config.width > 0 else auto_w,
        depth=config.depth if config.depth > 0 else auto_w,
        height=config.height if config.height > 0 else auto_h,
        clearance=config.clearance, count=config.count,
        margin=config.margin, seed_face=config.seed_face,
    )


def _distribute_perimeter(bounds: dict, plane_co: Vector, plane_no: Vector, outward_normal: Vector, config: ConnectorConfig, count: int) -> list[_Placement]:
    bounds_2d = bounds["bounds_2d"]
    n = len(bounds_2d)
    if n < 3 or count == 0: return []

    edge_lengths = [(bounds_2d[i] - bounds_2d[(i + 1) % n]).length for i in range(n)]
    total_length = sum(edge_lengths)
    if total_length < 1e-6: return []

    cumulative = [0.0]
    for length in edge_lengths:
        cumulative.append(cumulative[-1] + length)

    u, v = _build_local_plane_basis(plane_no)
    center_2d = Vector((sum(p.x for p in bounds_2d) / n, sum(p.y for p in bounds_2d) / n))
    margin = config.margin
    step = total_length / count
    placements = []

    for i in range(count):
        t = (i + 0.5) * step
        edge_idx = 0
        for j in range(1, len(cumulative)):
            if cumulative[j] >= t: edge_idx = j - 1; break
        local_t = max(0.0, min(1.0, (t - cumulative[edge_idx]) / max(edge_lengths[edge_idx], 1e-6)))
        a_2d, b_2d = bounds_2d[edge_idx], bounds_2d[(edge_idx + 1) % n]
        edge_point_2d = a_2d.lerp(b_2d, local_t)

        inward_2d = center_2d - edge_point_2d
        if inward_2d.length_squared < 1e-12:
            edge_dir = (b_2d - a_2d).normalized()
            inward_2d = Vector((-edge_dir.y, edge_dir.x))
        inward_2d.normalize()

        edge_3d = _project_2d_to_3d(edge_point_2d, plane_co, u, v)
        position = edge_3d + (inward_2d.x * u + inward_2d.y * v) * margin
        tangent_2d = (b_2d - a_2d).normalized()
        tangent = (tangent_2d.x * u + tangent_2d.y * v).normalized()
        placements.append(_Placement(position=position, tangent=tangent, normal=outward_normal))

    return placements


def _distribute_grid(bounds: dict, plane_co: Vector, plane_no: Vector, outward_normal: Vector, config: ConnectorConfig, count: int) -> list[_Placement]:
    bounds_2d = bounds["bounds_2d"]
    if not bounds_2d or count == 0: return []
    margin = config.margin
    xs, ys = [p.x for p in bounds_2d], [p.y for p in bounds_2d]
    min_x, max_x = min(xs) + margin, max(xs) - margin
    min_y, max_y = min(ys) + margin, max(ys) - margin
    span_x, span_y = max_x - min_x, max_y - min_y
    if span_x <= 0.0 or span_y <= 0.0: return []

    cols = max(1, int(round(math.sqrt(count * span_x / max(span_y, 1e-6)))))
    rows = max(1, (count + cols - 1) // cols)
    u, v = _build_local_plane_basis(plane_no)
    cell_w, cell_h = span_x / cols, span_y / rows
    tangent = u.normalized()
    placements = []
    for row in range(rows):
        for col in range(cols):
            if len(placements) >= count: return placements
            uv_coord = Vector((min_x + (col + 0.5) * cell_w, min_y + (row + 0.5) * cell_h))
            position = _project_2d_to_3d(uv_coord, plane_co, u, v)
            placements.append(_Placement(position=position, tangent=tangent, normal=outward_normal))
    return placements


def _distribute_center(bounds: dict, plane_co: Vector, plane_no: Vector, outward_normal: Vector, config: ConnectorConfig, count: int) -> list[_Placement]:
    center = bounds.get("center", plane_co)
    area = bounds.get("area", 1.0)
    u, v = _build_local_plane_basis(plane_no)
    bounds_2d = bounds.get("bounds_2d", [])
    if count <= 0: return []

    if config.connector_type == 'DOVETAIL':
        if len(bounds_2d) >= 3:
            xs, ys = [p.x for p in bounds_2d], [p.y for p in bounds_2d]
            span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
            if span_x >= span_y:
                tangent, exact_span, perp_span = u.normalized(), span_x, span_y
            else:
                tangent, exact_span, perp_span = v.normalized(), span_y, span_x
        else:
            tangent = u.normalized()
            exact_span = math.sqrt(area) * 2.0
            perp_span = math.sqrt(area)
        config.depth = exact_span * 0.96
        config.width = min(config.width if config.width > 0 else perp_span * 0.20, perp_span * 0.35)
        config.height = min(config.height if config.height > 0 else perp_span * 0.10, perp_span * 0.15)
        return [_Placement(position=center, tangent=tangent, normal=outward_normal)]

    char_len = math.sqrt(area)
    radius = char_len * 0.3
    tangent = u.normalized()
    placements = []
    if count == 1:
        placements.append(_Placement(position=center, tangent=tangent, normal=outward_normal))
    else:
        for i in range(count):
            angle = (2 * math.pi * i) / count
            offset_2d = Vector((math.cos(angle) * radius, math.sin(angle) * radius))
            pos_3d = center + u * offset_2d.x + v * offset_2d.y
            placements.append(_Placement(position=pos_3d, tangent=tangent, normal=outward_normal))
    return placements


def _placement_transform(connector_bm: bmesh.types.BMesh, placement: _Placement, align_normal: Vector, is_peg: bool, peg_depth: float) -> bpy.types.Object:
    bm = connector_bm.copy()
    z_axis = Vector((0.0, 0.0, 1.0))
    z_rot = z_axis.rotation_difference(align_normal).to_matrix().to_4x4()
    x_axis = Vector((1.0, 0.0, 0.0))
    rotated_x = z_rot @ x_axis
    tangent_proj = placement.tangent - placement.tangent.project(align_normal)
    if tangent_proj.length_squared > 1e-10:
        target_x = tangent_proj.normalized()
    else:
        target_x = rotated_x.normalized()
    x_rot = rotated_x.normalized().rotation_difference(target_x).to_matrix().to_4x4()
    rot = x_rot @ z_rot

    if is_peg:
        offset = Matrix.Translation(Vector((0.0, 0.0, -peg_depth * 0.5)))
    else:
        offset = Matrix.Identity(4)
    translate = Matrix.Translation(placement.position - placement.normal * 0.005)
    transform_bmesh(bm, translate @ rot @ offset)

    name = _PC_PREFIX
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = True
    obj.display_type = 'WIRE'
    return obj


def _add_connector_boolean(target_obj: bpy.types.Object, connector_bm: bmesh.types.BMesh, placement: _Placement, operation: str, config: ConnectorConfig) -> None:
    align_normal = placement.normal
    is_peg = config.connector_type == 'PEG_HOLE'
    bm = connector_bm.copy()
    if is_peg:
        center = sum((v.co for v in bm.verts), Vector((0, 0, 0))) / max(len(bm.verts), 1)
        for v in bm.verts:
            v.co.z -= center.z
        align_normal = -align_normal
    if operation == 'DIFFERENCE' and config.connector_type == 'DOVETAIL':
        center = sum((v.co for v in bm.verts), Vector((0, 0, 0))) / max(len(bm.verts), 1)
        for v in bm.verts:
            v.co = center + (v.co - center) * 1.08
    is_peg = config.connector_type == 'PEG_HOLE'
    z_axis = Vector((0.0, 0.0, 1.0))
    z_rot = z_axis.rotation_difference(align_normal).to_matrix().to_4x4()
    x_axis = Vector((1.0, 0.0, 0.0))
    rotated_x = z_rot @ x_axis
    tangent_proj = placement.tangent - placement.tangent.project(align_normal)
    target_x = tangent_proj.normalized() if tangent_proj.length_squared > 1e-10 else rotated_x.normalized()
    x_rot = rotated_x.normalized().rotation_difference(target_x).to_matrix().to_4x4()
    rot = x_rot @ z_rot
    peg_offset = Matrix.Translation(Vector((0, 0, -config.height * 0.5))) if is_peg else Matrix.Identity(4)
    inset = max(config.height * 0.02, 0.05)
    translate = Matrix.Translation(placement.position - placement.normal * inset)
    transform_bmesh(bm, translate @ rot @ peg_offset)

    mesh = bpy.data.meshes.new(_PC_PREFIX)
    bm.to_mesh(mesh)
    bm.free()
    cutter = bpy.data.objects.new(_PC_PREFIX, mesh)
    bpy.context.scene.collection.objects.link(cutter)
    cutter.hide_render = True
    mod = target_obj.modifiers.new(name=_PC_PREFIX, type='BOOLEAN')
    mod.object = cutter
    mod.operation = operation
    mod.solver = 'EXACT'
    if hasattr(mod, 'use_self'):
        mod.use_self = True


def _cleanup_temp_objects(target_obj: bpy.types.Object, prefix: str = _PC_PREFIX) -> None:
    to_remove = []
    for mod in target_obj.modifiers:
        if mod.type == "BOOLEAN" and mod.object is not None and mod.object.name.startswith(prefix):
            to_remove.append(mod.object)
    if not to_remove:
        return
    for obj in to_remove:
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
    for obj in to_remove:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def generate_connectors(half_a: bpy.types.Object, half_b: bpy.types.Object, cut_plane_co: Vector, cut_plane_no: Vector, config: ConnectorConfig):
    for half in (half_a, half_b):
        if half.type != "MESH":
            raise ValueError(f"generate_connectors: '{half.name}' is not a MESH object (type={half.type})")

    plane_no = cut_plane_no.normalized()
    cut_surfaces = extract_cut_faces(half_a, half_b, cut_plane_co, plane_no)
    seed_key = config.seed_face
    other_key = "B" if seed_key == "A" else "A"
    seed_surface = cut_surfaces[seed_key]

    if not seed_surface["faces"]:
        logger.warning("generate_connectors: seed face '%s' has no cut faces", seed_key)
        _free_cut_bmeshes(cut_surfaces)
        return half_a, half_b
    if seed_surface["orientation"] == 0:
        logger.warning("generate_connectors: seed face '%s' has orientation=0", seed_key)
        _free_cut_bmeshes(cut_surfaces)
        return half_a, half_b

    seed_bounds = get_cut_surface_bounds(seed_surface["bm"], plane_co=cut_plane_co, plane_no=plane_no)
    seed_half = half_a if seed_key == 'A' else half_b
    seed_half.data.update()
    mat_inv = seed_half.matrix_world.inverted()
    lc = mat_inv @ cut_plane_co
    ln = (mat_inv.to_3x3() @ plane_no).normalized()
    dists = [ln.dot(Vector(c) - lc) for c in seed_half.bound_box]
    thickness = max(abs(d) for d in dists) if dists else 1.0
    object_thickness = thickness * 0.45

    outward_normal = plane_no * seed_surface["orientation"]
    config = _auto_size(seed_bounds["area"], config, object_thickness)
    count = _determine_count(seed_bounds, config)
    plane_co = seed_bounds.get("center", cut_plane_co)

    placements = _distribute_center(seed_bounds, plane_co, plane_no, outward_normal, config, count)
    if not placements:
        logger.warning("generate_connectors: no valid placement positions")
        _free_cut_bmeshes(cut_surfaces)
        return half_a, half_b

    seed_obj = duplicate_object(half_a if seed_key == "A" else half_b)
    other_obj = duplicate_object(half_b if seed_key == "A" else half_a)
    bpy.context.scene.collection.objects.link(seed_obj)
    bpy.context.scene.collection.objects.link(other_obj)

    try:
        for placement in placements:
            male_bm, female_bm = _build_connector_pair(config)
            _add_connector_boolean(seed_obj, male_bm, placement, "UNION", config)
            _add_connector_boolean(other_obj, female_bm, placement, "DIFFERENCE", config)
            male_bm.free()
            female_bm.free()

        apply_all_modifiers(seed_obj)
        apply_all_modifiers(other_obj)

        for obj in list(bpy.data.objects):
            if obj.name.startswith(_PC_PREFIX):
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if mesh and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

        move_to_collection(seed_obj, _CONNECTOR_RESULTS)
        move_to_collection(other_obj, _CONNECTOR_RESULTS)

    except Exception:
        _safe_delete(seed_obj)
        _safe_delete(other_obj)
        raise
    finally:
        _free_cut_bmeshes(cut_surfaces)

    if seed_key == "A":
        return seed_obj, other_obj
    else:
        return other_obj, seed_obj


def _free_cut_bmeshes(cut_surfaces: dict) -> None:
    for key in ("A", "B"):
        entry = cut_surfaces.get(key)
        if entry and "bm" in entry:
            bm = entry["bm"]
            if bm is not None and bm.is_valid:
                bm.free()


def _safe_delete(obj: Optional[bpy.types.Object]) -> None:
    if obj is None: return
    try:
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    except Exception:
        pass


__all__ = ["ConnectorConfig", "generate_connectors"]
