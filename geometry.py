import bpy, bmesh, math
from mathutils import Vector

def mesh_objects(objects):
    return [o for o in objects if o.type == 'MESH' and not o.hide_render]

def world_bbox(objects):
    pts=[]
    for o in mesh_objects(objects):
        pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return Vector((0,0,0)), Vector((0,0,0))
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx

def stats(o, dg):
    eo=o.evaluated_get(dg)
    me=eo.to_mesh()
    try:
        bm=bmesh.new()
        bm.from_mesh(me)
        bm.transform(eo.matrix_world)
        vol=abs(bm.calc_volume(signed=False))
        bm.free()
        surface=sum(p.area for p in me.polygons)
        return {
            "dimensions": list(o.dimensions),
            "volume": float(vol),
            "surface": float(surface),
            "vertices": len(me.vertices),
            "polygons": len(me.polygons),
        }
    finally:
        eo.to_mesh_clear()

def center(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector())/8

def normalized_center(o,mn,mx):
    c=center(o); s=mx-mn
    return [float((c[i]-mn[i])/s[i]) if abs(s[i])>1e-9 else .5 for i in range(3)]

def sample(o,dg,n=700):
    eo=o.evaluated_get(dg); me=eo.to_mesh()
    try:
        pts=[eo.matrix_world @ v.co for v in me.vertices]
        if not pts: return []
        if len(pts)>n:
            step=max(1,len(pts)//n); pts=pts[::step][:n]
        mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
        mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
        s=mx-mn
        return [[(p[i]-mn[i])/s[i] if abs(s[i])>1e-9 else .5 for i in range(3)] for p in pts]
    finally: eo.to_mesh_clear()

def model_signature(objects,dg):
    mn,mx=world_bbox(objects); size=mx-mn
    total_vol=sum(stats(o,dg)["volume"] for o in mesh_objects(objects))
    total_surface=sum(stats(o,dg)["surface"] for o in mesh_objects(objects))
    return {
        "dimensions":list(size),
        "volume":float(total_vol),
        "surface":float(total_surface),
        "object_count":len(mesh_objects(objects)),
        "bbox_min":list(mn),"bbox_max":list(mx)
    }

def loose_component_count(o, dg, min_volume=1e-6):
    eo = o.evaluated_get(dg)
    me = eo.to_mesh()

    bm = None

    try:
        bm = bmesh.new()
        bm.from_mesh(me)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Обязательно создаём таблицу индексов
        bm.verts.ensure_lookup_table()

        comps = []

        # Индексы всех вершин
        unseen = {v.index for v in bm.verts}

        # Строим связи между вершинами
        adjacency = {}

        for v in bm.verts:
            adjacency[v.index] = {
                edge.other_vert(v).index
                for edge in v.link_edges
            }

        # Ищем связанные компоненты
        while unseen:
            seed = next(iter(unseen))

            stack = [seed]
            comp = set()

            while stack:
                x = stack.pop()

                if x not in unseen:
                    continue

                unseen.remove(x)
                comp.add(x)

                # Добавляем соседние вершины
                stack.extend(
                    adjacency.get(x, set()) & unseen
                )

            # Считаем только достаточно крупные компоненты
            if len(comp) >= 4:
                sub = bmesh.new()

                try:
                    # Копируем вершины компонента
                    for idx in comp:
                        nv = sub.verts.new(
                            bm.verts[idx].co
                        )

                    # После добавления вершин также обновляем таблицу
                    sub.verts.ensure_lookup_table()

                    comps.append(len(comp))

                finally:
                    sub.free()

        return len(comps)

    finally:
        if bm is not None:
            bm.free()

        eo.to_mesh_clear()
