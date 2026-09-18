import bpy
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty

class AutoCheckSettings(bpy.types.PropertyGroup):
    reference_file: StringProperty(name="Reference .blend", subtype='FILE_PATH')
    student_file: StringProperty(name="Student .blend", subtype='FILE_PATH')
    assignment_file: StringProperty(name="Generated criteria", subtype='FILE_PATH')
    dimension_tolerance: FloatProperty(name="Dimension tolerance %", default=5.0, min=0, max=100)
    position_tolerance: FloatProperty(name="Position tolerance %", default=5.0, min=0, max=100)
    geometry_tolerance: FloatProperty(name="Geometry tolerance %", default=12.0, min=0, max=100)
    component_tolerance: FloatProperty(name="Component count tolerance %", default=0.0, min=0, max=100)
    min_component_volume: FloatProperty(name="Min component volume", default=0.000001, min=0)
    use_loose_parts: BoolProperty(name="Detect loose mesh parts", default=True)
    normalize_orientation: BoolProperty(name="Normalize model orientation", default=False)
    result_text: StringProperty(default="")
    reference_loaded: BoolProperty(default=False)
    result_ready: BoolProperty(default=False)

CLASSES = [AutoCheckSettings]
