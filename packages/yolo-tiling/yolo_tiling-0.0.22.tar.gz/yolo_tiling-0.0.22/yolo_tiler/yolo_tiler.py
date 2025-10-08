import os
import logging
import math
import yaml
import random
import shutil
import warnings
from tqdm import tqdm

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Union, Generator, Callable

import cv2
import numpy as np
import pandas as pd
import rasterio

import shapely
import matplotlib.pyplot as plt

import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
from rasterio.windows import Window
from shapely.geometry import Polygon, MultiPolygon

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


# ----------------------------------------------------------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class TileConfig:
    def __init__(self,
                 slice_wh: Union[int, Tuple[int, int]],
                 overlap_wh: Union[int, Tuple[float, float]] = 0,
                 annotation_type: str = "object_detection",
                 input_ext: str = ".png",
                 output_ext: Optional[str] = None,
                 densify_factor: float = 0.5,
                 smoothing_tolerance: float = 0.1,
                 train_ratio: float = 0.8,
                 valid_ratio: float = 0.1,
                 test_ratio: float = 0.1,
                 margins: Union[float, Tuple[float, float, float, float]] = 0.0,
                 include_negative_samples: bool = True,
                 copy_source_data: bool = False,
                 compression: int = 90):
        """
        Args:
            slice_wh: Size of each slice (width, height)
            overlap_wh: Overlap between slices as a fraction of slice size (width, height)
            annotation_type: Type of annotation format (object_detection, instance_segmentation, image_classification)
            input_ext: Input image extension
            output_ext: Output image extension (defaults to input_ext)
            densify_factor: Factor to densify lines for smoothing
            smoothing_tolerance: Tolerance for polygon simplification
            train_ratio: Ratio of train set
            valid_ratio: Ratio of valid set
            test_ratio: Ratio of test set
            margins: Margins to exclude from tiling (left, top, right, bottom)
            include_negative_samples: Include tiles without annotations
            copy_source_data: Copy original source images to target directory
            compression: Compression percentage for different output formats (0-100)
        """
        self.slice_wh = slice_wh if isinstance(slice_wh, tuple) else (slice_wh, slice_wh)
        self.overlap_wh = overlap_wh
        self.annotation_type = annotation_type
        self.input_ext = input_ext
        self.output_ext = output_ext if output_ext is not None else input_ext
        self.densify_factor = densify_factor
        self.smoothing_tolerance = smoothing_tolerance
        self.train_ratio = train_ratio
        self.valid_ratio = valid_ratio
        self.test_ratio = test_ratio
        self.include_negative_samples = include_negative_samples
        self.copy_source_data = copy_source_data
        self.compression = compression
        
        # Validate annoation type
        valid_types = ["object_detection", "instance_segmentation", "image_classification", "semantic_segmentation"]
        if self.annotation_type not in valid_types:
            raise ValueError(f"ERROR: Invalid annotation type: {self.annotation_type}\n\
                              Must be one of {valid_types}")

        # Handle margins
        if isinstance(margins, (int, float)):
            self.margins = (margins, margins, margins, margins)
        else:
            self.margins = margins

        self._validate()

    def _validate(self):
        # Add to existing validation
        if isinstance(self.margins[0], float):
            if not all(0 <= m <= 1 for m in self.margins):
                raise ValueError("Float margins must be between 0 and 1")
        elif isinstance(self.margins[0], int):
            if not all(m >= 0 for m in self.margins):
                raise ValueError("Integer margins must be non-negative")
        else:
            raise ValueError("Margins must be int or float")

    def get_effective_area(self, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
        """Calculate the effective area after applying margins"""
        left, top, right, bottom = self.margins

        if isinstance(left, float):
            x_min = int(image_width * left)
            y_min = int(image_height * top)
            x_max = int(image_width * (1 - right))
            y_max = int(image_height * (1 - bottom))
        else:
            x_min = left
            y_min = top
            x_max = image_width - right
            y_max = image_height - bottom

        return x_min, y_min, x_max, y_max


@dataclass
class TileProgress:
    """Data class to track tiling progress"""
    current_set_name: str = ""
    current_image_name: str = ""
    current_image_idx: int = 0
    total_images: int = 0
    current_tile_idx: int = 0  
    total_tiles: int = 0  


class YoloTiler:
    """
    A class to tile YOLO dataset images and their corresponding annotations.
    Supports both object detection and instance segmentation formats.
    """

    def __init__(self,
                 source: Union[str, Path],
                 target: Union[str, Path],
                 config: TileConfig,
                 num_viz_samples: int = 0,
                 show_processing_status: bool = True,
                 progress_callback: Optional[Callable[[TileProgress], None]] = None):
        """
        Initialize YoloTiler with source and target directories.

        Args:
            source: Source directory containing YOLO dataset
            target: Target directory for sliced dataset
            config: TileConfig object containing tiling parameters
            num_viz_samples: Number of random samples to visualize from train set
            show_processing_status: Whether to show processing status
            progress_callback: Optional callback function to report progress
        """
        # Add show_process_status parameter and initialize progress bars dict
        self.show_process_status = show_processing_status
        self._progress_bars = {}
        
        try:
            self.source = Path(source)
            self.target = Path(target)
        except:
            raise ValueError("Source and target must be valid paths")
        
        self.config = config
        self.num_viz_samples = num_viz_samples
        
        # Set up the progress callback based on parameters
        if progress_callback is not None:
            self.progress_callback = progress_callback
        elif show_processing_status:
            self.progress_callback = self._tqdm_callback
        else:
            self.progress_callback = None
        
        self.logger = self._setup_logger()
        
        # Get the annotation type
        self.annotation_type = self.config.annotation_type
        
        if self.annotation_type != "image_classification":
            self.subfolders = ['train/', 'valid/', 'test/']
        else:
            self.subfolders = ['train/', 'val/', 'test/']

        # Create rendered directory if visualization is requested
        if self.num_viz_samples > 0:
            self.render_dir = self.target / 'rendered'
            self.render_dir.mkdir(parents=True, exist_ok=True)
            
    def _tqdm_callback(self, progress: TileProgress):
        """Internal callback function that uses tqdm for progress tracking
        
        Args:
            progress: TileProgress object containing current progress
            
        """
        # Initialize or get progress bar for current set
        if progress.current_set_name not in self._progress_bars:
            # Determine if we're tracking tiles or images
            if progress.total_tiles > 0:
                total = progress.total_tiles
                desc = f"{progress.current_set_name}: Tile"
                unit = 'tiles'
            else:
                total = progress.total_images
                desc = f"{progress.current_set_name}: Image"
                unit = 'images'
                
            self._progress_bars[progress.current_set_name] = tqdm(
                total=total,
                desc=desc,
                unit=unit
            )
        
        # Update progress based on available information
        if progress.total_tiles > 0:
            self._progress_bars[progress.current_set_name].n = progress.current_tile_idx
        else:
            self._progress_bars[progress.current_set_name].n = progress.current_image_idx
            
        self._progress_bars[progress.current_set_name].refresh()
        
        # Close and cleanup if task is complete
        is_complete = (progress.total_tiles > 0 and progress.current_tile_idx >= progress.total_tiles) or \
                      (progress.total_tiles == 0 and progress.current_image_idx >= progress.total_images)
                    
        if is_complete:
            self._progress_bars[progress.current_set_name].close()
            del self._progress_bars[progress.current_set_name]

    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the tiler"""
        logger = logging.getLogger('YoloTiler')
        logger.setLevel(logging.INFO)
        return logger

    def _create_target_folder(self, target: Path) -> None:
        """Create target folder if it does not exist"""
        
        if self.annotation_type == "image_classification":
            # Get class categories from source folders
            class_cats = set()
            for subfolder in self.subfolders:
                class_cats.update([d.name for d in (self.source / subfolder).iterdir() if d.is_dir()])
            # Unique and sorted class categories
            class_cats = sorted(list(class_cats))
            
        for subfolder in self.subfolders:
            if self.annotation_type == "image_classification":
                for class_cat in class_cats:
                    # tiled/subfolder/class_cat/
                    (target / subfolder / class_cat).mkdir(parents=True, exist_ok=True)
            else:
                # tiled/subfolder/images and tiled/subfolder/labels
                (target / subfolder / "images").mkdir(parents=True, exist_ok=True)
                (target / subfolder / "labels").mkdir(parents=True, exist_ok=True)

    def _validate_yolo_structure(self, folder: Path) -> None:
        """
        Validate YOLO dataset folder structure.

        Args:
            folder: Soruce path to check for YOLO structure

        Raises:
            ValueError: If required folders {train, val/id, test} are missing
        """
        # Subfolder contains {train, val/id, test}
        for subfolder in self.subfolders:
            
            if self.annotation_type == "image_classification":
                # Check for class folders for image classification
                if not (folder / subfolder).exists():
                    raise ValueError(f"Required folder {folder / subfolder} does not exist")
                else:
                    class_folders = [sub.name for sub in (folder / subfolder).iterdir() if sub.is_dir()]
                    if not class_folders:
                        raise ValueError(f"No class folders found in {folder / subfolder}")
            else:
                # Check for images and labels folders for detection and segmentation tasks
                if not (folder / subfolder / 'images').exists():
                    raise ValueError(f"Required folder {folder / subfolder / 'images'} does not exist")
                if not (folder / subfolder / 'labels').exists():
                    raise ValueError(f"Required folder {folder / subfolder / 'labels'} does not exist")

    def _count_total_tiles(self, image_size: Tuple[int, int]) -> int:
        """Count total number of tiles for an image"""
        img_w, img_h = image_size
        slice_w, slice_h = self.config.slice_wh
        overlap_w, overlap_h = self.config.overlap_wh

        # Calculate effective step sizes
        step_w = self._calculate_step_size(slice_w, overlap_w)
        step_h = self._calculate_step_size(slice_h, overlap_h)

        # Generate tile positions using numpy for faster calculations
        x_coords = self._generate_tile_positions(img_w, step_w)
        y_coords = self._generate_tile_positions(img_h, step_h)

        return len(x_coords) * len(y_coords)

    def _calculate_step_size(self, slice_size: int, overlap: Union[int, float]) -> int:
        """Calculate effective step size for tiling."""
        if isinstance(overlap, float):
            overlap = int(slice_size * overlap)
        return slice_size - overlap

    def _calculate_num_tiles(self, img_size: int, step_size: int) -> int:
        """Calculate number of tiles in one dimension."""
        return math.ceil((img_size - step_size) / step_size)

    def _generate_tile_positions(self, img_size: int, step_size: int) -> np.ndarray:
        """Generate tile positions using numpy for faster calculations."""
        return np.arange(0, img_size, step_size)

    def _calculate_tile_positions(self,
                                  image_size: Tuple[int, int]) -> Generator[Tuple[int, int, int, int], None, None]:
        """
        Calculate tile positions with overlap, respecting margins.

        Args:
            image_size: (width, height) of the image after margins applied

        Yields:
            Tuples of (x1, y1, x2, y2) for each tile within effective area
        """
        img_w, img_h = image_size
        slice_w, slice_h = self.config.slice_wh
        overlap_w, overlap_h = self.config.overlap_wh

        # Calculate effective step sizes
        step_w = self._calculate_step_size(slice_w, overlap_w)
        step_h = self._calculate_step_size(slice_h, overlap_h)

        # Generate tile positions using numpy for faster calculations
        # Use effective dimensions (after margins)
        x_coords = self._generate_tile_positions(img_w, step_w)
        y_coords = self._generate_tile_positions(img_h, step_h)

        for y1 in y_coords:
            for x1 in x_coords:
                x2 = min(x1 + slice_w, img_w)
                y2 = min(y1 + slice_h, img_h)

                # Handle edge cases by shifting tiles
                if x2 == img_w and x2 != x1 + slice_w:
                    x1 = max(0, x2 - slice_w)
                if y2 == img_h and y2 != y1 + slice_h:
                    y1 = max(0, y2 - slice_h)

                yield x1, y1, x2, y2

    def _densify_line(self, coords: List[Tuple[float, float]], factor: float) -> List[Tuple[float, float]]:
        """Add points along line segments to increase resolution"""
        result = []
        for i in range(len(coords) - 1):
            p1, p2 = coords[i], coords[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            segment_length = math.sqrt(dx * dx + dy * dy)
            steps = int(segment_length / factor)

            if steps > 1:
                for step in range(steps):
                    t = step / steps
                    x = p1[0] + t * dx
                    y = p1[1] + t * dy
                    result.append((x, y))
            else:
                result.append(p1)

        result.append(coords[-1])
        return result

    def _process_polygon(self, poly: Polygon) -> List[List[Tuple[float, float]]]:
        # Calculate densification distance based on polygon size
        perimeter = poly.length
        dense_distance = perimeter * self.config.densify_factor

        # Process exterior ring
        coords = list(poly.exterior.coords)[:-1]
        dense_coords = self._densify_line(coords, dense_distance)

        # Create simplified version for smoothing
        dense_poly = Polygon(dense_coords)
        smoothed = dense_poly.simplify(self.config.smoothing_tolerance, preserve_topology=True)

        result = [list(smoothed.exterior.coords)[:-1]]

        # Process interior rings (holes)
        for interior in poly.interiors:
            coords = list(interior.coords)[:-1]
            dense_coords = self._densify_line(coords, dense_distance)
            hole_poly = Polygon(dense_coords)
            smoothed_hole = hole_poly.simplify(self.config.smoothing_tolerance, preserve_topology=True)
            result.append(list(smoothed_hole.exterior.coords)[:-1])

        return result

    def _process_intersection(self, intersection: Union[Polygon, MultiPolygon]) -> List[List[Tuple[float, float]]]:
        """Process intersection geometry with proper polygon closure."""
        from shapely.geometry import LineString, Polygon, MultiPolygon
        
        def process_single_polygon(geom) -> List[List[Tuple[float, float]]]:
            # Handle LineString case
            if isinstance(geom, LineString):
                # Convert LineString to a very thin polygon
                buffer_dist = 1e-10
                geom = geom.buffer(buffer_dist)
            
            if not isinstance(geom, Polygon):
                return []
                
            # Ensure proper closure of exterior ring
            exterior_coords = list(geom.exterior.coords)
            if exterior_coords[0] != exterior_coords[-1]:
                exterior_coords.append(exterior_coords[0])

            result = [exterior_coords[:-1]]  # Remove duplicate closing point

            # Process holes with proper closure
            for interior in geom.interiors:
                interior_coords = list(interior.coords)
                if interior_coords[0] != interior_coords[-1]:
                    interior_coords.append(interior_coords[0])
                result.append(interior_coords[:-1])

            return result

        if isinstance(intersection, MultiPolygon):
            all_coords = []
            for poly in intersection.geoms:
                all_coords.extend(process_single_polygon(poly))
            return all_coords
        else:
            return process_single_polygon(intersection)

            if isinstance(intersection, Polygon):
                return process_single_polygon(intersection)
            else:  # MultiPolygon
                all_coords = []
                for poly in intersection.geoms:
                    all_coords.extend(process_single_polygon(poly))
                return all_coords

    def _normalize_coordinates(self, 
                               coord_lists: List[List[Tuple[float, float]]],
                               tile_bounds: Tuple[int, int, int, int]) -> str:
        """Normalize coordinates with proper polygon closure."""
        x1, y1, x2, y2 = tile_bounds
        tile_width = x2 - x1
        tile_height = y2 - y1

        normalized_parts = []
        for coords in coord_lists:
            # Ensure proper closure
            if coords[0] != coords[-1]:
                coords = coords + [coords[0]]

            normalized = []
            for x, y in coords:
                norm_x = max(0, min(1, (x - x1) / tile_width))  # Clamp to [0,1]
                norm_y = max(0, min(1, (y - y1) / tile_height))
                normalized.append(f"{norm_x:.6f} {norm_y:.6f}")
            normalized_parts.append(normalized)

        return " ".join([" ".join(part) for part in normalized_parts])

    def _save_labels(self, labels: List, path: Path, is_segmentation: bool) -> None:
        """
        Save labels to file in appropriate format. Image classification ignored.

        Args:
            labels: List of label data
            path: Path to save labels
            is_segmentation: Whether using segmentation format
        """
        if is_segmentation:
            with open(path, 'w') as f:
                for label_class, points in labels:
                    f.write(f"{label_class} {points}\n")
                    
        else:  # Object detection
            df = pd.DataFrame(labels, columns=['class', 'x1', 'y1', 'w', 'h'])
            df.to_csv(path, sep=' ', index=False, header=False, float_format='%.6f')

    def _save_mask(self, mask: np.ndarray, path: Path) -> None:
        """
        Save mask to PNG file for semantic segmentation.

        Args:
            mask: Numpy array of mask data
            path: Path to save mask
        """
        # Ensure mask is uint8
        mask = mask.astype(np.uint8)
        
        # Save as PNG
        from PIL import Image
        img = Image.fromarray(mask, mode='L')  # 'L' for grayscale
        img.save(path)

    def tile_image(self, 
                   image_path: Path, 
                   label_path: Union[Path, str],  # Path to labels.txt, or class name
                   folder: str, 
                   current_image_idx: int, 
                   total_images: int) -> None:
        """
        Tile an image and its corresponding labels, properly handling margins.
        """
        def clean_geometry(geom: Polygon) -> Polygon:
            """Clean potentially invalid geometry"""
            if not geom.is_valid:
                # Apply small buffer to fix self-intersections
                cleaned = geom.buffer(0)
                if cleaned.is_valid:
                    return cleaned
                # Try more aggressive cleaning if needed
                return geom.buffer(1e-10).buffer(-1e-10)
            return geom

        # Read image and labels
        with rasterio.open(image_path) as src:
            width, height = src.width, src.height

            # Get effective area (area after margins applied)
            x_min, y_min, x_max, y_max = self.config.get_effective_area(width, height)
            effective_width = x_max - x_min
            effective_height = y_max - y_min

            # Create polygon representing effective area (excludes margins)
            effective_area = Polygon([
                (x_min, y_min),
                (x_max, y_min),
                (x_max, y_max),
                (x_min, y_max)
            ])

            # Calculate total tiles for progress tracking
            total_tiles = self._count_total_tiles((effective_width, effective_height))
            
            # Read labels based on annotation type
            if self.annotation_type == "image_classification":
                # Image classification (unnecessary for tiling)
                lines = []
                boxes = []
                mask_data = None
            elif self.annotation_type == "semantic_segmentation":
                # Read PNG mask for semantic segmentation
                try:
                    with rasterio.open(label_path) as mask_src:
                        mask_data = mask_src.read(1)  # Read single channel mask
                    lines = []
                    boxes = []
                except Exception as e:
                    raise ValueError(f"Failed to read mask file {label_path}: {e}")
            else:
                # Object detection and instance segmentation - read text file
                try:
                    f = open(label_path)
                    lines = f.readlines()
                    f.close()
                    
                    # Boxes or polygons
                    boxes = []
                    mask_data = None
                    
                except Exception as e:
                    raise ValueError(f"Failed to read label file {label_path}: {e}")
            
            # Process each line
            for line in lines:
                try:
                    parts = line.strip().split()
                    class_id = int(parts[0])

                    if self.config.annotation_type == "object_detection":
                        # Parse normalized coordinates
                        x_center_norm = float(parts[1])
                        y_center_norm = float(parts[2])
                        box_w_norm = float(parts[3])
                        box_h_norm = float(parts[4])

                        # Convert to absolute coordinates
                        x_center = x_center_norm * width
                        y_center = y_center_norm * height
                        box_w = box_w_norm * width
                        box_h = box_h_norm * height

                        x1 = x_center - box_w / 2
                        y1 = y_center - box_h / 2
                        x2 = x_center + box_w / 2
                        y2 = y_center + box_h / 2
                        box_polygon = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

                        # Only include if box intersects with effective area
                        if box_polygon.intersects(effective_area):
                            # Clip box to effective area
                            clipped_box = box_polygon.intersection(effective_area)
                            if not clipped_box.is_empty:
                                boxes.append((class_id, clipped_box))
            
                    else:  # Instance segmentation
                        points = []
                        for i in range(1, len(parts), 2):
                            x_norm = float(parts[i])
                            y_norm = float(parts[i + 1])
                            x = x_norm * width
                            y = y_norm * height
                            points.append((x, y))

                        try:
                            polygon = Polygon(points)
                            # Clean and validate polygon
                            polygon = clean_geometry(polygon)
                            
                            if polygon.is_valid and polygon.intersects(effective_area):
                                # Safely perform intersection
                                try:
                                    clipped_polygon = polygon.intersection(effective_area)
                                    if not clipped_polygon.is_empty:
                                        boxes.append((class_id, clipped_polygon))
                                        
                                except (shapely.errors.GEOSException, ValueError) as e:
                                    print(f"Warning: Failed to process polygon in {image_path.name}: {e}")
                                    continue
                                
                        except Exception as e:
                            print(f"Warning: Invalid polygon in {image_path.name}: {e}")
                            continue
                        
                except Exception as e:
                    print(f"Warning: Failed to process line in {label_path}: {e}")
                    continue

            # Calculate tile positions
            effective_areas = self._calculate_tile_positions((effective_width, effective_height))
            
            # Process each tile within effective area
            for tile_idx, (x1, y1, x2, y2) in enumerate(effective_areas):
                # Convert tile coordinates to absolute image coordinates
                abs_x1 = x1 + x_min
                abs_y1 = y1 + y_min
                abs_x2 = x2 + x_min
                abs_y2 = y2 + y_min

                if self.progress_callback:
                    progress = TileProgress(
                        current_tile_idx=tile_idx + 1,
                        total_tiles=total_tiles,
                        current_set_name=folder.rstrip('/'),
                        current_image_name=image_path.name,
                        current_image_idx=current_image_idx,
                        total_images=total_images
                    )
                    self.progress_callback(progress)

                # Extract tile data
                window = Window(abs_x1, abs_y1, abs_x2 - abs_x1, abs_y2 - abs_y1)
                tile_data = src.read(window=window)

                # Create polygon for current tile
                tile_polygon = Polygon([
                    (abs_x1, abs_y1),
                    (abs_x2, abs_y1),
                    (abs_x2, abs_y2),
                    (abs_x1, abs_y2)
                ])

                tile_labels = []

                if self.annotation_type == "semantic_segmentation":
                    # Crop the mask to the tile area
                    tile_mask = mask_data[abs_y1:abs_y2, abs_x1:abs_x2]
                    tile_labels = tile_mask
                else:
                    # Process annotations for this tile (boxes or polygons)
                    for box_class, box_polygon in boxes:
                        # Deal with intersections if they occur
                        # This is necessary for cases where a box / polygon
                        # is split across tiles
                        if tile_polygon.intersects(box_polygon):
                            intersection = tile_polygon.intersection(box_polygon)

                            if self.config.annotation_type == "object_detection":
                                # Handle object detection
                                bbox = intersection.envelope
                                center = bbox.centroid
                                bbox_coords = bbox.exterior.coords.xy

                                # Normalize relative to tile dimensions
                                tile_width = abs_x2 - abs_x1
                                tile_height = abs_y2 - abs_y1

                                new_width = (max(bbox_coords[0]) - min(bbox_coords[0])) / tile_width
                                new_height = (max(bbox_coords[1]) - min(bbox_coords[1])) / tile_height
                                new_x = (center.x - abs_x1) / tile_width
                                new_y = (center.y - abs_y1) / tile_height

                                tile_labels.append([box_class, new_x, new_y, new_width, new_height])
                            else:
                                # Handle instance segmentation
                                coord_lists = self._process_intersection(intersection)
                                normalized = self._normalize_coordinates(coord_lists, (abs_x1, abs_y1, abs_x2, abs_y2))
                                tile_labels.append([box_class, normalized])

                # Save tile image and labels if include_negative_samples is True or there are labels
                if self.config.include_negative_samples or tile_labels:
                    # Calculate width and height for the new naming convention
                    tile_width = abs_x2 - abs_x1
                    tile_height = abs_y2 - abs_y1
                    tile_coords = (abs_x1, abs_y1, tile_width, tile_height)
                    self._save_tile(tile_data, image_path, tile_coords, tile_labels, folder)

    def _save_tile_image(self, tile_data: np.ndarray, image_path: Path, suffix: str, folder: str) -> None:
        """
        Save a tile image to the appropriate directory.
    
        Args:
            tile_data: Numpy array of tile image
            image_path: Path to original image
            suffix: Suffix for the tile filename
            folder: Subfolder name (train, val/id, test)
        """
        # Set the save directory based on annotation type
        if self.annotation_type == "image_classification":
            class_name = image_path.parent.name
            save_dir = self.target / folder / class_name
            image_path_out = save_dir / image_path.name.replace(self.config.input_ext, suffix)
        else:
            save_dir = self.target / folder / "images"
            image_path_out = save_dir / image_path.name.replace(self.config.input_ext, suffix)
    
        # Make sure the directory exists
        save_dir.mkdir(parents=True, exist_ok=True)
    
        # Select appropriate driver and options based on extension
        output_ext = self.config.output_ext.lower()
        
        if output_ext in ['.jpg', '.jpeg']:
            driver = 'JPEG'
            options = {'quality': self.config.compression}
        elif output_ext == '.png':
            driver = 'PNG'
            # PNG compression (0-9); convert from JPEG scale
            png_compression = min(9, max(0, int(self.config.compression / 10)))
            options = {'zlevel': png_compression}
        elif output_ext == '.bmp':
            driver = 'BMP'
            options = {}  # BMP doesn't support compression
        elif output_ext in ['.tif', '.tiff']:
            driver = 'GTiff'
            # Map JPEG quality to appropriate TIFF compression
            if self.config.compression >= 90:
                # Use lossless LZW for high quality
                options = {'compress': 'lzw'}
            elif self.config.compression >= 75:
                # Use lossless DEFLATE for medium-high quality
                options = {'compress': 'deflate', 'zlevel': 6}
            else:
                # Use JPEG compression for lower quality settings
                # Scale the JPEG quality to something reasonable for TIFF
                tiff_jpeg_quality = max(50, self.config.compression)
                options = {'compress': 'jpeg', 'jpeg_quality': tiff_jpeg_quality}
        else:
            # Default to GTiff for unknown formats
            driver = 'GTiff'
            options = {'compress': 'lzw'}  # Safe default
    
        with rasterio.open(
            image_path_out,
            'w',
            driver=driver,
            height=tile_data.shape[1],
            width=tile_data.shape[2],
            count=tile_data.shape[0],
            dtype=tile_data.dtype,
            **options
        ) as dst:
            dst.write(tile_data)

    def _save_tile_labels(self, labels: Optional[List], image_path: Path, suffix: str, folder: str) -> None:
        """
        Save tile labels to the appropriate directory.

        Args:
            labels: List of labels for the tile
            image_path: Path to original image
            suffix: Suffix for the tile filename
            folder: Subfolder name (train, valid, test)
        """
        # Save the labels in the appropriate directory
        if self.annotation_type == "semantic_segmentation":
            # For semantic segmentation, always use PNG format for masks
            # Extract coordinates from suffix and create PNG suffix
            parts = suffix.split('_')
            if len(parts) >= 5:
                x1, y1, width, height = parts[-4], parts[-3], parts[-2], parts[-1].split('.')[0]
                mask_suffix = f'_{x1}_{y1}_{width}_{height}.png'
            else:
                # Fallback if parsing fails
                mask_suffix = suffix.replace(self.config.output_ext, '.png')
            label_path = self.target / folder / "labels" / image_path.name.replace(self.config.input_ext, mask_suffix)
            # labels is a numpy array for semantic segmentation
            self._save_mask(labels, label_path)
        elif self.annotation_type != "image_classification":
            label_path = self.target / folder / "labels" / image_path.name.replace(self.config.input_ext, suffix)
            label_path = label_path.with_suffix('.txt')
            self._save_labels(labels, 
                              label_path, 
                              is_segmentation=self.annotation_type == "instance_segmentation")

    def _save_tile(self,
                   tile_data: np.ndarray,
                   original_path: Path,
                   tile_coords: Tuple[int, int, int, int],
                   labels: Optional[List],
                   folder: str) -> None:
        """
        Save a tile image and its labels.

        Args:
            tile_data: Numpy array of tile image
            original_path: Path to original image
            tile_coords: Tuple of (x1, y1, width, height) for the tile
            labels: List of labels for the tile
            folder: Subfolder name (train, valid, test)
        """
        # Create suffix with coordinates: _x_y_width_height
        x1, y1, width, height = tile_coords
        suffix = f'_{x1}_{y1}_{width}_{height}{self.config.output_ext}'
        
        self._save_tile_image(tile_data, original_path, suffix, folder)
        
        # Only save label files for detection and segmentation tasks
        if self.annotation_type != "image_classification":
            self._save_tile_labels(labels, original_path, suffix, folder)

    def split_data(self) -> None:
        """
        Split train data into train, valid, and test sets using specified ratios.
        Files are moved from train to valid/test directories.
        """
        if self.annotation_type == "image_classification":
            self._split_classification_data()
        else:
            self._split_detection_data()

    def _split_detection_data(self) -> None:
        """Split data for object detection and instance segmentation"""
        train_images = list((self.target / 'train' / 'images').glob(f'*{self.config.output_ext}'))
        train_labels = list((self.target / 'train' / 'labels').glob('*.txt'))

        if not train_images or not train_labels:
            self.logger.warning("No train data found to split")
            return

        # Create a dictionary mapping from image stem to image path
        image_dict = {img_path.stem: img_path for img_path in train_images}
        
        # Create a dictionary mapping from label stem to label path
        label_dict = {lbl_path.stem: lbl_path for lbl_path in train_labels}
        
        # Create properly matched image-label pairs
        combined = []
        for stem, img_path in image_dict.items():
            if stem in label_dict:
                combined.append((img_path, label_dict[stem]))
            else:
                self.logger.warning(f"No matching label found for image: {img_path.name}, skipping")
        
        if not combined:
            self.logger.warning("No matching image-label pairs found to split")
            return
                
        random.shuffle(combined)

        num_train = int(len(combined) * self.config.train_ratio)
        num_valid = int(len(combined) * self.config.valid_ratio)

        valid_set = combined[num_train:num_train + num_valid]
        test_set = combined[num_train + num_valid:]
        
        # Move files to valid folder
        for image_idx, (image_path, label_path) in enumerate(valid_set):
            self._move_split_data(image_path, label_path, 'valid')

            if self.progress_callback:
                progress = TileProgress(
                    current_tile_idx=0,
                    total_tiles=0,
                    current_set_name='valid',
                    current_image_name=image_path.name,
                    current_image_idx=image_idx + 1,
                    total_images=len(valid_set)
                )
                self.progress_callback(progress)

        # Move files to test folder
        for image_idx, (image_path, label_path) in enumerate(test_set):
            self._move_split_data(image_path, label_path, 'test')
            if self.progress_callback:
                progress = TileProgress(
                    current_tile_idx=0,
                    total_tiles=0,
                    current_set_name='test',
                    current_image_name=image_path.name,
                    current_image_idx=image_idx + 1,
                    total_images=len(test_set)
                )
                self.progress_callback(progress)

    def _split_classification_data(self) -> None:
        """Split data for image classification"""
        # Get all class directories in train folder
        train_class_dirs = [d for d in (self.target / 'train').iterdir() if d.is_dir()]
        
        if not train_class_dirs:
            self.logger.warning("No class directories found in train folder")
            return
        
        # Process each class to maintain class distribution
        for class_dir in train_class_dirs:
            class_name = class_dir.name
            images = list(class_dir.glob(f'*{self.config.output_ext}'))
            
            if not images:
                continue
                
            # Shuffle images for this class
            random.shuffle(images)
            
            num_train = int(len(images) * self.config.train_ratio)
            num_valid = int(len(images) * self.config.valid_ratio)
            
            valid_set = images[num_train:num_train + num_valid]
            test_set = images[num_train + num_valid:]
            
            # Move files to val folder for this class (YOLO uses 'val' not 'valid' for classification)
            for image_idx, image_path in enumerate(valid_set):
                self._move_classification_image(image_path, class_name, 'val')
                
                if self.progress_callback:
                    progress = TileProgress(
                        current_tile_idx=0,
                        total_tiles=0,
                        current_set_name='val',
                        current_image_name=image_path.name,
                        current_image_idx=image_idx + 1,
                        total_images=len(valid_set)
                    )
                    self.progress_callback(progress)
            
            # Move files to test folder for this class
            for image_idx, image_path in enumerate(test_set):
                self._move_classification_image(image_path, class_name, 'test')
                
                if self.progress_callback:
                    progress = TileProgress(
                        current_tile_idx=0,
                        total_tiles=0,
                        current_set_name='test',
                        current_image_name=image_path.name,
                        current_image_idx=image_idx + 1,
                        total_images=len(test_set)
                    )
                    self.progress_callback(progress)

    def _move_classification_image(self, image_path: Path, class_name: str, folder: str) -> None:
        """
        Move classification image to appropriate class folder.
        
        Args:
            image_path: Path to image file
            class_name: Class name (folder name)
            folder: Target folder (val or test)
        """
        # Ensure target class directory exists
        target_class_dir = self.target / folder / class_name
        target_class_dir.mkdir(parents=True, exist_ok=True)
        
        # Move the image
        target_image = target_class_dir / image_path.name
        image_path.rename(target_image)

    def _move_split_data(self, image_path: Path, label_path: Path, folder: str) -> None:
        """
        Move split data to the appropriate folder.

        Args:
            image_path: Path to image file
            label_path: Path to label file
            folder: Subfolder name (valid or test)
        """
        target_image = self.target / folder / "images" / image_path.name
        target_label = self.target / folder / "labels" / label_path.name

        image_path.rename(target_image)
        label_path.rename(target_label)

    def _validate_directories(self) -> None:
        """Validate source and target directories."""
        self._validate_yolo_structure(self.source)
        self._create_target_folder(self.target)

    def _process_subfolder(self, subfolder: str) -> None:
        """Process images and labels in a subfolder."""
        
        if self.annotation_type == 'image_classification':
            image_paths = list((self.source / subfolder).glob(f'**/*{self.config.input_ext}'))
            label_paths = [image_path.parent.name for image_path in image_paths]
        else:
            # Detection and segmentation tasks (get the images and labels in subfolders)
            image_paths = list((self.source / subfolder / 'images').glob(f'*{self.config.input_ext}'))
            
            if self.annotation_type == "semantic_segmentation":
                label_paths = list((self.source / subfolder / 'labels').glob('*.png'))
            else:
                label_paths = list((self.source / subfolder / 'labels').glob('*.txt'))
            
            # Sort paths to ensure consistent ordering
            image_paths.sort()
            label_paths.sort()
            
            # For detection/segmentation, create a mapping of stem to label path
            # This ensures correct matching regardless of directory listing order
            label_dict = {path.stem: path for path in label_paths}

        # Log the number of images, labels found
        self.logger.info(f'Found {len(image_paths)} images in {subfolder} directory')
        self.logger.info(f'Found {len(label_paths)} label files in {subfolder} directory')

        # Check for missing files
        if not image_paths:
            self.logger.warning(f"No images found in {subfolder} directory, skipping")
            return
        if len(image_paths) != len(label_paths):
            self.logger.error(f"Number of images and labels do not match in {subfolder} directory, skipping")
            return

        total_images = len(image_paths)

        # Process each image
        for current_image_idx, image_path in enumerate(image_paths):
            if self.annotation_type != "image_classification":
                # Look up the matching label path based on stem instead of position
                label_path = label_dict.get(image_path.stem)
                if label_path is None:
                    self.logger.warning(f"No matching label found for image: {image_path.name}, skipping")
                    continue
            else:
                # For classification, the label is still the parent folder name
                label_path = image_path.parent.name
            
            self.logger.info(f'Processing {image_path}')
            self.tile_image(image_path, label_path, subfolder, current_image_idx + 1, total_images)

    def _check_and_split_data(self) -> None:
        """Check if valid or test folders are empty and split data if necessary."""
        if self.annotation_type == "image_classification":
            # Check if val or test folders are empty
            val_empty = not any((self.target / 'val').glob(f'**/*{self.config.output_ext}'))
            test_empty = not any((self.target / 'test').glob(f'**/*{self.config.output_ext}'))
            
            if val_empty or test_empty:
                self.split_data()
                self.logger.info('Split train data into val and test sets')
        else:
            # For detection/segmentation
            valid_images = list((self.target / 'valid' / 'images').glob(f'*{self.config.output_ext}'))
            test_images = list((self.target / 'test' / 'images').glob(f'*{self.config.output_ext}'))

            if not valid_images or not test_images:
                self.split_data()
                self.logger.info('Split train data into valid and test sets')

    def _copy_and_update_data_yaml(self) -> None:
        """Copy and update data.yaml with new paths for tiled dataset."""
        if self.annotation_type != "image_classification":
            data_yaml = self.source / 'data.yaml'
            if data_yaml.exists():
                
                # Read YAML as structured data
                with open(data_yaml, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Update paths
                if 'train' in data:
                    data['train'] = str(self.target / 'train' / 'images')
                if 'val' in data:
                    data['val'] = str(self.target / 'valid' / 'images')
                if 'valid' in data:
                    data['valid'] = str(self.target / 'valid' / 'images')
                if 'test' in data:
                    data['test'] = str(self.target / 'test' / 'images')
                if 'path' in data:
                    data['path'] = str(self.target)
                
                # Write updated YAML
                with open(self.target / 'data.yaml', 'w') as f:
                    yaml.dump(data, f, sort_keys=False)
            else:
                self.logger.warning('data.yaml not found in source directory')
                
    def _copy_source_data(self) -> None:
        """Copy original source data to the target directory."""        
        self.logger.info('Copying original source data to target directory...')
        
        for subfolder in self.subfolders:
            if self.annotation_type == "image_classification":
                # For image classification, copy all class directories
                source_dir = self.source / subfolder
                if source_dir.exists():
                    # Get all class directories
                    class_dirs = [d for d in source_dir.iterdir() if d.is_dir()]
                    
                    for class_dir in class_dirs:
                        class_name = class_dir.name
                        target_class_dir = self.target / f"{subfolder.rstrip('/')}" / class_name
                        target_class_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Copy all images for this class
                        for img_path in class_dir.glob(f"*{self.config.input_ext}"):
                            shutil.copy2(img_path, target_class_dir / img_path.name)
            else:
                # For detection and segmentation tasks
                source_img_dir = self.source / subfolder / "images"
                source_lbl_dir = self.source / subfolder / "labels"
                
                if source_img_dir.exists() and source_lbl_dir.exists():
                    target_img_dir = self.target / f"{subfolder.rstrip('/')}" / "images"
                    target_lbl_dir = self.target / f"{subfolder.rstrip('/')}" / "labels"
                    
                    target_img_dir.mkdir(parents=True, exist_ok=True)
                    target_lbl_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Copy all images
                    for img_path in source_img_dir.glob(f"*{self.config.input_ext}"):
                        shutil.copy2(img_path, target_img_dir / img_path.name)
                    
                    # Copy all labels (TXT for detection/segmentation, PNG for semantic)
                    if self.annotation_type == "semantic_segmentation":
                        label_pattern = "*.png"
                    else:
                        label_pattern = "*.txt"
                    
                    for lbl_path in source_lbl_dir.glob(label_pattern):
                        shutil.copy2(lbl_path, target_lbl_dir / lbl_path.name)
        
        self.logger.info('Source data copied successfully')

    def visualize_random_samples(self) -> None:
        """
        Visualize random samples from the original source images and their corresponding tiles.
        This helps see how original images are divided into tiles.
        """
        if self.num_viz_samples <= 0:
            return

        # Get images from source directory first
        if self.annotation_type == "image_classification":
            # Get all class directories in train folder
            train_dir = self.source / 'train'
            source_image_paths = list(train_dir.glob(f'**/*{self.config.input_ext}'))
        else:
            # Original code for object detection and instance segmentation
            train_image_dir = self.source / 'train' / 'images'
            source_image_paths = list(train_image_dir.glob(f'*{self.config.input_ext}'))

        if not source_image_paths:
            self.logger.warning("No images found in source train folder for visualization")
            return
        
        # Select random samples from source
        num_samples = min(self.num_viz_samples, len(source_image_paths))
        selected_source_images = random.sample(source_image_paths, num_samples)
        
        # Process each selected source image
        for image_idx, source_image_path in enumerate(selected_source_images):
            # Find all tiles derived from this source image
            base_name = source_image_path.stem
            
            if self.annotation_type == "image_classification":
                # For image classification
                class_name = source_image_path.parent.name
                target_train_dir = self.target / 'train' / class_name
                tiles = list(target_train_dir.glob(f"{base_name}_*_*_*_*{self.config.output_ext}"))
            else:
                # For object detection and instance segmentation
                target_train_dir = self.target / 'train' / 'images'
                tiles = list(target_train_dir.glob(f"{base_name}_*_*_*_*{self.config.output_ext}"))
                
            if not tiles:
                self.logger.warning(f"No tiles found for source image {source_image_path.name}")
                continue
                
            # Render source image first
            if self.annotation_type == "image_classification":
                source_label = source_image_path.parent.name  # Class name
            else:
                # For detection and segmentation tasks
                if self.annotation_type == "semantic_segmentation":
                    source_label_path = source_image_path.parent.parent / 'labels' / f"{source_image_path.stem}.png"
                else:
                    source_label_path = source_image_path.parent.parent / 'labels' / f"{source_image_path.stem}.txt"
                if not source_label_path.exists():
                    self.logger.warning(f"Label file not found for source {source_image_path.name}")
                    continue
                
            # Either the class category or the label file path 
            label_path = source_label if self.annotation_type == "image_classification" else source_label_path
            # Render the source image
            self._render_single_sample(source_image_path, 
                                       label_path,
                                       f"{image_idx+1:03d}_source")
            
            # Render each tile
            for tile_idx, tile_path in enumerate(tiles):
                if self.annotation_type == "image_classification":
                    tile_label = tile_path.parent.name  # Class name
                else:
                    # For detection and segmentation tasks
                    if self.annotation_type == "semantic_segmentation":
                        tile_label_path = self.target / 'train' / 'labels' / f"{tile_path.stem}.png"
                    else:
                        tile_label_path = self.target / 'train' / 'labels' / f"{tile_path.stem}.txt"
                    if not tile_label_path.exists():
                        self.logger.warning(f"Label file not found for tile {tile_path.name}")
                        continue
                
                # Update progress
                if self.progress_callback:
                    progress = TileProgress(
                        current_tile_idx=tile_idx + 1,
                        total_tiles=len(tiles),
                        current_set_name=f'rendered (image {image_idx+1}/{num_samples})',
                        current_image_name=source_image_path.name,
                        current_image_idx=image_idx + 1,
                        total_images=num_samples
                    )
                    self.progress_callback(progress)

                # Extract coordinates from filename for better visualization naming
                try:
                    # Parse coordinates from the filename (format: name_x_y_width_height.ext)
                    parts = tile_path.stem.split('_')
                    x = parts[-4]
                    y = parts[-3]
                    render_id = f"{image_idx+1:03d}_tile_x{x}_y{y}_{tile_idx+1:03d}"
                except (IndexError, ValueError):
                    # Fallback if parsing fails
                    render_id = f"{image_idx+1:03d}_tile_{tile_idx+1:03d}"
                
                # Either the class category or the label file path 
                label_path = tile_label if self.annotation_type == "image_classification" else tile_label_path
                # Render the tile
                self._render_single_sample(tile_path, 
                                           label_path, 
                                           render_id)
            
    def _render_single_sample(self, image_path: Path, 
                              label_path: Union[Path, str],  # Path to labels.txt, or class name
                              idx: Union[str, int]) -> None:
        """
        Render a single sample with its annotations.

        Args:
            image_path: Path to the image file
            label_path: Path to the label file, or class name for image classification
            idx: Index or identifier for the output filename
        """
        # Read image using OpenCV
        img = cv2.imread(str(image_path))
        if img is None:
            self.logger.warning(f"Could not read image: {image_path}")
            return

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        height, width = img.shape[:2]

        # Create figure and axis
        fig, ax = plt.subplots(1)
        ax.imshow(img)

        # Add image filename as figure title
        is_source = "source" in str(idx)
        title = f"{'Source: ' if is_source else 'Tile: '}{image_path.name}"
        fig.suptitle(title, fontsize=10)

        # Random colors for different classes
        np.random.seed(42)  # For consistent colors
        colors = np.random.rand(100, 3)  # Support up to 100 classes
        
        if self.annotation_type == "image_classification":
            class_name = label_path
            ax.text(width / 2, height / 2, 
                    class_name, 
                    fontsize=12, 
                    color='white', 
                    backgroundcolor='black',
                    ha='center')
        elif self.annotation_type == "semantic_segmentation":
            # Read and overlay the mask
            mask = cv2.imread(str(label_path), cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                # Create a colored overlay
                colored_mask = np.zeros_like(img)
                for class_id in np.unique(mask):
                    if class_id == 0:  # Skip background
                        continue
                    color = colors[class_id % len(colors)]
                    # Convert to RGB values
                    rgb_color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    colored_mask[mask == class_id] = rgb_color
                
                # Blend with original image
                alpha = 0.5
                overlay = cv2.addWeighted(img, 1 - alpha, colored_mask, alpha, 0)
                ax.imshow(overlay)
            else:
                self.logger.warning(f"Could not read mask: {label_path}")
        else:
            # Object detection and instance segmentation - read text file
            with open(label_path) as f:
                for line in f:
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    color = colors[class_id % len(colors)]

                    if self.config.annotation_type == "object_detection":
                        # Parse bounding box
                        x_center = float(parts[1]) * width
                        y_center = float(parts[2]) * height
                        box_w = float(parts[3]) * width
                        box_h = float(parts[4]) * height

                        # Calculate box coordinates
                        x = x_center - box_w / 2
                        y = y_center - box_h / 2

                        # Create rectangle patch with transparency
                        rect = patches.Rectangle(
                            (x, y),
                            box_w,
                            box_h,
                            linewidth=2,
                            edgecolor=color,
                            facecolor=color,
                            alpha=0.3  # Add transparency
                        )
                        ax.add_patch(rect)
                        
                    else:  # instance segmentation
                        # Parse polygon coordinates
                        coords = []
                        try:
                            for i in range(1, len(parts), 2):
                                if i + 1 < len(parts):  # Make sure y coordinate exists
                                    x = float(parts[i]) * width
                                    y = float(parts[i + 1]) * height
                                    coords.append([x, y])

                            # Only create polygon if we have enough valid coordinates
                            if len(coords) >= 3 and len(set(tuple(p) for p in coords)) >= 3:  # At least 3 unique points
                                # Create polygon patch with transparency
                                polygon = MplPolygon(
                                    coords,
                                    facecolor=color,
                                    edgecolor=color,
                                    linewidth=2,
                                    alpha=0.3
                                )
                                try:
                                    ax.add_patch(polygon)
                                except Exception as e:
                                    self.logger.warning(f"Failed to add polygon: {e}, coords shape")
                            else:
                                self.logger.warning(f"Polygon with insufficient coordinates in {image_path.name}")
                        except Exception as e:
                            self.logger.warning(f"Error creating polygon in {image_path.name}: {e}")
            
        # Remove axes
        ax.axis('off')

        # Adjust layout
        plt.ioff()  # Turn off interactive mode
        plt.tight_layout()

        # Save the visualization
        output_path = self.render_dir / image_path.name
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close(fig)  # Close the specific figure

    def run(self) -> None:
        """Run the complete tiling process"""
        try:
            # Validate directories
            self._validate_directories()

            # Train, val/id, test subfolders
            for subfolder in self.subfolders:
                self._process_subfolder(subfolder)

            self.logger.info('Tiling process completed successfully')

            # Check if valid or test folders are empty
            self._check_and_split_data()

            # Copy and update data.yaml with new paths
            self._copy_and_update_data_yaml()
            
            # Copy source data if requested
            if self.config.copy_source_data:
                self._copy_source_data()

            # Generate visualizations if requested
            if self.num_viz_samples > 0:
                self.logger.info(f'Generating {self.num_viz_samples} visualization samples...')
                self.visualize_random_samples()
                self.logger.info('Visualization generation completed')

        except Exception as e:
            self.logger.error(f'Error during tiling process: {str(e)}')
            raise
        
    def __del__(self):
        """Cleanup method to ensure all progress bars are closed"""
        if self._progress_bars:
            for pbar in self._progress_bars.values():
                pbar.close()
            self._progress_bars.clear()
