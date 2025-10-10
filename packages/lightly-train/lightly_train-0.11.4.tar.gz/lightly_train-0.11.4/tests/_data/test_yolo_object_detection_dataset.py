#
# Copyright (c) Lightly AG and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
from __future__ import annotations

from pathlib import Path
from typing import Literal

import torch
from albumentations import BboxParams

from lightly_train._data.yolo_object_detection_dataset import (
    YOLOObjectDetectionDataArgs,
    YOLOObjectDetectionDataset,
)
from lightly_train._transforms.object_detection_transform import (
    ObjectDetectionTransform,
    ObjectDetectionTransformArgs,
)
from lightly_train._transforms.transform import (
    ChannelDropArgs,
    RandomFlipArgs,
    RandomPhotometricDistortArgs,
    RandomZoomOutArgs,
    ScaleJitterArgs,
    StopPolicyArgs,
)

from ..helpers import create_yolo_dataset


class DummyTransformArgs(ObjectDetectionTransformArgs):
    channel_drop: ChannelDropArgs | None = None
    num_channels: int | Literal["auto"] = "auto"
    photometric_distort: RandomPhotometricDistortArgs | None = None
    random_zoom_out: RandomZoomOutArgs | None = None
    random_flip: RandomFlipArgs | None = None
    image_size: tuple[int, int] = (32, 32)
    stop_policy: StopPolicyArgs | None = None
    scale_jitter: ScaleJitterArgs | None = None
    bbox_params: BboxParams = BboxParams(
        format="yolo",
        label_fields=["class_labels"],
    )


class TestYoloObjectDetectionDataset:
    def test__split_first(self, tmp_path: Path) -> None:
        create_yolo_dataset(tmp_path=tmp_path, split_first=True)

        args = YOLOObjectDetectionDataArgs(
            path=tmp_path,
            train="train/images",
            val="val/images",
            names={0: "class_0", 1: "class_1"},
        )

        train_args = args.get_train_args()
        val_args = args.get_val_args()

        train_dataset = YOLOObjectDetectionDataset(
            dataset_args=train_args,
            transform=ObjectDetectionTransform(DummyTransformArgs()),
            image_filenames=["0.png", "1.png"],
        )

        val_dataset = YOLOObjectDetectionDataset(
            dataset_args=val_args,
            transform=ObjectDetectionTransform(DummyTransformArgs()),
            image_filenames=["0.png", "1.png"],
        )

        sample = train_dataset[0]
        assert sample["image"].dtype == torch.float32
        assert sample["bboxes"].shape == (1, 4)
        assert sample["classes"].shape == (1,)

        sample = val_dataset[0]
        assert sample["image"].dtype == torch.float32
        assert sample["bboxes"].shape == (1, 4)
        assert sample["classes"].shape == (1,)

    def test__split_last(self, tmp_path: Path) -> None:
        create_yolo_dataset(tmp_path=tmp_path, split_first=False)

        args = YOLOObjectDetectionDataArgs(
            path=tmp_path,
            train="images/train",
            val="images/val",
            names={0: "class_0", 1: "class_1"},
        )

        train_args = args.get_train_args()
        val_args = args.get_val_args()

        train_dataset = YOLOObjectDetectionDataset(
            dataset_args=train_args,
            transform=ObjectDetectionTransform(DummyTransformArgs()),
            image_filenames=["0.png", "1.png"],
        )

        val_dataset = YOLOObjectDetectionDataset(
            dataset_args=val_args,
            transform=ObjectDetectionTransform(DummyTransformArgs()),
            image_filenames=["0.png", "1.png"],
        )

        sample = train_dataset[0]
        assert sample["image"].dtype == torch.float32
        assert sample["bboxes"].shape == (1, 4)
        assert sample["classes"].shape == (1,)

        sample = val_dataset[0]
        assert sample["image"].dtype == torch.float32
        assert sample["bboxes"].shape == (1, 4)
