import bpy
from mathutils import Vector
from ..core.connectors import ConnectorConfig, generate_connectors

_PLANE_NORMAL_MAP = {
    'POS_X': (1, 0, 0), 'NEG_X': (-1, 0, 0),
    'POS_Y': (0, 1, 0), 'NEG_Y': (0, -1, 0),
    'POS_Z': (0, 0, 1), 'NEG_Z': (0, 0, -1),
}


def _resolve_plane_normal(s):
    c = getattr(s, 'custom_normal', None)
    if c and Vector(c).length > 0.001: return Vector(c).normalized()
    return Vector(_PLANE_NORMAL_MAP.get(s.plane_normal, (0, 0, 1)))


def _resolve_plane_co(s):
    return Vector(getattr(s, 'plane_location', (0, 0, 0)))


class PRINT_OT_generate_connectors(bpy.types.Operator):
    bl_idname = "print_connector.generate_connectors"
    bl_label = "Generate Connectors"
    bl_description = "Generate connectors, then scroll to adjust depth/size."
    bl_options = {"REGISTER", "UNDO"}

    _half_a = None
    _half_b = None
    _plane_co = None
    _plane_no = None
    _config = None
    _result_a = None
    _result_b = None

    @classmethod
    def poll(cls, context): return True

    def invoke(self, context, event):
        s = context.scene.print_connector
        sel = [o for o in context.selected_objects if o.type == "MESH"]
        if len(sel) != 2:
            self.report({"ERROR"}, "Select exactly 2 mesh objects.")
            return {"CANCELLED"}
        sel.sort(key=lambda o: o.name)
        self._half_a, self._half_b = sel[0], sel[1]
        self._plane_no = _resolve_plane_normal(s)
        self._plane_co = _resolve_plane_co(s)
        self._config = ConnectorConfig(
            connector_type=s.connector_type, width=s.width, depth=0,
            height=s.height, clearance=s.clearance,
            count=s.count, margin=s.margin, seed_face='A')
        self._prev_xray = context.space_data.shading.show_xray
        context.space_data.shading.show_xray = True
        self._regenerate()
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Scroll=height  Shift+scroll=size  Click=ok  Esc=cancel")
        return {"RUNNING_MODAL"}

    def _regenerate(self):
        if self._result_a and self._result_a.name in bpy.data.objects \
           and self._result_a != self._half_a and self._result_a != self._half_b:
            bpy.data.objects.remove(self._result_a, do_unlink=True)
        if self._result_b and self._result_b.name in bpy.data.objects \
           and self._result_b != self._half_a and self._result_b != self._half_b:
            bpy.data.objects.remove(self._result_b, do_unlink=True)
        self._result_a, self._result_b = generate_connectors(
            self._half_a, self._half_b, self._plane_co, self._plane_no, self._config)

    def modal(self, context, event):
        if event.type in {"ESC", "RIGHTMOUSE"}:
            context.space_data.shading.show_xray = self._prev_xray
            if self._result_a and self._result_a.name in bpy.data.objects:
                bpy.data.objects.remove(self._result_a, do_unlink=True)
            if self._result_b and self._result_b.name in bpy.data.objects:
                bpy.data.objects.remove(self._result_b, do_unlink=True)
            self.report({"INFO"}, "Cancelled."); return {"CANCELLED"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            context.space_data.shading.show_xray = self._prev_xray
            bpy.ops.object.select_all(action="DESELECT")
            for o in (self._half_a, self._half_b):
                if o and o.name in bpy.data.objects:
                    bpy.data.objects.remove(o, do_unlink=True)
            if self._result_a: self._result_a.select_set(True)
            if self._result_b: self._result_b.select_set(True)
            context.view_layer.objects.active = self._result_a
            self.report({"INFO"}, f"w={self._config.width:.1f} h={self._config.height:.1f}")
            return {"FINISHED"}

        changed = False
        if event.type == "WHEELUPMOUSE":
            if event.shift:
                self._config.width = max(0.03, self._config.width + 0.03)
                self._config.depth = self._config.width
            else:
                self._config.height = max(0.03, self._config.height + 0.03)
            changed = True
        elif event.type == "WHEELDOWNMOUSE":
            if event.shift:
                self._config.width = max(0.03, self._config.width - 0.03)
                self._config.depth = self._config.width
            else:
                self._config.height = max(0.03, self._config.height - 0.03)
            changed = True

        if changed:
            self._regenerate()
            self.report({"INFO"}, f"size={self._config.width:.1f} depth={self._config.height:.1f}")

        return {"RUNNING_MODAL"}
