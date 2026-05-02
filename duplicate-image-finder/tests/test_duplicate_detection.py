from duplicate_finder.duplicate_detection import detect_duplicate_groups
from duplicate_finder.repository.image.entity import EMBEDDING_DIM, ImageEntity


class FakeRepository:
    def __init__(self, images: list[ImageEntity], edges: dict[str, list[str]]):
        self._images = images
        self._edges = edges
        self._by_path = {img.path: img for img in images}

    def find_all(self) -> list[ImageEntity]:
        return list(self._images)

    def find_similar(self, path, vector, threshold, limit):
        return [self._by_path[p] for p in self._edges.get(path, [])]


def _img(path: str) -> ImageEntity:
    return ImageEntity(file_hash=path, path=path, vector=[0.0] * EMBEDDING_DIM)


def _paths(group: list[ImageEntity]) -> list[str]:
    return sorted(img.path for img in group)


def test_no_edges_returns_no_groups():
    images = [_img("a"), _img("b"), _img("c")]
    repo = FakeRepository(images, edges={})
    assert (
        detect_duplicate_groups(repo, similarity_threshold=0.1, max_neighbors=50) == []
    )


def test_isolated_pair_forms_one_group():
    images = [_img("a"), _img("b"), _img("c")]
    repo = FakeRepository(images, edges={"a": ["b"], "b": ["a"]})
    groups = detect_duplicate_groups(repo, similarity_threshold=0.1, max_neighbors=50)
    assert len(groups) == 1
    assert _paths(groups[0]) == ["a", "b"]


def test_chain_forms_single_group():
    # A~B, B~C but A is not similar to C. Connected components must still merge them.
    # This catches the regression where "first-seen wins" leaves C as an orphan.
    images = [_img("a"), _img("b"), _img("c")]
    repo = FakeRepository(images, edges={"a": ["b"], "b": ["a", "c"], "c": ["b"]})
    groups = detect_duplicate_groups(repo, similarity_threshold=0.1, max_neighbors=50)
    assert len(groups) == 1
    assert _paths(groups[0]) == ["a", "b", "c"]


def test_bridge_image_merges_two_existing_groups():
    # X bridges {A,B} and {C,D} → all five end up in one group.
    images = [_img("a"), _img("b"), _img("c"), _img("d"), _img("x")]
    repo = FakeRepository(
        images,
        edges={
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
            "x": ["b", "c"],
        },
    )
    groups = detect_duplicate_groups(repo, similarity_threshold=0.1, max_neighbors=50)
    assert len(groups) == 1
    assert _paths(groups[0]) == ["a", "b", "c", "d", "x"]
