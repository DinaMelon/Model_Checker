import importlib
import json

from types import SimpleNamespace

import pytest


# ============================================================
# ИМПОРТ ТЕСТИРУЕМОГО МОДУЛЯ
# ============================================================

# Замените model_checker на имя папки вашего аддона.
assignment_module = importlib.import_module(
    "model_checker.assignment"
)


# ============================================================
# ТЕСТОВЫЕ ДАННЫЕ
# ============================================================

@pytest.fixture
def settings():
    # Создаём настройки проверки с известными значениями.
    return SimpleNamespace(
        dimension_tolerance=5.0,
        geometry_tolerance=12.0,
        component_tolerance=0,
    )


@pytest.fixture
def reference_object():
    # Создаём имитацию объекта Blender.
    return SimpleNamespace(
        name="Cube",
        type="MESH",
        hide_render=False,
        dimensions=(2.0, 2.0, 2.0),
    )


@pytest.fixture
def object_stats():
    # Задаём ожидаемые характеристики объекта.
    return {
        "dimensions": [2.0, 2.0, 2.0],
        "volume": 8.0,
        "surface": 24.0,
        "vertices": 8,
        "polygons": 6,
    }


@pytest.fixture
def model_data():
    # Задаём ожидаемые характеристики всей модели.
    return {
        "dimensions": [2.0, 2.0, 2.0],
        "volume": 8.0,
        "surface": 24.0,
        "vertices": 8,
        "polygons": 6,
        "object_count": 1,
    }


# ============================================================
# ТЕСТЫ ФУНКЦИИ build_assignment()
# ============================================================

def test_build_assignment_raises_error_without_meshes(
    monkeypatch,
    settings,
):
    # Имитируем ситуацию, когда в эталоне нет подходящих мешей.
    monkeypatch.setattr(
        assignment_module,
        "mesh_objects",
        lambda objects: [],
    )

    # Функция должна сообщить об отсутствии мешей.
    with pytest.raises(
        ValueError,
        match="Reference contains no mesh objects.",
    ):
        assignment_module.build_assignment(
            [],
            object(),
            settings,
        )


def test_build_assignment_creates_correct_structure(
    monkeypatch,
    settings,
    reference_object,
    object_stats,
    model_data,
):
    # Имитируем фильтрацию объектов.
    monkeypatch.setattr(
        assignment_module,
        "mesh_objects",
        lambda objects: list(objects),
    )

    # Возвращаем заранее заданную сигнатуру всей модели.
    monkeypatch.setattr(
        assignment_module,
        "model_signature",
        lambda objects, depsgraph: model_data.copy(),
    )

    # Возвращаем характеристики отдельного объекта.
    monkeypatch.setattr(
        assignment_module,
        "stats",
        lambda obj, depsgraph: object_stats.copy(),
    )

    # Имитируем подсчёт отдельных компонентов сетки.
    monkeypatch.setattr(
        assignment_module,
        "loose_component_count",
        lambda obj, depsgraph: 1,
    )

    # Создаём задание на основе одного объекта.
    result = assignment_module.build_assignment(
        [reference_object],
        object(),
        settings,
    )

    # Проверяем формат задания.
    assert result["format"] == (
        "automatic_model_similarity_assignment"
    )

    # Проверяем версию формата.
    assert result["version"] == 3

    # Проверяем общие характеристики эталонной модели.
    assert result["reference"]["model"] == model_data

    # Проверяем количество объектов в задании.
    assert len(result["reference"]["objects"]) == 1

    # Проверяем характеристики первого объекта.
    obj_data = result["reference"]["objects"][0]

    assert obj_data["name"] == "Cube"
    assert obj_data["dimensions"] == [2.0, 2.0, 2.0]
    assert obj_data["volume"] == 8.0
    assert obj_data["surface"] == 24.0
    assert obj_data["vertices"] == 8
    assert obj_data["polygons"] == 6
    assert obj_data["loose_components"] == 1

    # Проверяем сохранение настроек сравнения.
    assert result["criteria"] == {
        "dimension_tolerance": 5.0,
        "geometry_tolerance": 12.0,
        "component_tolerance": 0,
    }


def test_build_assignment_filters_objects(
    monkeypatch,
    settings,
    reference_object,
    object_stats,
    model_data,
):
    # Создаём объект камеры, который не должен попасть в задание.
    camera = SimpleNamespace(
        name="Camera",
        type="CAMERA",
        hide_render=False,
    )

    # Имитируем фильтрацию: камера исключается, меш остаётся.
    monkeypatch.setattr(
        assignment_module,
        "mesh_objects",
        lambda objects: [
            obj
            for obj in objects
            if obj.type == "MESH" and not obj.hide_render
        ],
    )

    monkeypatch.setattr(
        assignment_module,
        "model_signature",
        lambda objects, depsgraph: model_data.copy(),
    )

    monkeypatch.setattr(
        assignment_module,
        "stats",
        lambda obj, depsgraph: object_stats.copy(),
    )

    monkeypatch.setattr(
        assignment_module,
        "loose_component_count",
        lambda obj, depsgraph: 1,
    )

    # Передаём меш и камеру одновременно.
    result = assignment_module.build_assignment(
        [reference_object, camera],
        object(),
        settings,
    )

    # В задании должен остаться только меш.
    assert len(result["reference"]["objects"]) == 1
    assert result["reference"]["objects"][0]["name"] == "Cube"


def test_build_assignment_multiple_objects(
    monkeypatch,
    settings,
    object_stats,
    model_data,
):
    # Создаём два отдельных объекта.
    cube = SimpleNamespace(
        name="Cube",
        type="MESH",
        hide_render=False,
    )

    sphere = SimpleNamespace(
        name="Sphere",
        type="MESH",
        hide_render=False,
    )

    # Имитируем фильтрацию объектов.
    monkeypatch.setattr(
        assignment_module,
        "mesh_objects",
        lambda objects: list(objects),
    )

    monkeypatch.setattr(
        assignment_module,
        "model_signature",
        lambda objects, depsgraph: {
            **model_data,
            "object_count": len(objects),
        },
    )

    monkeypatch.setattr(
        assignment_module,
        "stats",
        lambda obj, depsgraph: object_stats.copy(),
    )

    monkeypatch.setattr(
        assignment_module,
        "loose_component_count",
        lambda obj, depsgraph: 1,
    )

    # Создаём задание из двух объектов.
    result = assignment_module.build_assignment(
        [cube, sphere],
        object(),
        settings,
    )

    # Проверяем, что оба объекта попали в задание.
    objects = result["reference"]["objects"]

    assert len(objects) == 2
    assert objects[0]["name"] == "Cube"
    assert objects[1]["name"] == "Sphere"

    # Общая сигнатура должна учитывать два объекта.
    assert result["reference"]["model"]["object_count"] == 2


# ============================================================
# ТЕСТЫ ФУНКЦИИ save()
# ============================================================

def test_save_creates_json_file(tmp_path):
    # Создаём небольшое тестовое задание.
    data = {
        "format": "automatic_model_similarity_assignment",
        "version": 3,
        "reference": {
            "objects": [
                {
                    "name": "Cube",
                    "volume": 8.0,
                }
            ]
        },
    }

    # Создаём путь к временному файлу.
    path = tmp_path / "assignment.json"

    # Сохраняем задание.
    assignment_module.save(data, path)

    # Проверяем, что файл действительно создан.
    assert path.exists()

    # Читаем содержимое файла.
    content = path.read_text(encoding="utf-8")

    # Проверяем, что файл содержит корректный JSON.
    loaded_data = json.loads(content)

    assert loaded_data == data


def test_save_preserves_cyrillic_characters(tmp_path):
    # Создаём задание с русским названием объекта.
    data = {
        "reference": {
            "objects": [
                {
                    "name": "Колесо",
                }
            ]
        }
    }

    path = tmp_path / "assignment.json"

    # Сохраняем данные с ensure_ascii=False.
    assignment_module.save(data, path)

    # Проверяем содержимое файла в кодировке UTF-8.
    content = path.read_text(encoding="utf-8")

    # Русские символы должны сохраняться без Unicode-экранирования.
    assert "Колесо" in content
    assert "\\u041a" not in content

    # После чтения данные должны восстановиться без изменений.
    assert json.loads(content) == data


# ============================================================
# ТЕСТЫ ФУНКЦИИ load()
# ============================================================

def test_load_reads_json_file(tmp_path):
    # Подготавливаем тестовое задание.
    data = {
        "version": 3,
        "reference": {
            "objects": [
                {
                    "name": "Cube",
                    "volume": 8.0,
                }
            ]
        },
    }

    path = tmp_path / "assignment.json"

    # Создаём JSON-файл с тестовыми данными.
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Загружаем данные функцией load().
    result = assignment_module.load(path)

    # Проверяем, что данные восстановлены без изменений.
    assert result == data


def test_load_preserves_cyrillic_characters(tmp_path):
    # Подготавливаем JSON с русским названием объекта.
    data = {
        "reference": {
            "objects": [
                {
                    "name": "Корпус",
                }
            ]
        }
    }

    path = tmp_path / "assignment.json"

    # Записываем данные в UTF-8.
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    # Загружаем задание.
    result = assignment_module.load(path)

    # Проверяем, что название не повредилось.
    assert result["reference"]["objects"][0]["name"] == "Корпус"


def test_load_raises_error_for_missing_file(tmp_path):
    # Указываем путь к несуществующему файлу.
    path = tmp_path / "missing.json"

    # При чтении отсутствующего файла ожидается FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        assignment_module.load(path)


def test_load_raises_error_for_invalid_json(tmp_path):
    # Создаём файл с некорректным JSON.
    path = tmp_path / "invalid.json"
    path.write_text(
        '{"version": 3, invalid}',
        encoding="utf-8",
    )

    # Некорректный JSON должен приводить к JSONDecodeError.
    with pytest.raises(json.JSONDecodeError):
        assignment_module.load(path)


# ============================================================
# ТЕСТ СОХРАНЕНИЯ И ПОСЛЕДУЮЩЕЙ ЗАГРУЗКИ
# ============================================================

def test_save_and_load_round_trip(tmp_path):
    # Создаём тестовое задание.
    original_data = {
        "format": "automatic_model_similarity_assignment",
        "version": 3,
        "reference": {
            "model": {
                "dimensions": [2.0, 2.0, 2.0],
                "volume": 8.0,
            },
            "objects": [
                {
                    "name": "Cube",
                    "dimensions": [2.0, 2.0, 2.0],
                    "volume": 8.0,
                    "surface": 24.0,
                    "loose_components": 1,
                }
            ],
        },
        "criteria": {
            "dimension_tolerance": 5.0,
            "geometry_tolerance": 12.0,
            "component_tolerance": 0,
        },
    }

    path = tmp_path / "assignment.json"

    # Сначала сохраняем задание.
    assignment_module.save(original_data, path)

    # Затем загружаем его из файла.
    loaded_data = assignment_module.load(path)

    # После сохранения и загрузки данные не должны измениться.
    assert loaded_data == original_data
