#
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the Apache License, Version 2.0
# found in the LICENSE file in the root directory of this source tree.
#

# References:
#   https://github.com/facebookresearch/dino/blob/master/vision_transformer.py
#   https://github.com/rwightman/pytorch-image-models/tree/master/timm/layers/patch_embed.py

# Modifications Copyright 2025 Lightly AG:
# - Modified load_state_dict to handle different number of input channels


import math
from typing import Callable, Optional, Tuple, Union

import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from lightly_train._models import _model_helpers


def make_2tuple(x):
    if isinstance(x, tuple):
        assert len(x) == 2
        return x

    assert isinstance(x, int)
    return (x, x)


class PatchEmbed(nn.Module):
    """
    2D image to patch embedding: (B,C,H,W) -> (B,N,D)

    Args:
        img_size: Image size.
        patch_size: Patch token size.
        in_chans: Number of input image channels.
        embed_dim: Number of linear projection output channels.
        norm_layer: Normalization layer.
    """

    def __init__(
        self,
        img_size: Union[int, Tuple[int, int]] = 224,
        patch_size: Union[int, Tuple[int, int]] = 16,
        in_chans: int = 3,
        embed_dim: int = 768,
        norm_layer: Optional[Callable] = None,
        flatten_embedding: bool = True,
    ) -> None:
        super().__init__()

        image_HW = make_2tuple(img_size)
        patch_HW = make_2tuple(patch_size)
        patch_grid_size = (
            image_HW[0] // patch_HW[0],
            image_HW[1] // patch_HW[1],
        )

        self.img_size = image_HW
        self.patch_size = patch_HW
        self.patches_resolution = patch_grid_size
        self.num_patches = patch_grid_size[0] * patch_grid_size[1]

        self.in_chans = in_chans
        self.embed_dim = embed_dim

        self.flatten_embedding = flatten_embedding

        self.proj = nn.Conv2d(
            in_chans, embed_dim, kernel_size=patch_HW, stride=patch_HW
        )
        self.norm = norm_layer(embed_dim) if norm_layer else nn.Identity()

        if hasattr(self, "register_load_state_dict_pre_hook"):
            self.register_load_state_dict_pre_hook(
                _model_helpers.patch_embed_adjust_input_channels_hook
            )
        else:
            # Backwards compatibility for PyTorch <= 2.4
            self._register_load_state_dict_pre_hook(
                _model_helpers.patch_embed_adjust_input_channels_hook, with_module=True
            )

    def forward(self, x: Tensor) -> Tuple[Tensor, int, int]:
        _, _, H, W = x.shape
        patch_H, patch_W = self.patch_size

        # Find the next multiple of patch size for height & width.
        new_H = math.ceil(H / patch_H) * patch_H
        new_W = math.ceil(W / patch_W) * patch_W

        if new_H != H or new_W != W:
            # Resize image to nearest valid resolution
            x = F.interpolate(
                x, size=(new_H, new_W), mode="bicubic", align_corners=False
            )
            H, W = new_H, new_W

        assert H % patch_H == 0, (
            f"Input image height {H} is not a multiple of patch height {patch_H}"
        )
        assert W % patch_W == 0, (
            f"Input image width {W} is not a multiple of patch width: {patch_W}"
        )

        x = self.proj(x)  # B C H W
        H, W = x.size(2), x.size(3)
        x = x.flatten(2).transpose(1, 2)  # B HW C
        x = self.norm(x)
        if not self.flatten_embedding:
            x = x.reshape(-1, H, W, self.embed_dim)  # B H W C
        return x, new_H, new_W

    def flops(self) -> float:
        Ho, Wo = self.patches_resolution
        flops = (
            Ho
            * Wo
            * self.embed_dim
            * self.in_chans
            * (self.patch_size[0] * self.patch_size[1])
        )
        if self.norm is not None:
            flops += Ho * Wo * self.embed_dim
        return flops
