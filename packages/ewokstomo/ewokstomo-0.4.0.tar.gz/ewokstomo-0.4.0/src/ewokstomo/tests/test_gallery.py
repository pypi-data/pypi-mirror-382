import shutil
from pathlib import Path

import pytest
import numpy as np
from PIL import Image

from ewokstomo.tasks.buildgallery import BuildProjectionsGallery, BuildSlicesGallery


def get_data_dir(scan_name: str) -> Path:
    return Path(__file__).resolve().parent / "data" / scan_name


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    src_dir = get_data_dir("TestEwoksTomo_0010")
    dst_dir = tmp_path / "TestEwoksTomo_0010"
    shutil.copytree(src_dir, dst_dir)
    # remove any existing darks/flats and gallery
    for pattern in ("*_darks.hdf5", "*_flats.hdf5", "gallery"):
        for f in dst_dir.glob(pattern):
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
    # generate fresh darks/flats
    from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat

    nx = dst_dir / "TestEwoksTomo_0010.nx"
    rd_task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    rd_task.run()
    return dst_dir


@pytest.fixture
def simple_image() -> np.ndarray:
    return np.linspace(0, 255, num=100, dtype=float).reshape((10, 10))


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [BuildProjectionsGallery])
def test_buildgallery_task(Task, tmp_dataset_path):
    nx = tmp_dataset_path / "TestEwoksTomo_0010.nx"
    darks = tmp_dataset_path / "TestEwoksTomo_0010_darks.hdf5"
    flats = tmp_dataset_path / "TestEwoksTomo_0010_flats.hdf5"
    task = Task(
        inputs={
            "nx_path": str(nx),
            "reduced_darks_path": str(darks),
            "reduced_flats_path": str(flats),
        },
    )
    task.run()
    gallery_dir = Path(task.outputs.processed_data_dir) / "gallery"
    assert gallery_dir.exists(), "Gallery directory does not exist"
    assert gallery_dir.is_dir(), "Gallery path is not a directory"

    images = sorted(gallery_dir.glob("*.png"))
    assert len(images) == 5, f"Expected 5 images, found {len(images)}"

    for img_path in images:
        img = Image.open(img_path)
        assert img.format == "PNG", f"{img_path.name} is not a valid PNG image"
        assert img.mode == "L", f"{img_path.name} is not grayscale"
        assert (
            img.size[0] > 0 and img.size[1] > 0
        ), f"{img_path.name} has invalid dimensions"

        arr = np.array(img)
        assert arr.dtype == np.uint8, f"{img_path.name} not saved as 8-bit"
        assert (
            arr.max() <= 255 and arr.min() >= 0
        ), f"{img_path.name} has out-of-bound pixel values"

        unique_vals = np.unique(arr)
        assert (
            len(unique_vals) > 1
        ), f"{img_path.name} appears to be flat (no intensity variation)"


@pytest.mark.order(6)
def test_save_to_gallery_bounds(simple_image, tmp_path):
    scan_dir = get_data_dir("TestEwoksTomo_0010")
    output_file = tmp_path / "image_bounds_00000.png"
    task = BuildProjectionsGallery(
        inputs={
            "nx_path": str(scan_dir / "TestEwoksTomo_0010.nx"),
            "reduced_darks_path": str(scan_dir / "TestEwoksTomo_0010_darks.hdf5"),
            "reduced_flats_path": str(scan_dir / "TestEwoksTomo_0010_flats.hdf5"),
            "bounds": (50.0, 200.0),
        },
    )
    task.gallery_overwrite = True
    task.gallery_output_binning = 1
    task.save_to_gallery(output_file, simple_image)
    assert output_file.exists(), "Gallery file was not created"


@pytest.mark.order(7)
@pytest.mark.parametrize("angle_step,expected_count", [(45, 9), (90, 5), (180, 3)])
def test_buildgallery_angles(angle_step, expected_count, tmp_dataset_path):
    nx = tmp_dataset_path / "TestEwoksTomo_0010.nx"
    darks = tmp_dataset_path / "TestEwoksTomo_0010_darks.hdf5"
    flats = tmp_dataset_path / "TestEwoksTomo_0010_flats.hdf5"
    gallery_dir = tmp_dataset_path / "gallery"
    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)
    task = BuildProjectionsGallery(
        inputs={
            "nx_path": str(nx),
            "reduced_darks_path": str(darks),
            "reduced_flats_path": str(flats),
            "angle_step": angle_step,
        },
    )
    task.run()
    images = list(gallery_dir.glob("*.png"))
    assert (
        len(images) == expected_count
    ), f"Expected {expected_count} images, found {len(images)}"


def _expected_slice_path(root: Path) -> Path:
    return (
        root / "reconstructed_slices" / "TestEwoksTomo_0010slice_000008_plane_XY.hdf5"
    )


@pytest.mark.order(11)
def test_buildslicesgallery_creates_one_image(tmp_dataset_path):
    gallery_dir = tmp_dataset_path / "gallery"
    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)
    assert slice_path.exists(), f"Missing test input: {slice_path}"

    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
            "output_binning": 2,
        }
    )
    task.run()

    processed_dir = Path(task.outputs.processed_data_dir)
    out_gallery = Path(task.outputs.gallery_path)
    out_image = Path(task.outputs.gallery_image_path)

    assert out_gallery == processed_dir / "gallery"
    assert out_gallery.exists() and out_gallery.is_dir()

    # New naming: <input_stem>_bin{binning}.png
    assert out_image.name == f"{slice_path.stem}_bin2.png"
    assert out_image.exists()

    with Image.open(out_image) as im:
        assert im.format == "PNG"
        assert im.mode == "L"
        w, h = im.size
        assert w > 0 and h > 0
        arr = np.array(im)
        assert arr.dtype == np.uint8
        assert 0 <= arr.min() <= 255 and 0 <= arr.max() <= 255
        assert len(np.unique(arr)) > 1


@pytest.mark.order(12)
def test_buildslicesgallery_overwrite_guard(tmp_dataset_path):
    gallery_dir = tmp_dataset_path / "gallery"
    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)

    # First run creates the image
    BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
        }
    ).run()

    # Second run with overwrite disabled must raise
    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": False,
        }
    )
    with pytest.raises(OSError):
        task.run()


@pytest.mark.order(13)
def test_buildslicesgallery_bounds_and_binning(tmp_dataset_path):
    gallery_dir = tmp_dataset_path / "gallery"
    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)

    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
            "bounds": (50.0, 200.0),
            "output_binning": 2,
        }
    )
    task.run()

    processed_dir = Path(task.outputs.processed_data_dir)
    assert task.get_gallery_dir(processed_dir) == str(processed_dir / "gallery")

    out_image = Path(task.outputs.gallery_image_path)
    with Image.open(out_image) as im:
        arr = np.array(im)
        assert arr.min() >= 0 and arr.max() <= 255
        assert len(np.unique(arr)) >= 6
        assert (arr.max() - arr.min()) >= 32
