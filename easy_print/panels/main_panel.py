import bpy


class PRINT_PT_main_panel(bpy.types.Panel):
    bl_idname = "PRINT_PT_main_panel"
    bl_label = "Easy-Print"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Easy-Print"

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'print_connector')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        s = context.scene.print_connector

        from .. import _icons
        if _icons and "logo" in _icons:
            row = layout.row()
            row.alignment = 'CENTER'
            row.template_icon(icon_value=_icons["logo"].icon_id, scale=6)

        box = layout.box()
        col = box.column(align=True)
        col.label(text="CUT", icon='MOD_BOOLEAN')
        col.operator("print_connector.cut", text="Cut Model", icon='MOD_BOOLEAN')
        col.separator()
        col.label(text="Draw line → release → click", icon='HAND')

        layout.separator()

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="CONNECTOR", icon='MOD_ARRAY')
        row.prop(s, "connector_type", text="")
        col.separator()
        col.prop(s, "width")
        col.prop(s, "height")
        col.prop(s, "clearance")
        col.prop(s, "count")
        col.separator()
        col.operator("print_connector.generate_connectors", text="Generate Connectors", icon='ADD')
        col.separator()

        hint_box = col.box()
        hint_col = hint_box.column(align=True)
        hint_col.scale_y = 0.85
        hint_col.label(text="After Generate:", icon='INFO')
        hint_col.label(text="  Scroll      —  Adjust Height", icon='EVENT_W')
        hint_col.label(text="  Shift+Scroll —  Adjust Size", icon='EVENT_SHIFT')
        hint_col.label(text="  LMB Click   —  Confirm", icon='MOUSE_LMB')
        hint_col.label(text="  RMB / Esc   —  Cancel", icon='EVENT_ESC')


class PRINT_PT_about(bpy.types.Panel):
    bl_idname = "PRINT_PT_about"
    bl_label = "ABOUT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Easy-Print"
    bl_parent_id = "PRINT_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, 'print_connector')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Easy-Print v0.1.0")
        col.label(text="by Double_G")
        col.label(text="Blender 4.2 - 5.2")
        col.separator()
        box = col.box()
        box_col = box.column(align=True)
        box_col.scale_y = 0.85
        box_col.label(text="This is a free & open-source add-on.", icon='FUND')
        box_col.label(text="Please download from official sources only.")
        box_col.separator()
        box_col.label(text="本插件为免费开源插件，请通过官方渠道下载。", icon='FUND')
