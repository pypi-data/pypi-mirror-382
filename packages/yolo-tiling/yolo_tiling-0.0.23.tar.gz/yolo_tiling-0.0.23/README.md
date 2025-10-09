# YOLO Dataset tiling

<div align="center">

[![python-version](https://img.shields.io/pypi/pyversions/yolo-tiling.svg)](https://pypi.org/project/yolo-tiling)
[![version](https://img.shields.io/pypi/v/yolo-tiling.svg)](https://pypi.python.org/pypi/yolo-tiling)
[![pypi-passing](https://github.com/Jordan-Pierce/yolo-tiling/actions/workflows/pypi.yml/badge.svg)](https://pypi.org/project/yolo-tiling)
[![windows](https://github.com/Jordan-Pierce/yolo-tiling/actions/workflows/windows.yml/badge.svg)](https://pypi.org/project/yolo-tiling)
[![macos](https://github.com/Jordan-Pierce/yolo-tiling/actions/workflows/macos.yml/badge.svg)](https://pypi.org/project/yolo-tiling)
[![ubuntu](https://github.com/Jordan-Pierce/yolo-tiling/actions/workflows/ubuntu.yml/badge.svg)](https://pypi.org/project/yolo-tiling)
</div>

This module can cut images and corresponding labels from a YOLO dataset into tiles of specified size and create a
new dataset based on these tiles. It supports object detection, instance segmentation, semantic segmentation, and image classification.
Credit for the original repository goes to [slanj](https://github.com/slanj/yolo-tiling).

## Installation

To install the package, use pip:

```bash
pip install yolo-tiling
```

## Usage

```python
from yolo_tiler import YoloTiler, TileConfig

src = "path/to/dataset"         # Source YOLO dataset directory
dst = "path/to/tiled_dataset"   # Output directory for tiled dataset

config = TileConfig(
    # Size of each tile (width, height). Can be:
    # - Single integer for square tiles: slice_wh=640
    # - Tuple for rectangular tiles: slice_wh=(640, 480)
    slice_wh=(640, 480),

    # Overlap between adjacent tiles. Can be:
    # - Single float (0-1) for uniform overlap percentage: overlap_wh=0.1
    # - Tuple of floats for different overlap in each dimension: overlap_wh=(0.1, 0.1)
    # - Single integer for pixel overlap: overlap_wh=64
    # - Tuple of integers for different pixel overlaps: overlap_wh=(64, 48)
    overlap_wh=(0.1, 0.1),

    # Input image file extension to process
    input_ext=".png",

    # Output image file extension to save (default: same as input_ext)
    # Note: Output mask must be .png for semantic_segmentation
    output_ext=None,

    # Type of YOLO annotations to process:
    # - "object_detection": Standard YOLO format (class, x, y, width, height)
    # - "instance_segmentation": YOLO segmentation format (class, x1, y1, x2, y2, ...)
    # - "semantic_segmentation": PNG mask format (0=background, 1-255=class IDs)
    # - "image_classification": YOLO classification format (class)
    annotation_type="instance_segmentation",

    # For instance segmentation only: Controls point density along polygon edges
    # Lower values = more points, higher quality but larger files
    densify_factor=0.01,

    # For instance segmentation only: Controls polygon smoothing
    # Lower values = more details preserved, higher values = smoother shapes
    smoothing_tolerance=0.99,

    # Dataset split ratios (must sum to 1.0)
    train_ratio=0.7,  # Proportion of data for training
    valid_ratio=0.2,  # Proportion of data for validation
    test_ratio=0.1,   # Proportion of data for testing

    # Optional margins to exclude from input images. Can be:
    # - Single float (0-1) for uniform margin percentage: margins=0.1
    # - Tuple of floats for different margins: margins=(0.1, 0.1, 0.1, 0.1)
    # - Single integer for pixel margins: margins=64
    # - Tuple of integers for different pixel margins: margins=(64, 64, 64, 64)
    margins=0.0,

    # Include negative samples (tiles without any instances)
    include_negative_samples=True

    # Include source data (copied over, and included in the tiled dataset)
    copy_source_data=False,

    # Compression setting (interpreted differently for each format):
    # - JPEG/JPG: Quality level (0-100)
    # - PNG: Automatically converts to compression level (0-9)
    # - TIFF: Selects appropriate compression method based on quality
    #   * High quality (≥90): Lossless LZW compression
    #   * Medium quality (≥75): Lossless DEFLATE compression
    #   * Lower quality (<75): JPEG compression with adjusted quality
    # - BMP: No compression supported
    compression=90
)

tiler = YoloTiler(
    source=src,
    target=dst,
    config=config,
    num_viz_samples=5,                      # Number of samples to visualize
    show_processing_status=True,            # Show the progress of the tiling process
    progress_callback=progress_callback     # Optional callback function to report progress (see below)
)

tiler.run()
```

```python
@dataclass
class TileProgress:
    """Data class to track tiling progress"""
    current_set_name: str = ""
    current_image_name: str = ""
    current_image_idx: int = 0
    total_images: int = 0
    current_tile_idx: int = 0
    total_tiles: int = 0
```

Using `TileProgress` custom callback functions can be created. An example of an (optional) `progress_callback` function
can be seen below:

```python
from yolo_tiler import TilerProgress

def progress_callback(progress: TileProgress):
    # Determine whether to show tile or image progress
    if progress.total_tiles > 0:
        print(f"Processing {progress.current_image_name} in {progress.current_set_name} set: "
              f"Tile {progress.current_tile_idx}/{progress.total_tiles}")
    else:
        print(f"Processing {progress.current_image_name} in {progress.current_set_name} set: "
              f"Image {progress.current_image_idx}/{progress.total_images}")

```

### Notes

- The tiler **requires** a YOLO dataset structure within the source directory (see below).
- If only a `train` folder exists, the train / valid / test ratios will be used to split the tiled `train` folder.
- If there already exists train / valid / test folders in the source directory, the ratios are ignored.
- Tiles are named as `basename_top-left_bottom-right_width_height.ext`.
- `copy_source_data` will make copy the original YOLO dataset to the output folder (for multiscale).
- Pay attention to the differences between the `valid` and `val` folder for different tasks.

#### Object Detection, Instance Segmentation, and Semantic Segmentation

```bash
dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/  # <--- "valid", not "val"
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml  # Optional
```

#### Image Classification

```bash
dataset/
├── train/
│   ├── class_1/
│   └── class_2/
├── val/    # <--- "val", not "valid"
│   ├── class_1/
│   └── class_2/
├── test/
    ├── class_1/
    └── class_2/
```

**Note**: For semantic segmentation, the `labels/` folders contain PNG mask files (single channel, uint8) where pixel values represent class IDs (0 = background, 1-255 = classes). Tiled masks are also saved as PNG files regardless of the output format specified for images. For object detection and instance segmentation, the `labels/` folders contain `.txt` files with YOLO format annotations.

### Test Data

```bash
python tests/test_yolo_tiler.py
```

## Command Line Usage

In addition to using the tiler within a script, it can also use the command line interface to run the tiling process.
Here are the instructions:

```bash
yolo-tiling --source --target [--slice_wh SLICE_WH SLICE_WH] [--overlap_wh OVERLAP_WH OVERLAP_WH] [--input_ext INPUT_EXT] [--output_ext OUTPUT_EXT] [--annotation_type ANNOTATION_TYPE] [--densify_factor DENSIFY_FACTOR] [--smoothing_tolerance SMOOTHING_TOLERANCE] [--train_ratio TRAIN_RATIO] [--valid_ratio VALID_RATIO] [--test_ratio TEST_RATIO] [--margins MARGINS] [--include_negative_samples INCLUDE_NEGATIVE_SAMPLES] [--compression COMPRESSION]
```

### Example Commands

1. Basic usage with default parameters:
```bash
yolo-tiling --source tests/detection --target tests/detection_tiled
```

2. Custom slice size and overlap:
```bash
yolo-tiling --source tests/detection --target tests/detection_tiled --slice_wh 640 480 --overlap_wh 0.1 0.1
```

3. Custom annotation type and image extension:
```bash
yolo-tiling --source tests/segmentation --target tests/segmentation_tiled --annotation_type instance_segmentation --input_ext .jpg --output_ext .png
```

4. Semantic segmentation with PNG masks:
```bash
yolo-tiling --source tests/semantic --target tests/semantic_tiled --annotation_type semantic_segmentation --input_ext .png --output_ext .png
```

5. Custom compression percentage for JPEG/JPG output formats:
```bash
yolo-tiling --source tests/detection --target tests/detection_tiled --output_ext .jpg --compression 85

yolo-tiling --source tests/detection --target tests/detection_tiled --output_ext .png --compression 90

yolo-tiling --source tests/detection --target tests/detection_tiled --output_ext .tif --compression 95
```

### Memory Efficiency

The `tile_image` method now uses rasterio's Window to read and process image tiles directly from the disk, instead of loading the entire image into memory. This makes the tiling process more memory efficient, especially for large images.

---
## Disclaimer

This repository is a scientific product and is not official communication of the National
Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA
GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its
use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from
the use of this GitHub project will be governed by all applicable Federal law. Any reference to
specific commercial products, processes, or services by service mark, trademark, manufacturer, or
otherwise, does not constitute or imply their endorsement, recommendation or favoring by the
Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC
bureau, shall not be used in any manner to imply endorsement of any commercial product or activity
by DOC or the United States Government.


## License

Software code created by U.S. Government employees is not subject to copyright in the United States
(17 U.S.C. §105). The United States/Department of Commerce reserve all rights to seek and obtain
copyright protection in countries other than the United States for Software authored in its
entirety by the Department of Commerce. To this end, the Department of Commerce hereby grants to
Recipient a royalty-free, nonexclusive license to use, copy, and create derivative works of the
Software outside of the United States.
