from pathlib import Path
from statistics import mean
from typing import Generator, List, Tuple, Union

import numpy as np
import torch
from PIL import Image
from rich.progress import track
from torch import Tensor
from torch.utils.data import DataLoader, Dataset

from yolo.config import DataConfig, DatasetConfig
from yolo.tools.data_augmentation import AugmentationComposer
from yolo.tools.dataset_preparation import prepare_dataset
from yolo.utils.dataset_utils import (
    create_image_metadata,
    locate_label_paths,
    scale_segmentation,
    tensorlize,
)


class YoloDataset(Dataset):
    def __init__(self, data_cfg: DataConfig, dataset_cfg: DatasetConfig, phase: str = "train2017"):
        augment_cfg = data_cfg.data_augment
        self.image_size = data_cfg.image_size
        phase_name = dataset_cfg.get(phase, phase)
        self.batch_size = data_cfg.batch_size
        self.dynamic_shape = getattr(data_cfg, "dynamic_shape", False)
        self.base_size = mean(self.image_size)

        transforms = [eval(aug)(prob) for aug, prob in augment_cfg.items()]
        self.transform = AugmentationComposer(transforms, self.image_size, self.base_size)
        self.transform.get_more_data = self.get_more_data
        self.img_paths, self.bboxes, self.ratios = tensorlize(self.load_data(Path(dataset_cfg.path), phase_name))

    def load_data(self, dataset_path: Path, phase_name: str):
        """
        Loads data from a cache or generates a new cache for a specific dataset phase.

        Parameters:
            dataset_path (Path): The root path to the dataset directory.
            phase_name (str): The specific phase of the dataset (e.g., 'train', 'test') to load or generate data for.

        Returns:
            dict: The loaded data from the cache for the specified phase.
        """
        cache_path = dataset_path / f"{phase_name}.cache"

        if not cache_path.exists():
            data = self.filter_data(dataset_path, phase_name, self.dynamic_shape)
            torch.save(data, cache_path)
        else:
            try:
                data = torch.load(cache_path, weights_only=False)
            except Exception as e:
                raise e

        return data

    def filter_data(self, dataset_path: Path, phase_name: str, sort_image: bool = False) -> list:
        """
        Filters and collects dataset information by pairing images with their corresponding labels.

        Parameters:
            images_path (Path): Path to the directory containing image files.
            labels_path (str): Path to the directory containing label files.
            sort_image (bool): If True, sorts the dataset by the width-to-height ratio of images in descending order.

        Returns:
            list: A list of tuples, each containing the path to an image file and its associated segmentation as a tensor.
        """
        images_path = dataset_path / "images" / phase_name
        labels_path, data_type = locate_label_paths(dataset_path, phase_name)
        images_list = sorted([p.name for p in Path(images_path).iterdir() if p.is_file()])
        if data_type == "json":
            annotations_index, image_info_dict = create_image_metadata(labels_path)

        data = []
        valid_inputs = 0
        for image_name in track(images_list, description="Filtering data"):
            if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            image_id = Path(image_name).stem

            if data_type == "json":
                image_info = image_info_dict.get(image_id, None)
                if image_info is None:
                    continue
                annotations = annotations_index.get(image_info["id"], [])
                image_seg_annotations = scale_segmentation(annotations, image_info)
            elif data_type == "txt":
                label_path = labels_path / f"{image_id}.txt"
                if not label_path.is_file():
                    continue
                with open(label_path, "r") as file:
                    image_seg_annotations = [list(map(float, line.strip().split())) for line in file]
            else:
                image_seg_annotations = []

            labels = self.load_valid_labels(image_id, image_seg_annotations)

            img_path = images_path / image_name
            if sort_image:
                with Image.open(img_path) as img:
                    width, height = img.size
            else:
                width, height = 0, 1
            data.append((img_path, labels, width / height))
            valid_inputs += 1

        data = sorted(data, key=lambda x: x[2], reverse=True)

        return data

    def load_valid_labels(self, label_path: str, seg_data_one_img: list) -> Union[Tensor, None]:
        """
        Loads valid COCO style segmentation data (values between [0, 1]) and converts it to bounding box coordinates
        by finding the minimum and maximum x and y values.

        Parameters:
            label_path (str): The filepath to the label file containing annotation data.
            seg_data_one_img (list): The actual list of annotations (in segmentation format)

        Returns:
            Tensor or None: A tensor of all valid bounding boxes if any are found; otherwise, None.
        """
        bboxes = []
        for seg_data in seg_data_one_img:
            cls = seg_data[0]
            points = self.adapt_labels_list(seg_data[1:])
            points = np.array(points).reshape(-1, 2)
            if (points >= 0).all() and (points <= 1).all():
                valid_points = points[(points >= 0) & (points <= 1)].reshape(-1, 2)
                bbox = torch.tensor([cls, *valid_points.min(axis=0), *valid_points.max(axis=0)])
                bboxes.append(bbox)

        if bboxes:
            return torch.stack(bboxes)
        else:
            return torch.zeros((0, 5))

    def adapt_labels(self, bboxes: Tensor) -> Tensor: 
        """  
        Adapt bounding box labels using vectorized operations.  

        Args:  
            bboxes (Tensor): Tensor of bounding boxes in the format [class_id, width, height, x_center, y_center].  
        
        Returns:  
            Tensor: Tensor of adapted bounding boxes in the format [class_id, xmin, ymin, xmax, ymax].  
        """  
        class_ids = bboxes[:, 0]  
        widths = bboxes[:, 1]  
        heights = bboxes[:, 2]  
        x_centers = bboxes[:, 3]  
        y_centers = bboxes[:, 4]  
    
        xmins = x_centers - widths / 2  
        ymins = y_centers - heights / 2  
        xmaxs = x_centers + widths / 2  
        ymaxs = y_centers + heights / 2  
    
        adapted_bboxes = torch.stack([class_ids, xmins, ymins, xmaxs, ymaxs], dim=1)  
    
        return adapted_bboxes 

    def adapt_labels_list(self, points):
 
        x_center = points[0]  
        y_center = points[1]  
        width = points[2]  
        height = points[3]  
    
        xmin = x_center - width / 2  
        ymin = y_center - height / 2  
        xmax = x_center + width / 2  
        ymax = y_center + height / 2  
    
        return [xmin, ymin, xmax, ymax]

    def get_data(self, idx):
        img_path, bboxes = self.img_paths[idx], self.bboxes[idx]
        valid_mask = bboxes[:, 0] != -1
        with Image.open(img_path) as img:
            img = img.convert("RGB")
        return img, torch.from_numpy(bboxes[valid_mask]), img_path

    def get_more_data(self, num: int = 1):
        indices = torch.randint(0, len(self), (num,))
        return [self.get_data(idx)[:2] for idx in indices]

    def _update_image_size(self, idx: int) -> None:
        """Update image size based on dynamic shape and batch settings."""
        batch_start_idx = (idx // self.batch_size) * self.batch_size
        image_ratio = self.ratios[batch_start_idx].clip(1 / 3, 3)
        shift = ((self.base_size / 32 * (image_ratio - 1)) // (image_ratio + 1)) * 32

        self.image_size = [int(self.base_size + shift), int(self.base_size - shift)]
        self.transform.pad_resize.set_size(self.image_size)

    def __getitem__(self, idx) -> Tuple[Image.Image, Tensor, Tensor, List[str]]:
        img, bboxes, img_path = self.get_data(idx)

        if self.dynamic_shape:
            self._update_image_size(idx)

        img, bboxes, rev_tensor = self.transform(img, bboxes)
        bboxes[:, [1, 3]] *= self.image_size[0]
        bboxes[:, [2, 4]] *= self.image_size[1]
        return img, bboxes, rev_tensor, img_path

    def __len__(self) -> int:
        return len(self.bboxes)


def create_dataloader(data_cfg: DataConfig, dataset_cfg: DatasetConfig, task: str = "train"):
    if task == "inference":
        return StreamDataLoader(data_cfg)

    if getattr(dataset_cfg, "auto_download", False):
        prepare_dataset(dataset_cfg, task)
    dataset = YoloDataset(data_cfg, dataset_cfg, task)

    return DataLoader(
        dataset,
        batch_size=data_cfg.batch_size,
        num_workers=data_cfg.cpu_num,
        pin_memory=data_cfg.pin_memory,
        collate_fn=collate_fn,
    )