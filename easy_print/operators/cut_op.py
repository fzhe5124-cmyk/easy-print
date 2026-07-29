import bpy
import bpy_extras.view3d_utils as view3d_utils
from mathutils import Vector
from ..core.cutter import cut_object, cut_object_with_inset

_active_op = None
_draw_h = None


def _draw_line():
    op = _active_op
    if op is None or op._scr_start is None:
        return
    import gpu
    from gpu_extras.batch import batch_for_shader
    sx, sy = op._scr_start
    ex, ey = op._scr_current
    r = bpy.context.region
    if r is None: return
    rv = bpy.context.region_data
    if rv is None: return
    p0 = view3d_utils.region_2d_to_location_3d(r, rv, (sx, sy), Vector((0, 0, 0)))
    p1 = view3d_utils.region_2d_to_location_3d(r, rv, (ex, ey), Vector((0, 0, 0)))
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {'pos': [p0, p1]})
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.5)
    shader.bind()
    shader.uniform_float('color', (0.15, 1.0, 0.3, 0.9))
    batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


def _mouse_ray(context, event):
    r, v = context.region, context.region_data
    c = (event.mouse_region_x, event.mouse_region_y)
    return (view3d_utils.region_2d_to_origin_3d(r, v, c),
            view3d_utils.region_2d_to_vector_3d(r, v, c))


def _mouse_ray_from_screen(context, sx, sy):
    r, v = context.region, context.region_data
    return (view3d_utils.region_2d_to_origin_3d(r, v, (sx, sy)),
            view3d_utils.region_2d_to_vector_3d(r, v, (sx, sy)))


def _raycast_obj(obj, origin, direction):
    mi = obj.matrix_world.inverted()
    hit, loc, _, _ = obj.ray_cast(mi @ origin, (mi.to_3x3() @ direction).normalized())
    return (True, obj.matrix_world @ loc) if hit else (False, None)


class PRINT_OT_cut(bpy.types.Operator):
    bl_idname = "print_connector.cut"
    bl_label = "Cut Model"
    bl_description = "Draw line across model. Release=set plane. Click=cut."
    bl_options = {"REGISTER", "UNDO"}

    _state = 'IDLE'
    _target = None
    _scr_start = None
    _scr_current = None
    _plane_co = None
    _plane_no = None
    _prev_view_perspective = None

    @classmethod
    def poll(cls, context):
        return True

    def _set_ortho(self, context, enable):
        rv3d = context.region_data
        if rv3d is None: return
        if enable:
            self._prev_view_perspective = rv3d.view_perspective
            rv3d.view_perspective = 'ORTHO'
        else:
            if self._prev_view_perspective is not None:
                rv3d.view_perspective = self._prev_view_perspective
                self._prev_view_perspective = None

    def invoke(self, context, event):
        global _active_op, _draw_h
        obj = context.active_object
        if obj is None or obj.type != "MESH":
            for o in context.selected_objects:
                if o.type == 'MESH':
                    obj = o; context.view_layer.objects.active = obj; break
        if obj is None or obj.type != "MESH":
            self.report({"ERROR"}, "Select a mesh object first.")
            return {"CANCELLED"}
        self._target = obj
        self._state = 'DRAWING'
        self._set_ortho(context, True)
        _active_op = self
        if _draw_h is None:
            _draw_h = bpy.types.SpaceView3D.draw_handler_add(_draw_line, (), "WINDOW", "POST_VIEW")
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Draw line. Release to preview. Click to cut. Esc=cancel")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in {"RIGHTMOUSE", "ESC"}:
            if self._state == 'PREVIEW':
                self._state = 'DRAWING'; self._plane_co = None
                return {"RUNNING_MODAL"}
            global _active_op, _draw_h
            _active_op = None
            if _draw_h is not None:
                bpy.types.SpaceView3D.draw_handler_remove(_draw_h, "WINDOW")
                _draw_h = None
            self._set_ortho(context, False)
            self.report({"INFO"}, "Cut cancelled.")
            return {"CANCELLED"}

        if self._state == 'DRAWING':
            self._scr_current = (event.mouse_region_x, event.mouse_region_y)
            context.area.tag_redraw()
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                self._scr_start = (event.mouse_region_x, event.mouse_region_y)
                return {"RUNNING_MODAL"}
            if event.type == "LEFTMOUSE" and event.value == "RELEASE":
                if self._scr_start is None: return {"RUNNING_MODAL"}
                sx, sy = self._scr_start
                ex, ey = event.mouse_region_x, event.mouse_region_y
                ro_s, rd_s = _mouse_ray_from_screen(context, sx, sy)
                ro_e, rd_e = _mouse_ray_from_screen(context, ex, ey)
                hit_s, pt_s = _raycast_obj(self._target, ro_s, rd_s)
                hit_e, pt_e = _raycast_obj(self._target, ro_e, rd_e)
                if not hit_s: pt_s = ro_s + rd_s * 10
                if not hit_e: pt_e = ro_e + rd_e * 10

                rv3d = context.region_data
                vd = (rv3d.view_matrix.to_3x3().inverted() @ Vector((0, 0, -1))).normalized()
                ld = pt_e - pt_s
                if ld.length < 0.01:
                    self._plane_co = pt_s; self._plane_no = vd
                else:
                    ld.normalize(); pn = ld.cross(vd)
                    if pn.length < 0.001: pn = Vector((0, 0, 1))
                    self._plane_no = pn.normalized()
                    self._plane_co = (pt_s + pt_e) * 0.5

                self._state = 'PREVIEW'
                self.report({"INFO"}, "Click to cut. Esc=redraw.")
                return {"RUNNING_MODAL"}

        elif self._state == 'PREVIEW':
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                return self.execute(context)
            if event.type in {"ONE", "TWO", "THREE"} and event.value == "PRESS":
                a = {"ONE": (1, 0, 0), "TWO": (0, 1, 0), "THREE": (0, 0, 1)}
                self._plane_no = Vector(a[event.type])
                return {"RUNNING_MODAL"}
            if event.type == "WHEELUPMOUSE":
                self._plane_co += self._plane_no * 0.5
                return {"RUNNING_MODAL"}
            if event.type == "WHEELDOWNMOUSE":
                self._plane_co -= self._plane_no * 0.5
                return {"RUNNING_MODAL"}
            if event.type == "MOUSEMOVE":
                ro, rd = _mouse_ray(context, event)
                hit, hl = _raycast_obj(self._target, ro, rd)
                if hit:
                    d = (hl - self._plane_co).dot(self._plane_no)
                    self._plane_co += self._plane_no * d

        return {"PASS_THROUGH"}

    def execute(self, context):
        global _active_op, _draw_h
        _active_op = None
        if _draw_h is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_h, "WINDOW")
            _draw_h = None
        self._set_ortho(context, False)

        obj = self._target
        plane_no = self._plane_no.normalized()
        s = context.scene.print_connector
        s.plane_location = self._plane_co; s.custom_normal = plane_no; s.plane_normal = 'CUSTOM'

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.select_all(action="DESELECT")

        inset = s.inset_thickness
        if inset > 0.0:
            ha, hb, ins = cut_object_with_inset(obj, self._plane_co, plane_no, inset)
            for r in (ha, hb, ins):
                if r: r.select_set(True)
            context.view_layer.objects.active = ha if ha else hb
        else:
            ha, hb = cut_object(obj, self._plane_co, plane_no)
            for r in (ha, hb):
                if r: r.select_set(True)
            context.view_layer.objects.active = ha if ha else hb

        if ha is None and hb is None:
            self.report({"ERROR"}, "Cut failed."); return {"CANCELLED"}
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        names = [r.name for r in (ha, hb) if r]
        self.report({"INFO"}, f"Cut -> {', '.join(names)}")
        return {"FINISHED"}
