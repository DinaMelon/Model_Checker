import json
from pathlib import Path

from .geometry import (
    mesh_objects,
    model_signature,
    stats,
    loose_component_count,
)


def build_assignment(objects, depsgraph, settings):
    """
    Создаёт задание для автоматического сравнения модели.

    Критерии формируются автоматически на основе
    эталонной модели.
    """

    # Получаем только объекты типа MESH
    objects = mesh_objects(objects)

    if not objects:
        raise ValueError(
            "Reference contains no mesh objects."
        )

    # Общая информация об эталонной модели
    model_data = model_signature(
        objects,
        depsgraph
    )

    data = {
        "format": "automatic_model_similarity_assignment",
        "version": 3,

        "reference": {
            "model": model_data,
            "objects": []
        },

        "criteria": {
            "dimension_tolerance": settings.dimension_tolerance,
            "geometry_tolerance": settings.geometry_tolerance,
            "component_tolerance": settings.component_tolerance,
        }
    }

    # Информация об отдельных объектах
    for obj in objects:

        object_stats = stats(
            obj,
            depsgraph
        )

        data["reference"]["objects"].append({
            "name": obj.name,

            "dimensions": object_stats["dimensions"],
            "volume": object_stats["volume"],
            "surface": object_stats["surface"],
            "vertices": object_stats["vertices"],
            "polygons": object_stats["polygons"],

            "loose_components": loose_component_count(
                obj,
                depsgraph,
            ),
        })

    return data


def save(data, path):
    """
    Сохраняет задание в JSON-файл.
    """

    Path(path).write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def load(path):
    """
    Загружает задание из JSON-файла.
    """

    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )

