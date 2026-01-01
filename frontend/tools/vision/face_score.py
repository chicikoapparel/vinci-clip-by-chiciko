def score_faces(faces):
    """
    faces: list of dict {id, x, y, w, h, age}
    return: face dengan score tertinggi
    """

    best = None
    best_score = -1

    for f in faces:
        area = f["w"] * f["h"]
        age = f.get("age", 1)

        # bobot aman (bisa di-tuning)
        score = (
            area * 0.6 +
            age * 120
        )

        if score > best_score:
            best_score = score
            best = f

    return best
