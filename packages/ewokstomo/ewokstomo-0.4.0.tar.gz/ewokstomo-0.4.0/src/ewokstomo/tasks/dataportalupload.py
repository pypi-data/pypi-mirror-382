from __future__ import annotations
from typing import Any
import logging

from ewokscore import Task
from ewokscore.missing_data import MissingData
from esrf_pathlib import ESRFPath
from pyicat_plus.client.main import IcatClient
from pyicat_plus.client import defaults

logger = logging.getLogger(__name__)


def _build_icat_payload(
    folder_path: str, metadata_in: dict[str, Any] | MissingData
) -> dict[str, Any]:
    """Parse the path, normalize metadata, and return the ICAT call payload."""
    processed_path = ESRFPath(folder_path)

    if processed_path.schema_name is None:
        raise ValueError(f"Unknown ESRF path schema: {folder_path}")
    if processed_path.data_type != "PROCESSED_DATA":
        raise ValueError(f"Not a PROCESSED_DATA path: {folder_path}")

    if isinstance(metadata_in, MissingData):
        metadata = {"Sample_name": processed_path.collection}
    else:
        metadata = dict(metadata_in)
        metadata.setdefault("Sample_name", processed_path.collection)

    return {
        "beamline": processed_path.beamline,
        "proposal": processed_path.proposal,
        "dataset": processed_path.dataset,
        "path": str(processed_path),
        "raw": [str(processed_path.raw_dataset_path)],
        "metadata": metadata,
    }


class DataPortalUpload(
    Task,
    input_names=["process_folder_path"],
    optional_input_names=["metadata", "dry_run"],
):
    """Upload a processed dataset folder to the Data Portal using pyicat_plus."""

    icat_client_factory = staticmethod(
        lambda: IcatClient(metadata_urls=defaults.METADATA_BROKERS)
    )

    def run(self):
        folder_path: str = self.inputs.process_folder_path
        metadata_in = getattr(self.inputs, "metadata", MissingData())
        dry_run = bool(getattr(self.inputs, "dry_run", False))

        try:
            payload = _build_icat_payload(folder_path, metadata_in)

            if dry_run:
                logger.info(
                    "Dry-run: would store_processed_data "
                    "proposal=%s beamline=%s dataset=%s path=%s raw=%s metadata=%s",
                    payload["proposal"],
                    payload["beamline"],
                    payload["dataset"],
                    payload["path"],
                    payload["raw"],
                    payload["metadata"],
                    extra={"dp_payload": payload},
                )
                return

            client = self.icat_client_factory()
            try:
                client.store_processed_data(**payload)
                self.icat_status = "stored"
            finally:
                try:
                    client.disconnect()
                except Exception:
                    logger.warning("Failed to disconnect ICAT client")

        except ValueError as e:
            logger.warning("DataPortalUpload skipped: %s", e)
        except Exception as e:
            logger.warning("Error in DataPortalUpload: %s", e)
