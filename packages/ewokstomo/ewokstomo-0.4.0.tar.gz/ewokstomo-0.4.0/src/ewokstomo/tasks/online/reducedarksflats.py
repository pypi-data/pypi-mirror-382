import numpy as np
import logging
import h5py
from ewokscore import Task
from blissdata.redis_engine.store import DataStore
from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.exceptions import EndOfStream
from silx.io.url import DataUrl
from silx.io import h5py_utils
from tomoscan.framereducer.ReduceFrameSaver import ReduceFrameSaver
from blissdata.redis_engine.scan import ScanState
from ewokstomo.tasks.utils import wait_for_scan_state


logger = logging.getLogger(__name__)


class ReduceDarksFlatsTask(
    Task,
    input_names=[
        "index",
        "reduction_method",
        "output_file_path",
    ],
    optional_input_names=[
        # Online parameters
        "scan_key",
        # Offline parameters
        "scan_file_path",
        "scan_number",
        # Common parameters
        "overwrite",
        "output_dtype",
    ],
    output_names=[
        "reduced_url",
    ],
):
    _METHOD_MAP = {"mean": np.mean, "median": np.median}

    def run(self):
        """
        Reduces frames from an online scan stream (darks or flats).

        This task can work in two modes:
        1. Online: connects to a beacon data stream and reads frames in real-time
        2. Offline: reads frames from an existing HDF5 scan file

        index: int
            The index to assign to the reduced frame in the output file, needed for nabu.
        reduction_method: str
            The method to use for reduction ("mean" or "median").
        output_file_path: str
            The path to the output HDF5 file where the reduced frame will be saved.
        scan_key: str
            The identifier key for the scan in the data store. Required for online mode.
        scan_file_path: str
            The path to the existing HDF5 scan file (for offline mode).
        scan_number: int
            The scan number within the HDF5 file (for offline mode).
        overwrite: bool, optional
            Whether to overwrite the output file if it exists (default: True).
        output_dtype: numpy data-type, optional
            The desired data type for the output frame, needed for nabu (default: np.float32).
        """

        # Parse inputs
        reduction_method = self.inputs.reduction_method
        idx = self.inputs.index
        overwrite = self.get_input_value("overwrite", True)
        output_dtype = self.get_input_value("output_dtype", np.float32)
        output_file_path = self.inputs.output_file_path

        # Determine mode and read frames
        if self._has_online_parameters():
            try:
                all_arrays, scan_title = self._read_online(output_dtype)
            except Exception:
                if not self._has_offline_parameters():
                    raise
                logger.warning("Online read failed, falling back to offline mode")
                all_arrays, scan_title = self._read_offline(output_dtype)
        elif self._has_offline_parameters():
            all_arrays, scan_title = self._read_offline(output_dtype)
        else:
            raise ValueError(
                "Requires either 'scan_key' (online) or "
                "'scan_file_path' + 'scan_number' (offline)"
            )

        # Merge and reduce data
        merged_data = np.stack(all_arrays, axis=0)
        reduction_method_func = self.get_reduction_function(reduction_method)
        reduced_frame = reduction_method_func(merged_data, axis=0)

        # Prepare frames dictionary for saving
        frames_dict = {idx: reduced_frame}

        # Create data URL for saving
        data_path = f"entry0000/{scan_title}"
        reduced_url = (
            DataUrl(
                file_path=output_file_path,
                data_path=data_path,
                scheme="silx",
            ),
        )

        # Save reduced frames
        ReduceFrameSaver(
            frames=frames_dict,
            output_urls=reduced_url,
            overwrite=overwrite,
            frames_metadata=None,
            metadata_output_urls=None,
        ).save()

        self.outputs.reduced_url = reduced_url

    def _has_online_parameters(self) -> bool:
        """Check if online parameters are provided."""
        return bool(self.get_input_value("scan_key"))

    def _has_offline_parameters(self) -> bool:
        """Check if offline parameters are provided."""
        return bool(
            self.get_input_value("scan_file_path")
            and self.get_input_value("scan_number")
        )

    def _read_online(self, output_dtype) -> tuple[list[np.ndarray], str]:
        """Read frames from online beacon stream."""
        scan_key = self.inputs.scan_key

        # Connect to beacon and load scan
        beacon_client = BeaconData()
        redis_url = beacon_client.get_redis_data_db()
        data_store = DataStore(redis_url)
        scan = data_store.load_scan(scan_key)

        # Wait for scan to be in at least RUNNING state
        wait_for_scan_state(scan, ScanState.STARTED)

        # Get scan title and determine data type
        scan_title = scan.info.get("title", "").split()[0].lower()
        stream_name = self.get_image_stream_name(scan)

        # Read all frames from the stream
        all_arrays = self.read_stream(scan, stream_name, output_dtype=output_dtype)

        return all_arrays, scan_title

    def _read_offline(self, output_dtype) -> tuple[list[np.ndarray], str]:
        """Read frames from offline HDF5 file."""
        scan_file_path = self.inputs.scan_file_path
        scan_number = self.inputs.scan_number

        subscan = f"{scan_number}.1"

        with h5py_utils.File(scan_file_path, mode="r") as h5f:
            scan_entry = h5f[subscan]
            instrument = scan_entry["instrument"]

            # Get scan title from the scan entry title attribute or scan info
            scan_title = scan_entry["title"][()]
            if isinstance(scan_title, bytes):
                scan_title = scan_title.decode()
            scan_title = scan_title.split()[0].lower()

            # Find the image dataset
            image_dataset = self._get_image_dataset(instrument)
            if image_dataset is None:
                raise ValueError(
                    f"No image dataset found in scan '{scan_file_path}::/{subscan}'"
                )

            # Read all frames
            all_arrays = []
            for i in range(len(image_dataset)):
                data = image_dataset[i].astype(output_dtype)
                all_arrays.append(data)

        return all_arrays, scan_title

    def _get_image_dataset(self, instrument: h5py.Group) -> h5py.Dataset:
        """Find the image dataset in the instrument group."""
        for name in instrument:
            h5item = instrument[name]
            if not isinstance(h5item, h5py.Group):
                continue
            if "image" in h5item:
                return h5item["image"]
        return None

    def read_stream(
        self, scan, stream_name, output_dtype=np.float32
    ) -> list[np.ndarray]:
        """Reads data from a stream in the scan."""
        my_stream = scan.streams[stream_name]
        my_cursor = my_stream.cursor()
        all_arrays = []
        try:
            while True:
                view = my_cursor.read()
                data = view.get_data().astype(output_dtype)
                all_arrays.append(data)
        except EndOfStream:
            logger.info("Cursor reached the end.")
        return all_arrays

    def get_reduction_function(self, method):
        """
        Returns the reduction method to be used.
        """

        if method not in self._METHOD_MAP:
            raise ValueError(
                f"Unknown reduction method: {method}. Available: {self._METHOD_MAP.keys()}"
            )

        return self._METHOD_MAP[method]

    def get_image_stream_name(self, scan):
        """
        Returns the image stream name from the scan.
        """
        for stream_name in scan.streams:
            if ":image" in stream_name:
                return stream_name
