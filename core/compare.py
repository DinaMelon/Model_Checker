def err(reference, value):
    """
    Процентное отклонение.
    """

    return (
        abs(value - reference)
        / max(abs(reference), 1e-9)
        * 100
    )


def sim(error, tolerance):
    """
    Преобразует процент ошибки в оценку 0..100.
    """

    if tolerance <= 0:
        return 100 if error <= 1e-9 else 0

    score = 100 - error / tolerance * 100

    return max(0, min(100, score))


def vec_error(reference, value):
    """
    Средняя процентная ошибка размеров X/Y/Z.
    """

    errors = [
        err(reference[i], value[i])
        for i in range(3)
    ]

    return sum(errors) / 3


def compare(reference, student, tol_dim, tol_geo):

    # ---------------------------------------------------------
    # РАЗМЕРЫ
    # ---------------------------------------------------------

    reference_dimensions = reference["dimensions"]
    student_dimensions = student["dimensions"]

    dimensions_error = vec_error(
        reference_dimensions,
        student_dimensions
    )

    dimensions_score = sim(
        dimensions_error,
        tol_dim
    )

    # Абсолютная разница по каждой оси

    dimensions_difference = [
        student_dimensions[i]
        - reference_dimensions[i]
        for i in range(3)
    ]

    # Сколько нужно добавить/убавить,
    # чтобы получить размер эталона

    dimensions_correction = [
        reference_dimensions[i]
        - student_dimensions[i]
        for i in range(3)
    ]

    # ---------------------------------------------------------
    # ОБЪЁМ
    # ---------------------------------------------------------

    volume_error = err(
        reference["volume"],
        student["volume"]
    )

    volume_score = sim(
        volume_error,
        tol_geo
    )

    # ---------------------------------------------------------
    # ПЛОЩАДЬ ПОВЕРХНОСТИ
    # ---------------------------------------------------------

    surface_error = err(
        reference["surface"],
        student["surface"]
    )

    surface_score = sim(
        surface_error,
        tol_geo
    )

    # ---------------------------------------------------------
    # ГЕОМЕТРИЯ
    # ---------------------------------------------------------

    shape_score = (
        volume_score
        + surface_score
    ) / 2

    shape_error = (
        volume_error
        + surface_error
    ) / 2

    return {
        # Процентные показатели
        "dimensions_error": dimensions_error,
        "dimensions_score": dimensions_score,

        "volume_error": volume_error,
        "volume_score": volume_score,

        "surface_error": surface_error,
        "surface_score": surface_score,

        "shape_error": shape_error,
        "shape_score": shape_score,

        # Абсолютные размеры
        "reference_dimensions": list(
            reference_dimensions
        ),

        "student_dimensions": list(
            student_dimensions
        ),

        "dimensions_difference": dimensions_difference,

        "dimensions_correction": dimensions_correction,
    }