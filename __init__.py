bl_info = {
    "name": "Automatic Model Similarity Checker",
    "author": "DeynegoDina",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Auto Model Check",
    "description": "Automatically extracts comparison criteria from a reference Blender model and checks a student model",
    "category": "3D View",
}

import bpy
from .properties import CLASSES as PROP_CLASSES
from .operators import CLASSES as OP_CLASSES
from .panels import CLASSES as PANEL_CLASSES

CLASSES = PROP_CLASSES + OP_CLASSES + PANEL_CLASSES

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    from .properties import AutoCheckSettings
    bpy.types.Scene.auto_check = bpy.props.PointerProperty(type=AutoCheckSettings)

def unregister():
    if hasattr(bpy.types.Scene, "auto_check"):
        del bpy.types.Scene.auto_check
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)