
import bpy, os

from pathlib import Path

from .core.assignment import build_assignment, save, load
from .core.check import check
from .visual import highlight, clear
from .report import export


class OT_create_reference(bpy.types.Operator):

    bl_idname = "auto_check.create_reference"
    bl_label = "Создать критерии по текущей модели"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, c, e):
        self.filepath = str(
            Path(bpy.path.abspath("//")) / "auto_model_criteria.json"
        )
        c.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, c):
        try:
            dg = bpy.context.evaluated_depsgraph_get()

            data = build_assignment(
                bpy.context.scene.objects,
                dg,
                c.scene.auto_check
            )

            save(data, self.filepath)

            c.scene.auto_check.assignment_file = self.filepath
            c.scene.auto_check.reference_loaded = True
            c.scene["auto_assignment"] = data

            self.report(
                {'INFO'},
                f"Критерии автоматически созданы: "
                f"{len(data['reference']['objects'])} объектов"
            )

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class OT_load_reference(bpy.types.Operator):

    bl_idname = "auto_check.load_reference"
    bl_label = "Загрузить эталонную модель .blend"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, c, e):
        c.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, c):
        try:
            # Загружаем эталонную модель во временную сцену,
            # анализируем её и возвращаемся в текущую сцену.

            current = bpy.context.window.scene

            with bpy.data.libraries.load(
                self.filepath,
                link=False
            ) as (src, dst):

                dst.objects = list(src.objects)

            temp = bpy.data.scenes.new("AUTO_REFERENCE_TEMP")

            for o in dst.objects:
                if o:
                    temp.collection.objects.link(o)

            bpy.context.window.scene = temp

            dg = bpy.context.evaluated_depsgraph_get()

            data = build_assignment(
                temp.objects,
                dg,
                c.scene.auto_check
            )

            out = str(
                Path(self.filepath).with_suffix(".criteria.json")
            )

            save(data, out)

            bpy.context.window.scene = current

            bpy.data.scenes.remove(temp)

            for o in dst.objects:
                if o and o.name in bpy.data.objects:
                    bpy.data.objects.remove(
                        o,
                        do_unlink=True
                    )

            c.scene.auto_check.reference_file = self.filepath
            c.scene.auto_check.assignment_file = out
            c.scene["auto_assignment"] = data
            c.scene.auto_check.reference_loaded = True

            self.report(
                {'INFO'},
                f"Эталонная модель автоматически проанализирована: "
                f"{len(data['reference']['objects'])} объектов"
            )

            return {'FINISHED'}

        except Exception as e:
            try:
                bpy.context.window.scene = current
            except:
                pass

            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class OT_import_criteria(bpy.types.Operator):

    bl_idname = "auto_check.import_criteria"
    bl_label = "Загрузить созданные критерии"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, c, e):
        self.filepath = c.scene.auto_check.assignment_file
        c.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, c):
        try:
            c.scene["auto_assignment"] = load(self.filepath)
            c.scene.auto_check.reference_loaded = True

            self.report(
                {'INFO'},
                "Критерии успешно загружены"
            )

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class OT_check(bpy.types.Operator):

    bl_idname = "auto_check.check"
    bl_label = "Проверить модель ученика"

    def execute(self, c):

        a = c.scene.get("auto_assignment")

        if not a:
            self.report(
                {'ERROR'},
                "Сначала загрузите или проанализируйте эталонную модель"
            )
            return {'CANCELLED'}

        try:
            r = check(
                bpy.context.selected_objects,
                a,
                c.scene.auto_check
            )

            c.scene["auto_result"] = r
            c.scene.auto_check.result_ready = True

            highlight(r)

            self.report(
                {'INFO'},
                f"Сходство моделей: {r['overall']:.1f}%"
            )

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class OT_export(bpy.types.Operator):

    bl_idname = "auto_check.export"
    bl_label = "Экспортировать отчёт"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, c, e):

        self.filepath = str(
            Path(bpy.path.abspath("//")) / "model_check_result.json"
        )

        c.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, c):

        r = c.scene.get("auto_result")

        if not r:
            self.report(
                {'ERROR'},
                "Сначала выполните проверку модели"
            )
            return {'CANCELLED'}

        export(r, self.filepath)

        self.report(
            {'INFO'},
            "Отчёты JSON и HTML успешно экспортированы"
        )

        return {'FINISHED'}


class OT_clear(bpy.types.Operator):

    bl_idname = "auto_check.clear"
    bl_label = "Очистить подсветку"

    def execute(self, c):
        clear()
        return {'FINISHED'}


CLASSES = [
    OT_create_reference,
    OT_load_reference,
    OT_import_criteria,
    OT_check,
    OT_export,
    OT_clear
]

