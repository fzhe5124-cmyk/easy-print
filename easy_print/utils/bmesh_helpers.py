import bpy
import bmesh
from mathutils import Vector, Matrix


def get_bmesh(obj: bpy.types.Object, use_evaluated: bool = True) -> bmesh.types.BMesh:
    bm = bmesh.new()
    if use_evaluated:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        bm.from_mesh(eval_obj.data)
    else:
        bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def write_bmesh(obj: bpy.types.Object, bm: bmesh.types.BMesh):
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def transform_bmesh(bm: bmesh.types.BMesh, matrix: Matrix):
    bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts[:])


def move_to_collection(obj: bpy.types.Object, collection_name: str):
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)


def duplicate_object(obj: bpy.types.Object, name: str = "") -> bpy.types.Object:
    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    if name:
        new_obj.name = name
        new_obj.data.name = name
    new_obj.animation_data_clear()
    return new_obj


def apply_all_modifiers(obj: bpy.types.Object) -> bpy.types.Object:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    new_mesh = bpy.data.meshes.new_from_object(eval_obj)
    obj.data = new_mesh
    obj.modifiers.clear()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0001, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def plane_distance(point: Vector, plane_co: Vector, plane_no: Vector) -> float:
    return (point - plane_co).dot(plane_no)


def is_face_on_plane(face: bmesh.types.BMFace, plane_co: Vector, plane_no: Vector, distance_epsilon: float = 0.001, angle_epsilon: float = 0.001) -> bool:
    for vert in face.verts:
        if abs(plane_distance(vert.co, plane_co, plane_no)) > distance_epsilon:
            return False
    dot = abs(face.normal.dot(plane_no))
    if abs(dot - 1.0) > angle_epsilon:
        return False
    return True


def get_face_center(face: bmesh.types.BMFace) -> Vector:
    return sum((v.co for v in face.verts), Vector()) / len(face.verts)
