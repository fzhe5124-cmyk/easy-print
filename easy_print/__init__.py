bl_info = {
    "name": "Easy-Print",
    "author": "Double_G",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Easy-Print",
    "description": "Cut models and generate interlocking connectors for 3D printing",
    "category": "3D View",
}

import os
import bpy
from bpy.utils import previews
from .operators.cut_op import PRINT_OT_cut
from .operators.connector_op import PRINT_OT_generate_connectors
from .panels.main_panel import PRINT_PT_main_panel, PRINT_PT_about

_icons = None


class PrintConnectorSettings(bpy.types.PropertyGroup):
    plane_location: bpy.props.FloatVectorProperty(
        name="Location", subtype='TRANSLATION', default=(0.0, 0.0, 0.0),
        description="World-space origin of the cut plane",
    )
    plane_normal: bpy.props.EnumProperty(
        name="Normal",
        items=[
            ('POS_X', '+X', 'Cut perpendicular to +X axis'),
            ('NEG_X', '-X', 'Cut perpendicular to -X axis'),
            ('POS_Y', '+Y', 'Cut perpendicular to +Y axis'),
            ('NEG_Y', '-Y', 'Cut perpendicular to -Y axis'),
            ('POS_Z', '+Z', 'Cut perpendicular to +Z axis'),
            ('NEG_Z', '-Z', 'Cut perpendicular to -Z axis'),
            ('CUSTOM', 'Custom', 'Use custom normal (set via interactive cut)'),
        ],
        default='POS_Z',
    )
    custom_normal: bpy.props.FloatVectorProperty(
        name="Actual Normal", subtype='DIRECTION', default=(0.0, 0.0, 1.0),
    )
    inset_thickness: bpy.props.FloatProperty(
        name="Inset", subtype='DISTANCE', default=0.0, min=0.0, soft_max=1.0, precision=3,
    )
    connector_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('PEG_HOLE', 'Peg & Hole', 'Cylindrical peg and matching hole'),
            ('DOVETAIL', 'Dovetail', 'Sliding dovetail joint'),
            ('TAB_SLOT', 'Tab & Slot', 'Rectangular tab and slot'),
        ],
        default='TAB_SLOT',
    )
    width: bpy.props.FloatProperty(
        name="Size / 尺寸", subtype='DISTANCE', default=0.0, min=0.0, soft_max=20.0, precision=3,
    )
    height: bpy.props.FloatProperty(
        name="Height / 高度", subtype='DISTANCE', default=0.0, min=0.0, soft_max=20.0, precision=3,
    )
    clearance: bpy.props.FloatProperty(
        name="Clearance / 间隙", default=0.02, min=0.0, max=0.3, soft_max=0.15, precision=3,
    )
    count: bpy.props.IntProperty(
        name="Count / 数量", default=-1, min=-1, soft_max=20,
    )
    margin: bpy.props.FloatProperty(
        name="Margin", subtype='DISTANCE', default=2.0, min=0.0, soft_max=10.0, precision=3,
    )
    taper_angle_deg: bpy.props.FloatProperty(
        name="Taper Angle", default=20.0, min=5.0, max=60.0, precision=1,
    )


classes = [
    PRINT_OT_cut,
    PRINT_OT_generate_connectors,
    PRINT_PT_main_panel,
    PRINT_PT_about,
    PrintConnectorSettings,
]


def register():
    global _icons
    _icons = previews.new()
    icon_path = os.path.join(os.path.dirname(__file__), "icons", "logo.png")
    if os.path.exists(icon_path):
        _icons.load("logo", icon_path, 'IMAGE')

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.print_connector = bpy.props.PointerProperty(
        type=PrintConnectorSettings, name="Easy-Print Settings",
    )


def unregister():
    global _icons
    if _icons is not None:
        previews.remove(_icons)
        _icons = None

    try:
        del bpy.types.Scene.print_connector
    except (AttributeError, KeyError):
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
