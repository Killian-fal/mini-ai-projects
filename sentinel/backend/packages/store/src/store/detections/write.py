from bson import ObjectId

from store.connection import collections
from store.detections.schema import Detection
from store.error import guarded


def add_detection(page_id: str, detection: Detection) -> None:
    with guarded():
        collections().pages.update_one(
            {"_id": ObjectId(page_id)}, {"$push": {"detections": detection.to_doc()}}
        )
