import bpy

from .geometry import (
    mesh_objects,
    model_signature,
    stats,
)

from .compare import (
    compare,
    err,
)


def best_object(ref, candidates, used, depsgraph):
    """
    Находит наиболее подходящий объект ученика
    для объекта из эталонной модели.

    Для сопоставления используются:
    - размеры;
    - объём;
    - имя объекта.
    """

    best_index = None
    best_cost = float("inf")

    for index, obj in enumerate(candidates):

        # Объект уже сопоставлен
        if index in used:
            continue

        object_stats = stats(
            obj,
            depsgraph
        )

        # -------------------------
        # Ошибка размеров
        # -------------------------

        dimensions_error = sum(
            abs(
                err(
                    ref["dimensions"][axis],
                    object_stats["dimensions"][axis]
                )
            )
            for axis in range(3)
        )

        # -------------------------
        # Ошибка объёма
        # -------------------------

        volume_error = abs(
            err(
                ref["volume"],
                object_stats["volume"]
            )
        )

        # -------------------------
        # Сравнение имён
        # -------------------------

        reference_name = (
            ref["name"]
            .lower()
            .split(".")[0]
        )

        student_name = obj.name.lower()

        name_bonus = (
            0
            if reference_name in student_name
            else 5
        )

        # -------------------------
        # Итоговая стоимость
        # -------------------------

        cost = (
            dimensions_error
            + volume_error * 0.25
            + name_bonus
        )

        if cost < best_cost:
            best_cost = cost
            best_index = index

    return best_index


def check(objects, assignment, settings):
    """
    Проверяет модель ученика относительно эталонной модели.

    Проверяются:

    - наличие объектов;
    - размеры;
    - объём;
    - площадь поверхности;
    - геометрическая форма;
    - количество объектов.

    Положение объектов в сцене НЕ учитывается.
    """

    # -------------------------
    # Объекты ученика
    # -------------------------

    objects = mesh_objects(objects)

    if not objects:
        raise ValueError(
            "Select student's mesh objects."
        )

    depsgraph = (
        bpy.context.evaluated_depsgraph_get()
    )

    # -------------------------
    # Эталонная модель
    # -------------------------

    reference_model = (
        assignment["reference"]["model"]
    )

    references = (
        assignment["reference"]["objects"]
    )

    # -------------------------
    # Модель ученика
    # -------------------------

    student_model = model_signature(
        objects,
        depsgraph
    )

    # -------------------------
    # Сопоставление объектов
    # -------------------------

    used = set()
    details = []
    missing = []

    for reference in references:

        index = best_object(
            reference,
            objects,
            used,
            depsgraph
        )

        # Эталонный объект не найден
        if index is None:
            missing.append(reference)
            continue

        used.add(index)

        student_object = objects[index]

        student_stats = stats(
            student_object,
            depsgraph
        )

        # -------------------------
        # Сравнение геометрии
        # -------------------------

        comparison = compare(
            reference,

            {
                "dimensions": student_stats["dimensions"],
                "volume": student_stats["volume"],
                "surface": student_stats["surface"],
            },

            settings.dimension_tolerance,
            settings.geometry_tolerance,
        )

        # -------------------------
        # Результат объекта
        # -------------------------

        details.append({
        "reference": reference["name"],
        "student": student_object.name,

        # Проценты
        "dimensions_score":
            comparison["dimensions_score"],

        "volume_score":
            comparison["volume_score"],

        "surface_score":
            comparison["surface_score"],

        "shape_score":
            comparison["shape_score"],

        # Ошибки в процентах
        "dimensions_error":
            comparison["dimensions_error"],

        "volume_error":
            comparison["volume_error"],

        "surface_error":
            comparison["surface_error"],

        "shape_error":
            comparison["shape_error"],

        # Фактические размеры
        "reference_dimensions":
            comparison["reference_dimensions"],

        "student_dimensions":
            comparison["student_dimensions"],

        # Разница
        "dimensions_difference":
            comparison["dimensions_difference"],

        # Необходимая коррекция
        "dimensions_correction":
            comparison["dimensions_correction"],
    })

    # -------------------------
    # Лишние объекты
    # -------------------------

    extras = [
        obj.name
        for index, obj in enumerate(objects)
        if index not in used
    ]

    # -------------------------
    # Общие показатели
    # -------------------------

    reference_count = len(references)
    matched_count = len(details)

    # Процент найденных частей
    parts = (
        matched_count
        / max(1, reference_count)
        * 100
    )

    # Средняя оценка размеров
    dimensions = (
        sum(
            item["dimensions_score"]
            for item in details
        )
        / max(1, len(details))
    )

    # Средняя оценка геометрии
    geometry = (
        sum(
            (
                item["volume_score"]
                + item["surface_score"]
                + item["shape_score"]
            ) / 3
            for item in details
        )
        / max(1, len(details))
    )

    # -------------------------
    # Итоговая оценка
    # -------------------------

    overall = (
        parts * 0.30
        + dimensions * 0.30
        + geometry * 0.40
    )

    return {
        "overall": overall,
        "parts": parts,
        "dimensions": dimensions,
        "geometry": geometry,

        "missing": [
            item["name"]
            for item in missing
        ],

        "extras": extras,
        "details": details,

        "student_model": student_model,
        "reference_model": reference_model,
    }