import h5py
import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch
import shutil
from ewokstomo.tasks.online.reducedarksflats import ReduceDarksFlatsTask
from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat
from ewokstomo.tests.test_reduce import get_data_dir
from ewokstomo.tests.mock import FakeScan


@pytest.fixture
def TestEwoksTomo_0010_dataset(tmp_path) -> Path:
    scan = "TestEwoksTomo_0010"
    src_dir = get_data_dir(scan)
    dst_dir = tmp_path / scan
    shutil.copytree(src_dir, dst_dir)
    for pattern in ("*_darks.hdf5", "*_flats.hdf5"):
        for f in dst_dir.glob(pattern):
            f.unlink()
    return dst_dir


def test_reduce_online(TestEwoksTomo_0010_dataset):
    nx_file = TestEwoksTomo_0010_dataset / "TestEwoksTomo_0010.nx"
    h5py_file = TestEwoksTomo_0010_dataset / "TestEwoksTomo_0010.h5"

    # --- Run offline task to produce ground-truth ---
    offline_task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx_file),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    offline_task.execute()
    darks_offline = Path(offline_task.outputs.reduced_darks_path)
    flats_offline = Path(offline_task.outputs.reduced_flats_path)

    # Load offline reduced frames
    with h5py.File(darks_offline, "r") as f:
        offline_dark = f["entry0000/darks/0"][()]
    with h5py.File(flats_offline, "r") as f:
        offline_flat = f["entry0000/flats/2"][()]

    # --- Prepare fake online scan using raw frames ---
    with h5py.File(h5py_file, "r") as f:
        dark_frames = [np.array(frame) for frame in f["2.1/measurement/edgetwinmic"]]
        flat_frames = [np.array(frame) for frame in f["3.1/measurement/edgetwinmic"]]

    # Test both darks and flats
    for frames, title, method, expected in [
        (dark_frames, "darks", "mean", offline_dark),
        (flat_frames, "flats", "median", offline_flat),
    ]:
        fake_scan = FakeScan(frames, title=title)

        with (
            patch("ewokstomo.tasks.online.reducedarksflats.BeaconData") as MockBeacon,
            patch("ewokstomo.tasks.online.reducedarksflats.DataStore") as MockStore,
        ):
            MockBeacon.return_value.get_redis_data_db.return_value = "redis://fake"
            MockStore.return_value.load_scan.return_value = fake_scan

            output_file = TestEwoksTomo_0010_dataset / f"online_{title}.h5"
            task = ReduceDarksFlatsTask(
                inputs={
                    "scan_key": f"scan_{title}",
                    "index": 0,
                    "reduction_method": method,
                    "output_file_path": str(output_file),
                }
            )
            task.execute()

        assert output_file.is_file()

        # Load online reduced frames
        with h5py.File(output_file, "r") as f:
            reduced_online = f[f"entry0000/{title}"][()]

        # --- Compare online vs offline results ---
        np.testing.assert_allclose(reduced_online, expected, rtol=1e-6)


def test_reduce_offline(TestEwoksTomo_0010_dataset):
    nx_file = TestEwoksTomo_0010_dataset / "TestEwoksTomo_0010.nx"
    h5py_file = TestEwoksTomo_0010_dataset / "TestEwoksTomo_0010.h5"

    # --- Run offline task to produce ground-truth ---
    offline_task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx_file),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    offline_task.execute()
    darks_offline = Path(offline_task.outputs.reduced_darks_path)
    flats_offline = Path(offline_task.outputs.reduced_flats_path)

    # Load offline reduced frames
    with h5py.File(darks_offline, "r") as f:
        offline_dark = f["entry0000/darks/0"][()]
    with h5py.File(flats_offline, "r") as f:
        offline_flat = f["entry0000/flats/2"][()]

    # Test both darks and flats
    for title, method, expected in [
        ("dark", "mean", offline_dark),
        ("flat", "median", offline_flat),
    ]:

        output_file = TestEwoksTomo_0010_dataset / f"offline_{title}.h5"
        task = ReduceDarksFlatsTask(
            inputs={
                "scan_file_path": str(h5py_file),
                "scan_number": 2 if "dark" in title else 3,
                "index": 0,
                "reduction_method": method,
                "output_file_path": str(output_file),
            }
        )
        task.execute()

        assert output_file.is_file()

        with h5py.File(output_file, "r") as f:
            reduced_online = f[f"entry0000/{title}"][()]

        np.testing.assert_allclose(reduced_online, expected, rtol=1e-6)
