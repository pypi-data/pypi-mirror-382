import os
import re
from pathlib import Path

import numpy as np
import h5py
from PIL import Image
from ewokscore import Task
from tomoscan.esrf.scan.nxtomoscan import NXtomoScan
from nabu.preproc.flatfield import FlatField


def clean_angle_key(angle_key):
    """Convert angle key like '90.00000009(1)' to float, or leave float as is."""
    if isinstance(angle_key, float):
        return angle_key  # already clean
    cleaned = re.sub(r"\(.*?\)", "", angle_key)  # remove '(1)' etc.
    return float(cleaned)


class BuildProjectionsGallery(
    Task,
    input_names=["nx_path", "reduced_darks_path", "reduced_flats_path"],
    optional_input_names=[
        "bounds",
        "angle_step",
        "output_binning",
        "output_format",
        "overwrite",
    ],
    output_names=["processed_data_dir", "gallery_path"],
):
    def run(self):
        """
        Creates a gallery of images from the NXtomoScan object.
        """

        self.gallery_output_format = self.get_input_value("output_format", "png")
        self.gallery_overwrite = self.get_input_value("overwrite", True)
        self.gallery_output_binning = self.get_input_value("output_binning", 2)
        bounds = self.get_input_value("bounds", None)
        angle_step = self.get_input_value("angle_step", 90)

        # Use the directory of the output file as the processed data directory.
        nx_path = Path(self.inputs.nx_path)
        processed_data_dir = nx_path.parent
        gallery_dir = self.get_gallery_dir(processed_data_dir)
        os.makedirs(gallery_dir, exist_ok=True)

        # Open the NXtomoScan object.
        self.nxtomoscan = NXtomoScan(nx_path, entry="entry0000")

        angles, slices = self.get_slices_by_angle_step(angle_step)
        corrected_slices = self.flat_field_correction(slices)

        for angle, slice in zip(angles, corrected_slices):
            # Construct the output file name based on the provided output path.
            gallery_file_name = (
                f"{nx_path.stem}_{round(angle):05d}.{self.gallery_output_format}"
            )
            gallery_file_path = os.path.join(gallery_dir, gallery_file_name)

            # Process the image and save it in the gallery.
            self.save_to_gallery(gallery_file_path, slice, bounds)

        self.outputs.processed_data_dir = str(processed_data_dir)
        self.outputs.gallery_path = str(gallery_dir)

    def get_flats_from_h5(
        self, reduced_flat_path: str, data_path="entry0000/flats"
    ) -> np.ndarray:
        """
        Loads the data from a HDF5 file.
        """
        with h5py.File(reduced_flat_path, "r") as h5f:
            for idx in h5f[data_path]:
                data = h5f[data_path][idx]
                flats_idx = int(idx)
                flats_data = data[()]
        return {flats_idx: flats_data}

    def get_darks_from_h5(
        self, reduced_dark_path: str, data_path="entry0000/darks"
    ) -> np.ndarray:
        """
        Loads the data from a HDF5 file.
        """
        with h5py.File(reduced_dark_path, "r") as h5f:
            for idx in h5f[data_path]:
                data = h5f[data_path][idx]
                darks_idx = int(idx)
                darks_data = data[()]
        return {darks_idx: darks_data}

    def flat_field_correction(self, slices):
        """
        Applies flat field correction to the slices.
        """
        reduced_darks = self.get_darks_from_h5(self.inputs.reduced_darks_path)
        reduced_flats = self.get_flats_from_h5(self.inputs.reduced_flats_path)
        x, y = slices[0].shape
        radios_shape = (len(slices), x, y)
        flat_field = FlatField(
            radios_shape=radios_shape, flats=reduced_flats, darks=reduced_darks
        )
        normalized_slices = flat_field.normalize_radios(slices)
        return normalized_slices

    def get_gallery_dir(self, processed_data_dir: str) -> str:
        """
        Returns the path to the gallery folder inside the processed data directory.
        """
        return str(Path(processed_data_dir) / "gallery")

    def get_proj_from_data_url(self, data_url) -> np.ndarray:
        """Load the data from a DataUrl object."""
        with h5py.File(data_url.file_path(), "r") as h5f:
            data = h5f[data_url.data_path()]
            if data_url.data_slice() is not None:
                return data[data_url.data_slice()].astype(np.float32)

    def get_slices_by_angle_step(self, angle_step=90) -> list:
        """
        Returns the slices of the image to be processed.
        """
        # Get all angles
        angles_dict = self.nxtomoscan.get_proj_angle_url()
        angles_dict = {clean_angle_key(k): v for k, v in angles_dict.items()}
        all_angles = np.array(list(angles_dict.keys()))

        # Determine all 90° targets within full range
        min_angle = np.min(all_angles)
        max_angle = np.max(all_angles)
        target_angles = np.arange(min_angle, max_angle + angle_step, angle_step)

        # For each target angle, find the closest available
        selected_angles = []
        used_indices = set()
        for target in target_angles:
            diffs = np.abs(all_angles - target)
            idx = np.argmin(diffs)
            if idx not in used_indices:  # avoid duplicates
                used_indices.add(idx)
                selected_angles.append(all_angles[idx])

        selected_slices = [
            self.get_proj_from_data_url(angles_dict[angle]) for angle in selected_angles
        ]
        return selected_angles, selected_slices

    def _bin_data(self, data: np.ndarray, binning: int) -> np.ndarray:
        """
        Bins a 2D array by the specified binning factor.
        If binning <= 1, returns the original data.
        """
        if binning <= 1:
            return data
        h, w = data.shape
        new_h = h // binning
        new_w = w // binning
        # Crop the image if necessary so dimensions are divisible by the binning factor.
        data_cropped = data[: new_h * binning, : new_w * binning]
        # Reshape and compute the mean over each bin.
        binned = data_cropped.reshape(new_h, binning, new_w, binning).mean(axis=(1, 3))
        return binned

    def save_to_gallery(
        self,
        output_file_name: str,
        image: np.ndarray,
        bounds: tuple[float, float] | None = None,
    ) -> None:
        """
        Processes and saves the image to the gallery folder:
          - If the image is 3D with a singleton first dimension, reshapes it to 2D.
          - Normalizes the image to 8-bit grayscale using the provided bounds if available.
            If no bounds are provided, lower_bound defaults to 0 and upper_bound is set to the 99.9th percentile
            of pixels below 1e9. Also, any pixel with a value at or above 1e9 is set to 0. This is designed to handle the case of saturated pixels.
          - Applies binning based on gallery_output_binning.
          - Saves the result as an image in the specified output format.
        """
        overwrite = self.gallery_overwrite
        binning = self.gallery_output_binning

        # Ensure the image is 2D. If it's 3D with a single channel, squeeze it.
        if image.ndim == 3 and image.shape[0] == 1:
            image = image.reshape(image.shape[1:])
        elif image.ndim != 2:
            raise ValueError(f"Only 2D grayscale images are handled. Got {image.shape}")

        # Check if bounds is a valid tuple; otherwise use defaults.
        if not isinstance(bounds, tuple):
            lower_bound = 0
            if image.size > 0:
                upper_bound = np.percentile(image, 99.9)
            else:
                upper_bound = 2**16 - 1  # 16Bit
        else:
            lower_bound, upper_bound = bounds

        # Apply clamping and normalization.
        image = np.clip(image, lower_bound, upper_bound)
        image = image - lower_bound
        if upper_bound != lower_bound:
            image = image * (255.0 / (upper_bound - lower_bound))

        # Apply binning if necessary.
        image = self._bin_data(data=image, binning=binning)

        # Convert the image to a PIL Image.
        img = Image.fromarray(image.astype(np.uint8), mode="L")

        if not overwrite and os.path.exists(output_file_name):
            raise OSError(f"File already exists ({output_file_name})")
        img.save(output_file_name)


class BuildSlicesGallery(
    Task,
    input_names=["reconstructed_slice_path"],
    optional_input_names=[
        "bounds",
        "output_binning",
        "output_format",
        "overwrite",
    ],
    output_names=["processed_data_dir", "gallery_path", "gallery_image_path"],
):
    """Create one gallery image from a reconstructed slice.
    The output file keeps the input basename, with `_bin{binning}` suffix and the chosen extension.
    """

    def run(self):
        """Read the slice, normalize/optionally bin, and save to <processed>/gallery."""
        fmt = self.get_input_value("output_format", "png")
        overwrite = bool(self.get_input_value("overwrite", True))
        binning = int(self.get_input_value("output_binning", 2))
        bounds = self.get_input_value("bounds", None)

        slice_path = Path(self.inputs.reconstructed_slice_path)
        if not slice_path.exists():
            raise FileNotFoundError(f"Reconstructed slice not found: {slice_path}")

        slices_dir = slice_path.parent
        processed_data_dir = slices_dir.parent
        gallery_dir = Path(processed_data_dir) / "gallery"
        os.makedirs(gallery_dir, exist_ok=True)

        arr = self._load_slice(slice_path)
        out_name = f"{slice_path.stem}_bin{binning}.{fmt}"
        out_path = gallery_dir / out_name
        self._save_to_gallery(out_path, arr, bounds, overwrite, binning)

        self.outputs.processed_data_dir = str(processed_data_dir)
        self.outputs.gallery_path = str(gallery_dir)
        self.outputs.gallery_image_path = str(out_path)

    def get_gallery_dir(self, processed_data_dir: Path | str) -> str:
        """Return the fixed gallery directory path."""
        return str(Path(processed_data_dir) / "gallery")

    @staticmethod
    def _load_slice(img_path: Path) -> np.ndarray:
        """Load a 2D float32 slice (HDF5 at entry0000/reconstruction/results/data, EDF, or image)."""
        ext = img_path.suffix.lower()
        if ext in (".h5", ".hdf5"):
            with h5py.File(img_path, "r") as h5in:
                img = h5in["entry0000/reconstruction/results/data"][:]
            return np.squeeze(img).astype(np.float32)
        if ext == ".edf":
            try:
                import fabio  # type: ignore
            except Exception as exc:
                raise RuntimeError(
                    "EDF support requires 'fabio' (pip install fabio)."
                ) from exc
            return fabio.open(str(img_path)).data.astype(np.float32)
        with Image.open(img_path) as im:
            arr = np.array(im, dtype=np.float32)
        if arr.ndim == 3 and arr.shape[-1] in (3, 4):
            arr = arr[..., :3].mean(axis=-1)
        return arr

    @staticmethod
    def _bin(data: np.ndarray, binning: int) -> np.ndarray:
        """Downsample by integer binning using mean."""
        if binning <= 1:
            return data
        h, w = data.shape
        nh, nw = h // binning, w // binning
        data = data[: nh * binning, : nw * binning]
        return data.reshape(nh, binning, nw, binning).mean(axis=(1, 3))

    def _save_to_gallery(
        self,
        output_path: Path,
        image: np.ndarray,
        bounds: tuple[float, float] | None,
        overwrite: bool,
        binning: int,
    ) -> None:
        """Clamp to bounds, scale to 8-bit, apply optional binning, then save."""
        if image.ndim != 2:
            raise ValueError(
                f"Only 2D grayscale images are handled. Got shape={image.shape}"
            )
        if not isinstance(bounds, tuple):
            lower = 0.0
            upper = float(np.percentile(image, 99.9)) if image.size else 65535.0
        else:
            lower, upper = float(bounds[0]), float(bounds[1])
        img = np.clip(image, lower, upper) - lower
        scale = 255.0 / (upper - lower) if upper != lower else 1.0
        img = (img * scale).astype(np.float32)
        if binning > 1:
            img = self._bin(img, binning)
        pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), mode="L")
        if not overwrite and output_path.exists():
            raise OSError(f"File already exists ({output_path})")
        pil.save(str(output_path))
