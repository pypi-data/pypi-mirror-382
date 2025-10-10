# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""VAD Dataset.

This module provides PyTorch Dataset implementation for the VAD dataset. The
dataset will be downloaded and extracted automatically if not found locally.

The dataset contains one category of industrial objects with both normal and
anomalous samples.

License:
    VAD dataset is released under the Creative Commons
    Attribution-NonCommercial-ShareAlike 4.0 International License
    (CC BY-NC-SA 4.0).
    https://creativecommons.org/licenses/by-nc-sa/4.0/

Reference:
    Aimira Baitieva, David Hurych, Victor Besnier, Olivier Bernard:
    Supervised Anomaly Detection for Complex Industrial Images; in:
    The IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024,
    pp. 17754-17762, DOI: 10.1109/CVPR52733.2024.01681.
"""

from collections.abc import Sequence
from pathlib import Path

from pandas import DataFrame
from torchvision.transforms.v2 import Transform

from anomalib.data.datasets.base import AnomalibDataset
from anomalib.data.errors import MisMatchError
from anomalib.data.utils import LabelName, Split, validate_path

IMG_EXTENSIONS = (".png", ".PNG")
CATEGORIES = ("vad",)


class VADDataset(AnomalibDataset):
    """VAD dataset class.

    Dataset class for loading and processing VAD dataset images. Supports
    only classification task.

    Args:
        root (Path | str): Path to root directory containing the dataset.
            Defaults to ``"./datasets/VAD"``.
        category (str): Category name, must be one of ``CATEGORIES``.
            Defaults to ``"vad"``.
        augmentations (Transform, optional): Augmentations that should be applied to the input images.
            Defaults to ``None``.
        split (str | Split | None, optional): Dataset split - usually
            ``Split.TRAIN`` or ``Split.TEST``. Defaults to ``None``.

    Example:
        >>> from pathlib import Path
        >>> from anomalib.data.datasets import VADDataset
        >>> dataset = VADDataset(
        ...     root=Path("./datasets/VAD"),
        ...     category="vad",
        ...     split="train"
        ... )

        For classification tasks, each sample contains:

        >>> sample = dataset[0]
        >>> list(sample.keys())
        ['image_path', 'label', 'image']

        For segmentation tasks, samples also include mask paths and masks:

        >>> dataset.task = "segmentation"
        >>> sample = dataset[0]
        >>> list(sample.keys())
        ['image_path', 'label', 'image', 'mask_path', 'mask']

        Images are PyTorch tensors with shape ``(C, H, W)``, masks have shape
        ``(H, W)``:

        >>> sample["image"].shape, sample["mask"].shape
        (torch.Size([3, 256, 256]), torch.Size([256, 256]))
    """

    def __init__(
        self,
        root: Path | str = "./datasets/VAD",
        category: str = "vad",
        augmentations: Transform | None = None,
        split: str | Split | None = None,
    ) -> None:
        super().__init__(augmentations=augmentations)

        self.root_category = Path(root) / Path(category)
        self.category = category
        self.split = split
        self.samples = make_vad_dataset(
            self.root_category,
            split=self.split,
            extensions=IMG_EXTENSIONS,
        )


def make_vad_dataset(
    root: str | Path,
    split: str | Split | None = None,
    extensions: Sequence[str] | None = None,
) -> DataFrame:
    """Create VAD AD samples by parsing the data directory structure.

    The files are expected to follow the structure:
        ``path/to/dataset/split/category/image_filename.png``
        ``path/to/dataset/ground_truth/category/mask_filename.png``

    Args:
        root (Path | str): Path to dataset root directory
        split (str | Split | None, optional): Dataset split (train or test)
            Defaults to ``None``.
        extensions (Sequence[str] | None, optional): Valid file extensions
            Defaults to ``None``.

    Returns:
        DataFrame: Dataset samples with columns:
            - path: Base path to dataset
            - split: Dataset split (train/test)
            - label: Class label
            - image_path: Path to image file
            - mask_path: Path to mask file (if available)
            - label_index: Numeric label (0=normal, 1=abnormal)

    Example:
        >>> root = Path("./datasets/VAD/vad")
        >>> samples = make_vad_dataset(root, split="train")
        >>> samples.head()
           path                split label image_path           mask_path label_index
        0  datasets/VAD/vad train good  [...]/good/2041.png                         0
        1  datasets/VAD/vad train good  [...]/good/2565.png                         0

    Raises:
        RuntimeError: If no valid images are found
        MisMatchError: If anomalous images and masks don't match
    """
    if extensions is None:
        extensions = IMG_EXTENSIONS

    root = validate_path(root)
    samples_list = [(str(root), *f.parts[-3:]) for f in root.glob(r"**/*") if f.suffix in extensions]
    if not samples_list:
        msg = f"Found 0 images in {root}"
        raise RuntimeError(msg)

    samples = DataFrame(samples_list, columns=["path", "split", "label", "image_path"])

    # Modify image_path column by converting to absolute path
    samples["image_path"] = samples.path + "/" + samples.split + "/" + samples.label + "/" + samples.image_path

    # Create label index for normal (0) and anomalous (1) images.
    samples.loc[(samples.label == "good"), "label_index"] = LabelName.NORMAL
    samples.loc[(samples.label != "good"), "label_index"] = LabelName.ABNORMAL
    samples.label_index = samples.label_index.astype(int)

    # separate masks from samples
    mask_samples = samples.loc[samples.split == "ground_truth"].sort_values(
        by="image_path",
        ignore_index=True,
    )
    samples = samples[samples.split != "ground_truth"].sort_values(
        by="image_path",
        ignore_index=True,
    )

    # assign mask paths to anomalous test images
    samples["mask_path"] = None
    samples.loc[
        (samples.split == "test") & (samples.label_index == LabelName.ABNORMAL),
        "mask_path",
    ] = mask_samples.image_path.to_numpy()

    # assert that the right mask files are associated with the right test images
    abnormal_samples = samples.loc[samples.label_index == LabelName.ABNORMAL]
    if (
        len(abnormal_samples)
        and not abnormal_samples.apply(
            lambda x: Path(x.image_path).stem in Path(x.mask_path).stem,
            axis=1,
        ).all()
    ):
        msg = (
            "Mismatch between anomalous images and ground truth masks. Make sure "
            "mask files in 'ground_truth' folder follow the same naming "
            "convention as the anomalous images (e.g. image: '000.png', "
            "mask: '000.png' or '000_mask.png')."
        )
        raise MisMatchError(msg)

    # infer the task type
    samples.attrs["task"] = "classification" if (samples["mask_path"] == "").all() else "segmentation"

    if split:
        samples = samples[samples.split == split].reset_index(drop=True)

    return samples
