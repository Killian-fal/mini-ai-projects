from duplicate_finder.repository.image.entity import ImageEntity
from duplicate_finder.repository.image.repository import ImageRepository


def detect_duplicate_groups(
    repository: ImageRepository,
    similarity_threshold: float,
    max_neighbors: int,
) -> list[list[ImageEntity]]:
    images = repository.find_all()
    by_path = {img.path: img for img in images}

    groups = []
    for img in images:
        neighbors = repository.find_similar(
            path=img.path,
            vector=list(img.vector),
            threshold=similarity_threshold,
            limit=max_neighbors,
        )

        if neighbors:
            groups.append(set([img.path] + [n.path for n in neighbors]))

    merged = []
    for group in groups:
        indices = [i for i, mg in enumerate(merged) if not mg.isdisjoint(group)]

        if indices:
            new_group = group.union(*[merged[i] for i in indices])
            merged = [mg for i, mg in enumerate(merged) if i not in indices]
            merged.append(new_group)
        else:
            merged.append(group)

    return [[by_path[path] for path in group] for group in merged]
