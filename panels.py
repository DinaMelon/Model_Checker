import bpy


class PT_auto(bpy.types.Panel):
    bl_idname = "AUTO_CHECK_PT_main"
    bl_label = "Проверка 3D-модели"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Checker 3D Model"

    def draw(self, context):
        layout = self.layout

        settings = context.scene.auto_check
        assignment = context.scene.get("auto_assignment")
        result = context.scene.get("auto_result")

        # ---------------------------------------------------------
        # ЭТАЛОННАЯ МОДЕЛЬ
        # ---------------------------------------------------------

        box = layout.box()

        box.label(
            text="ЭТАЛОННАЯ МОДЕЛЬ",
            icon='OBJECT_DATA'
        )

        box.prop(
            settings,
            "reference_file"
        )

        box.operator(
            "auto_check.load_reference",
            text="Загрузить эталонную модель",
            icon='IMPORT'
        )

        box.operator(
            "auto_check.create_reference",
            text="Создать критерии по текущей модели",
            icon='FILE_TICK'
        )

        if assignment:
            box.label(
                text=(
                    "Критерии созданы автоматически: "
                    f"{len(assignment['reference']['objects'])} объектов"
                ),
                icon='CHECKMARK'
            )

            dimensions = assignment["reference"]["model"]["dimensions"]

            box.label(
                text=(
                    "Размер всей модели: "
                    f"{dimensions[0]:.3f} × "
                    f"{dimensions[1]:.3f} × "
                    f"{dimensions[2]:.3f}"
                )
            )

        # ---------------------------------------------------------
        # ПРОВЕРКА МОДЕЛИ УЧЕНИКА
        # ---------------------------------------------------------

        box = layout.box()

        box.label(
            text="ПРОВЕРКА МОДЕЛИ УЧЕНИКА",
            icon='VIEWZOOM'
        )

        box.label(
            text="Выберите объекты Mesh модели ученика."
        )

        box.label(
            text="Можно выбрать несколько объектов."
        )

        box.operator(
            "auto_check.check",
            text="Проверить модель ученика",
            icon='CHECKMARK'
        )


        # ---------------------------------------------------------
        # ДОПУСКИ
        # ---------------------------------------------------------

        box = layout.box()

        box.label(
            text="ДОПУСКИ ПРОВЕРКИ",
            icon='PREFERENCES'
        )

        box.prop(
            settings,
            "dimension_tolerance",
            text="Допуск размеров"
        )

        box.prop(
            settings,
            "geometry_tolerance",
            text="Допуск геометрии"
        )

        # ---------------------------------------------------------
        # РЕЗУЛЬТАТ
        # ---------------------------------------------------------

        if result:
            box = layout.box()

            box.label(
                text="РЕЗУЛЬТАТ ПРОВЕРКИ",
                icon='INFO'
            )

            box.separator()

            box.label(
                text=f"ОБЩЕЕ СХОДСТВО: {result['overall']:.1f}%"
            )

            box.separator()

            box.label(
                text=f"Детали: {result['parts']:.1f}%"
            )

            box.label(
                text=f"Размеры: {result['dimensions']:.1f}%"
            )
            box.separator()

            box.label(
                text="СРАВНЕНИЕ РАЗМЕРОВ"
            )

            for detail in result["details"]:

                reference_dimensions = detail["reference_dimensions"]
                student_dimensions = detail["student_dimensions"]
                correction = detail["dimensions_correction"]

                box.label(
                    text=f"Объект: {detail['student']}"
                )

                box.label(
                    text=(
                        f"Эталон: "
                        f"{reference_dimensions[0]:.3f} × "
                        f"{reference_dimensions[1]:.3f} × "
                        f"{reference_dimensions[2]:.3f}"
                    )
                )

                box.label(
                    text=(
                        f"Модель: "
                        f"{student_dimensions[0]:.3f} × "
                        f"{student_dimensions[1]:.3f} × "
                        f"{student_dimensions[2]:.3f}"
                    )
                )

                box.label(
                    text=(
                        f"Изменить: "
                        f"X {correction[0]:+.3f}, "
                        f"Y {correction[1]:+.3f}, "
                        f"Z {correction[2]:+.3f}"
                    )
                )
            box.label(
                text=f"Геометрия: {result['geometry']:.1f}%"
            )

            box.separator()

            box.label(
                text=(
                    f"Отсутствующие объекты: "
                    f"{len(result['missing'])}"
                )
            )

            box.label(
                text=(
                    f"Лишние объекты: "
                    f"{len(result['extras'])}"
                )
            )

            # -----------------------------------------------------
            # СПИСОК ОТСУТСТВУЮЩИХ ОБЪЕКТОВ
            # -----------------------------------------------------

            if result["missing"]:
                box.separator()

                box.label(
                    text="Отсутствуют:",
                    icon='ERROR'
                )

                for name in result["missing"]:
                    box.label(
                        text=f"• {name}"
                    )

            # -----------------------------------------------------
            # СПИСОК ЛИШНИХ ОБЪЕКТОВ
            # -----------------------------------------------------

            if result["extras"]:
                box.separator()

                box.label(
                    text="Лишние:",
                    icon='QUESTION'
                )

                for name in result["extras"]:
                    box.label(
                        text=f"• {name}"
                    )

            box.separator()

            box.operator(
                "auto_check.export",
                text="Экспортировать результат",
                icon='EXPORT'
            )


class PT_info(bpy.types.Panel):
    bl_idname = "AUTO_CHECK_PT_info"
    bl_label = "Как работает проверка"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Auto Checker 3D Model"

    def draw(self, context):
        layout = self.layout

        instructions = [
            "1. Загрузите эталонную модель в формате .blend.",
            "2. Аддон автоматически проанализирует модель.",
            "3. Критерии сравнения будут созданы автоматически.",
            "4. Откройте файл .blend с моделью ученика.",
            "5. Выберите все объекты Mesh модели ученика.",
            "6. Нажмите «Проверить модель ученика».",
            "",
            "Автоматически сравниваются:",
            "• размеры всей модели",
            "• количество объектов",
            "• размеры отдельных объектов",
            "• объём",
            "• площадь поверхности",
            "• геометрические характеристики",
            "• отсутствующие объекты",
            "• лишние объекты",
        ]

        for text in instructions:
            layout.label(text=text)


CLASSES = [
    PT_auto,
    PT_info,
]