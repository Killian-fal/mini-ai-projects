import argparse
from pathlib import Path

from duplicate_finder.config import load_config
from duplicate_finder.duplicate_detection import detect_duplicate_groups
from duplicate_finder.repository.duplicate_group.repository import (
    DuplicateGroupRepository,
)
from duplicate_finder.repository.image.entity import ImageEntity
from duplicate_finder.repository.image.repository import ImageRepository
from duplicate_finder.model import ImageToProcess
from duplicate_finder.util.image_util import image_sha256, is_valid_image
from duplicate_finder.vision_model import VisionModel


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Skip launching the AgentOS server after indexation.",
    )
    args = parser.parse_args()

    print("Running duplicate finder app...")
    config = load_config(Path("config.yaml"))

    image_repository = ImageRepository(config)
    group_repository = DuplicateGroupRepository(config)
    vision_model = VisionModel.load(config)

    to_process = []
    for path in config.folder.rglob("*"):
        if not path.is_file():
            continue

        spath = str(path)

        if image_repository.find_by_path(spath) is not None:
            print(f"[skip] Already processed: {spath}")
            continue

        if not is_valid_image(path):
            print(f"[skip] Invalid image: {spath}")
            continue

        file_hash = image_sha256(path)

        if (existing := image_repository.find_by_file_hash(file_hash)) is not None:
            print(f"[copy] Already exists: {spath} (hash: {file_hash})")
            image_repository.insert(
                ImageEntity(
                    file_hash=file_hash,
                    path=spath,
                    vector=existing.vector,
                )
            )
            continue

        print(f"[process] {spath} (hash: {file_hash})")
        to_process.append(ImageToProcess(file_hash=file_hash, path=spath))

    print(f"Total to process: {len(to_process)}")

    if to_process:
        image_vectors = vision_model.process(to_process)
        for image_to_process, vector in image_vectors.items():
            print(
                f"[insert] {image_to_process.path} (hash: {image_to_process.file_hash})"
            )
            image_repository.insert(
                ImageEntity(
                    file_hash=image_to_process.file_hash,
                    path=image_to_process.path,
                    vector=vector,
                )
            )

    print("\nDetecting duplicate groups...")
    groups = detect_duplicate_groups(
        image_repository,
        similarity_threshold=config.similarity_threshold,
        max_neighbors=config.max_neighbors,
    )

    print(f"\nFound {len(groups)} duplicate group(s):")
    for i, group in enumerate(groups, start=1):
        print(f"\n[group {i}] {len(group)} images:")
        for img in group:
            print(f"  - {img.path} (hash: {img.file_hash})")

    group_repository.save(groups)
    print(f"\nPersisted {len(groups)} group(s)")

    if args.no_agent:
        print("\n[--no-agent] Skipping agent startup.")
        return

    from duplicate_finder.agent.server import run_agent_os

    run_agent_os(config, image_repository, group_repository)
