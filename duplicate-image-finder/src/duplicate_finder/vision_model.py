from typing import Self

from PIL import Image

import torch
from torch.utils.data import DataLoader, Dataset
import torch.nn.functional as F
from transformers import AutoProcessor, Siglip2VisionModel

from duplicate_finder.config import Config
from duplicate_finder.model import ImageToProcess
from duplicate_finder.util.torch_util import determine_device

CKPT = "google/siglip2-so400m-patch16-naflex"


class _ImagePathDataset(Dataset):
    def __init__(self, images: list[ImageToProcess]):
        self.images = images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_to_process = self.images[idx]
        img = Image.open(image_to_process.path).convert("RGB")
        return image_to_process, img


class _Collator:
    def __init__(self, processor):
        self.processor = processor

    def __call__(self, batch):
        image_to_processes = [b[0] for b in batch]
        images = [b[1] for b in batch]
        inputs = self.processor(images=images, return_tensors="pt")
        return image_to_processes, inputs


class VisionModel:
    def __init__(self, model, processor, device, batch_size, num_workers):
        self.model = model
        self.processor = processor
        self.device = device
        self.batch_size = batch_size
        self.num_workers = num_workers

    @classmethod
    def load(cls, config: Config) -> Self:
        device = determine_device()
        dtype = torch.bfloat16 if device != "cpu" else torch.float32
        print(f"[debug] Device: {device} / dtype: {dtype}")

        model = (
            Siglip2VisionModel.from_pretrained(CKPT, torch_dtype=dtype)
            .eval()
            .to(device)
        )
        processor = AutoProcessor.from_pretrained(CKPT)

        return cls(
            model=model,
            processor=processor,
            device=device,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
        )

    def process(
        self, images: list[ImageToProcess]
    ) -> dict[ImageToProcess, list[float]]:
        dataset = _ImagePathDataset(images)
        loader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            collate_fn=_Collator(self.processor),
        )

        result = {}
        with torch.no_grad():
            for batch_images, inputs in loader:
                inputs = inputs.to(self.device)
                vectors = F.normalize(self.model(**inputs).pooler_output, dim=-1)
                for image, vector in zip(batch_images, vectors.float().tolist()):
                    result[image] = vector
        return result
