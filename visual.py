import bpy


def clear():
    """
    Восстанавливает исходный цвет объектов,
    если он был сохранён аддоном.
    """

    for obj in bpy.data.objects:

        if "auto_check_original_color" in obj:

            obj.color = obj["auto_check_original_color"]

            del obj["auto_check_original_color"]


def highlight(result):
    """
    Подсвечивает объекты модели ученика
    в зависимости от результата проверки.

    Зеленый  — хорошее совпадение.
    Желтый   — есть отклонения.
    Красный  — значительные отклонения.

    Положение объектов не учитывается.
    """

    clear()

    status = {}

    for detail in result["details"]:

        # Берём минимальный показатель объекта.
        #
        # Положение здесь НЕ используется.
        minimum_score = min(
            detail["dimensions_score"],
            detail["shape_score"]
        )

        if minimum_score >= 90:
            status[detail["student"]] = "good"

        elif minimum_score >= 70:
            status[detail["student"]] = "warn"

        else:
            status[detail["student"]] = "bad"

    # Подсвечиваем выбранные Mesh-объекты

    for obj in bpy.context.selected_objects:

        if obj.type != 'MESH':
            continue

        # Сохраняем исходный цвет,
        # чтобы потом его можно было восстановить.

        obj["auto_check_original_color"] = list(
            obj.color
        )

        state = status.get(obj.name)

        if state == "good":

            obj.color = (
                0.1,
                0.8,
                0.2,
                1.0
            )

        elif state == "warn":

            obj.color = (
                1.0,
                0.7,
                0.05,
                1.0
            )

        else:

            obj.color = (
                1.0,
                0.1,
                0.05,
                1.0
            )