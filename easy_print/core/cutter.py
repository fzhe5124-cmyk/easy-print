import logging
import bmesh
import bpy
from mathutils import Vector
from ..utils.bmesh_helpers import duplicate_object, move_to_collection

logger = logging.getLogger(__name__)
CUT_RESULTS_COLLECTION = "Cut Results"


def _bisect_half(obj, plane_co, plane_no, keep_positive):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    mat_inv = obj.matrix_world.inverted()
    lc = mat_inv @ plane_co
    ln = (mat_inv.to_3x3() @ plane_no).normalized()

    bpy.ops.mesh.bisect(plane_co=lc, plane_no=ln, use_fill=True, clear_inner=False, clear_outer=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bad = [v for v in bm.verts
           if (keep_positive and (v.co - lc).dot(ln) < -0.0001)
           or (not keep_positive and (v.co - lc).dot(ln) > 0.0001)]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context='VERTS')

    flip = [f for f in bm.faces
            if abs((f.calc_center_median() - lc).dot(ln)) < 0.002
            and f.normal.dot(-ln if keep_positive else ln) < 0]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def cut_object(obj, cut_plane_co, cut_plane_no):
    if obj.type != "MESH": return None, None
    plane_no = cut_plane_no.normalized()
    half_a = duplicate_object(obj, obj.name + "_A")
    half_b = duplicate_object(obj, obj.name + "_B")
    bpy.context.scene.collection.objects.link(half_a)
    bpy.context.scene.collection.objects.link(half_b)
    _bisect_half(half_a, cut_plane_co, plane_no, keep_positive=False)
    _bisect_half(half_b, cut_plane_co, plane_no, keep_positive=True)
    move_to_collection(half_a, CUT_RESULTS_COLLECTION)
    move_to_collection(half_b, CUT_RESULTS_COLLECTION)
    return half_a, half_b


def cut_object_with_inset(obj, cut_plane_co, cut_plane_no, inset_thickness):
    if obj.type != "MESH": return None, None, None
    plane_no = cut_plane_no.normalized()
    h = inset_thickness / 2.0
    co_a = cut_plane_co - plane_no * h
    co_b = cut_plane_co + plane_no * h
    half_a = duplicate_object(obj, obj.name + "_A")
    half_b = duplicate_object(obj, obj.name + "_B")
    inset = duplicate_object(obj, obj.name + "_inset")
    for o in (half_a, half_b, inset):
        bpy.context.scene.collection.objects.link(o)
    _bisect_half(half_a, co_a, plane_no, keep_positive=False)
    _bisect_half(half_b, co_b, plane_no, keep_positive=True)
    _bisect_half(inset, co_a, plane_no, keep_positive=False)
    _bisect_half(inset, co_b, plane_no, keep_positive=True)
    move_to_collection(half_a, CUT_RESULTS_COLLECTION)
    move_to_collection(half_b, CUT_RESULTS_COLLECTION)
    move_to_collection(inset, CUT_RESULTS_COLLECTION)
    return half_a, half_b, inset
