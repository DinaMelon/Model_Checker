import bmesh


def mesh_objects(objects):
   # Возвращает видимые объекты типа mesh
    return [
        obj
        for obj in objects
        if obj.type == "MESH" and not obj.hide_render
    ]


def stats(obj, depsgraph):
    """
    Возвращает характеристики объекта:

    - dimensions — размеры объекта
    - volume — объём
    - surface — площадь поверхности
    - vertices — количество вершин
    - polygons — количество полигонов
    """

    evaluated_obj = obj.evaluated_get(depsgraph)
    mesh = evaluated_obj.to_mesh()
    try:
        # Объём
        bm = bmesh.new()

        try:
            bm.from_mesh(mesh)
            volume = abs(bm.calc_volume(signed=False))
        finally:
            bm.free()
        # Площадь поверхности
        surface = sum(
            polygon.area
            for polygon in mesh.polygons
        )

        # Результат
        return {
            "dimensions": list(obj.dimensions),
            "volume": float(volume),
            "surface": float(surface),
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
        }

    finally:
        evaluated_obj.to_mesh_clear()


def model_signature(objects, depsgraph):
   # Собирает общие характеристики всей модели

    objects = mesh_objects(objects)
    total_volume = 0.0
    total_surface = 0.0
    total_vertices = 0
    total_polygons = 0

    # Максимальные размеры модели
    dimensions = [0.0, 0.0, 0.0]
    for obj in objects:
        data = stats(obj, depsgraph)

        total_volume += data["volume"]
        total_surface += data["surface"]

        total_vertices += data["vertices"]
        total_polygons += data["polygons"]

        for axis in range(3):
            dimensions[axis] = max(
                dimensions[axis],
                data["dimensions"][axis]
            )

    return {
        "dimensions": dimensions,
        "volume": float(total_volume),
        "surface": float(total_surface),
        "vertices": total_vertices,
        "polygons": total_polygons,
        "object_count": len(objects),
    }

def loose_component_count(
    obj,
    depsgraph,
    min_vertices=4
):
    """
    Считает количество отдельных связанных частей
    внутри одного объекта.

    Например, если меш состоит из:
    - корпуса
    - 4 колёс
    - 2 фар

    функция может определить несколько
    отдельных компонентов.
    """

    evaluated_obj = obj.evaluated_get(depsgraph)
    mesh = evaluated_obj.to_mesh()

    bm = bmesh.new()

    try:
        bm.from_mesh(mesh)
        # Вершины, которые ещё не проверены
        unseen = {
            vertex.index
            for vertex in bm.verts
        }
        # Связи между вершинами
        adjacency = {
            vertex.index: {
                edge.other_vert(vertex).index
                for edge in vertex.link_edges
            }
            for vertex in bm.verts
        }

        component_count = 0
        # Ищем связанные группы вершин
        while unseen:

            start_vertex = next(iter(unseen))

            stack = [start_vertex]
            component_size = 0
            while stack:
                vertex_index = stack.pop()

                if vertex_index not in unseen:
                    continue
                unseen.remove(vertex_index)
                component_size += 1
                neighbours = adjacency.get(
                    vertex_index,
                    set()
                )
                stack.extend(
                    neighbours & unseen
                )
            # Маленькие технические элементы игнорируем
            if component_size >= min_vertices:
                component_count += 1
        return component_count
    finally:
        bm.free()
        evaluated_obj.to_mesh_clear()
