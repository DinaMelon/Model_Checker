# План разработки: Automatic Model Similarity Checker

Чеклист задач по этапам. Каждый пункт можно продублировать как отдельный GitHub Issue
(см. `create_github_issues.sh`) — тогда галочки в этом файле можно менять вручную,
а реальный статус (To do / In Progress / Done) отслеживать через Issues/Project Board.

## Этап 0. Планирование и архитектура
- [ ] Зафиксировать сценарий "учитель → эталон, студент → проверка"
- [ ] Спроектировать JSON-схему `criteria.json`
- [ ] Определить веса итоговой оценки (parts/dimensions/position/geometry)
- [ ] Ревью архитектуры

## Этап 1. Каркас аддона
- [ ] `__init__.py`: bl_info
- [ ] `__init__.py`: сбор CLASSES из properties/operators/panels
- [ ] `__init__.py`: register()/unregister(), Scene.auto_check
- [ ] Тест: установка/выгрузка в Blender без ошибок в консоли
- [ ] Тест: unregister() не оставляет висящих классов/свойств

## Этап 2. Настройки пользователя (properties.py)
- [ ] PropertyGroup: пути к файлам (reference_file, student_file, assignment_file)
- [ ] PropertyGroup: допуски (dimension/position/geometry/component_tolerance)
- [ ] PropertyGroup: флаги (use_loose_parts, normalize_orientation)
- [ ] PropertyGroup: служебные поля (reference_loaded, result_ready)
- [ ] Тест: свойства появляются в UI и сохраняются
- [ ] Тест: граничные значения допусков (0%, 100%)

## Этап 3. Ядро геометрии (core/geometry.py)
- [ ] mesh_objects()
- [ ] world_bbox()
- [ ] stats() — volume/surface/vertices/polygons
- [ ] normalized_center()
- [ ] sample() — облако точек формы
- [ ] model_signature()
- [ ] loose_component_count()
- [ ] Unit-тесты чистой математики (pytest, мок Vector)
- [ ] In-Blender тесты на примитивах (куб, сфера — сверка с формулами)
- [ ] Тест на плоский меш (деление на ноль)
- [ ] Тест loose_component_count на объекте из 3 раздельных кусков

## Этап 4. Генерация эталона (core/assignment.py)
- [ ] build_assignment()
- [ ] save()/load()
- [ ] Round-trip тест save→load
- [ ] Тест на пустой сцене (ValueError)
- [ ] Ручной тест на реальной учебной модели

## Этап 5. Логика сравнения (core/compare.py)
- [ ] err(), sim()
- [ ] vec_error(), dist()
- [ ] chamfer()
- [ ] compare()
- [ ] Unit-тесты (pytest): err, sim, chamfer на идентичных/пустых облаках
- [ ] Тест устойчивости к делению на ноль

## Этап 6. Сопоставление и скоринг (core/check.py)
- [ ] best_object()
- [ ] check() — missing/extra, overall score
- [ ] Сценарный тест: студент = точная копия эталона (~100%)
- [ ] Сценарный тест: отсутствующий объект → missing
- [ ] Сценарный тест: лишний объект → extras
- [ ] Сценарный тест: искажённый объект → падение score
- [ ] Тест производительности на 50+ объектах
- [ ] Тест на "ложное совпадение" по объёму при разной геометрии

## Этап 7. Blender-операторы (operators.py)
- [ ] OT_create_reference
- [ ] OT_load_reference
- [ ] OT_import_criteria
- [ ] OT_check
- [ ] OT_export
- [ ] OT_clear
- [ ] Ручное тестирование каждого оператора в UI
- [ ] Тест обработки ошибок (некорректный путь, пустое выделение)
- [ ] Тест на утечки временной сцены/объектов после OT_load_reference

## Этап 8. Визуализация (visual.py)
- [ ] highlight()
- [ ] clear()
- [ ] Тест: clear() полностью восстанавливает исходный цвет
- [ ] Тест: повторный highlight() без clear() не портит сохранённый цвет

## Этап 9. Экспорт отчёта (report.py)
- [ ] export() — JSON
- [ ] export() — HTML с таблицей
- [ ] Тест экранирования спецсимволов в именах объектов
- [ ] Визуальная проверка HTML в браузере
- [ ] Тест кодировки (кириллица)

## Этап 10. UI-панели (panels.py)
- [ ] PT_auto — основная панель
- [ ] PT_info — инструкция "How it works"
- [ ] UX-тест с реальным пользователем
- [ ] Проверка на пустых состояниях (нет assignment/result)

## Этап 11. Интеграционное и приёмочное тестирование
- [ ] Полный e2e прогон на реальных файлах
- [ ] Тест на Blender 3.6 и 4.x
- [ ] Тест с некорректными входными файлами
- [ ] Нагрузочный тест на тяжёлых моделях
- [ ] Подготовить тестовые .blend фикстуры (tests/fixtures/)

## Этап 12. Документация и упаковка
- [ ] Обновить README.md (FAQ, ограничения)
- [ ] Собрать .zip для установки
- [ ] Инструкция для преподавателя
- [ ] Установка "с нуля" по инструкции на чистой машине
