import json
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import h5py
from esrf_pathlib import ESRFPath

from . import path_utils

_DATA_FORMATS = ("esrfv1", "esrfv2", "esrfv3", "id16bspec", "mx")

MX_METADATA_FILENAME = "metadata.json"

logger = logging.getLogger(__name__)


def get_session_dir(
    proposal: str,
    beamline: str,
    session: str,
    root_dir: Optional[str] = None,
    raw_data_format: str = "esrfv3",
) -> str:
    """Get the session directory from the proposal, beamlines and session name."""
    if raw_data_format not in _DATA_FORMATS:
        _raise_raw_data_format_error(raw_data_format)
    if "*" in (proposal, beamline, session):
        if root_dir is None:
            root_dir = os.path.join(os.sep, "data", "visitor")
        return os.path.join(root_dir, proposal, beamline, session)
    path = ESRFPath.from_fields(
        data_root=root_dir,
        proposal=proposal,
        beamline=beamline,
        session_date=session,
    )
    return str(path)


def parse_session_dir(
    session_dir: str, raw_data_format: str = "esrfv3"
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Get proposal, beamline and session name from the session directory."""
    try:
        path = ESRFPath(session_dir)
        proposal = path.proposal
        beamline = path.beamline_normalized
        session = path.session_date.strftime("%Y%m%d")
    except (ValueError, TypeError, AttributeError, RuntimeError):
        logger.warning("Not a valid session directory: %r", session_dir)
        return None, None, None
    return proposal, beamline, session


def get_raw_data_dir(session_dir: str, raw_data_format: str = "esrfv3") -> str:
    """Get the raw data directory from proposal, beamline and session name.
    This is the directory when Bliss saves the raw data.
    """
    if raw_data_format in ("esrfv3", "id16bspec", "mx"):
        return path_utils.markdir(os.path.join(session_dir, "RAW_DATA"))
    if raw_data_format == "esrfv2":
        return path_utils.markdir(os.path.join(session_dir, "raw"))
    if raw_data_format == "esrfv1":
        return path_utils.markdir(session_dir)
    _raise_raw_data_format_error(raw_data_format)


def get_dataset_filters(
    raw_root_dir: str, raw_data_format: str = "esrfv3"
) -> List[str]:
    """Get the dataset directory search filters from the raw data directory."""
    if raw_data_format in ("esrfv1", "esrfv2", "esrfv3", "id16bspec"):
        return [path_utils.markdir(os.path.join(raw_root_dir, "*", "*"))]
    elif raw_data_format == "mx":
        filters = []
        for root, dirs, files in os.walk(raw_root_dir):
            if MX_METADATA_FILENAME in files:
                filters.append(path_utils.markdir(root))
        return filters
    _raise_raw_data_format_error(raw_data_format)


def get_raw_dataset_name(
    dataset_dir: str, raw_data_format: str = "esrfv3"
) -> Optional[str]:
    """Get the raw data dataset name from the dataset directory."""
    if raw_data_format in ("esrfv1", "esrfv2", "esrfv3"):
        collection, collection_dataset = path_utils.split(dataset_dir)[-2:]
        if not collection_dataset.startswith(collection):
            return None
        dataset_name = collection_dataset[len(collection) + 1 :]
        if not dataset_name:
            return None
        return dataset_name
    if raw_data_format in ("id16bspec", "mx"):
        return path_utils.split(dataset_dir)[-1]
    _raise_raw_data_format_error(raw_data_format)


def get_raw_dataset_metadata(
    dataset_dir: str, raw_data_format: str = "esrfv3"
) -> Dict[str, str]:
    """Get dataset info from the raw dataset directory."""
    if raw_data_format in ("esrfv1", "esrfv2", "esrfv3"):
        return _raw_dataset_metadata_esrf(dataset_dir)
    if raw_data_format == "id16bspec":
        return _raw_dataset_metadata_id16bspec(dataset_dir)
    if raw_data_format == "mx":
        return _raw_dataset_metadata_mx(dataset_dir)
    _raise_raw_data_format_error(raw_data_format)


def _raise_raw_data_format_error(raw_data_format: str) -> None:
    if raw_data_format in _DATA_FORMATS:
        raise RuntimeError(f"Implementation error for '{raw_data_format}'")
    else:
        raise NotImplementedError(
            f"Raw data format '{raw_data_format}' is not supported"
        )


def _raw_dataset_metadata_esrf(dataset_dir: str) -> Dict[str, str]:
    try:
        path = ESRFPath(dataset_dir)
        dataset_file = str(path.raw_dataset_file)
        if not os.path.exists(dataset_file):
            raise FileNotFoundError("HDF5 file does not exist")
    except AttributeError as e:
        raise FileNotFoundError(f"Dataset directory is not valid ({e})") from e

    dataset_metadata = dict()
    enddate = None
    try:
        with h5py.File(dataset_file, "r", locking=False) as f:
            if not _is_bliss_raw_dataset_file(f):
                raise ValueError("HDF5 file not created by Bliss")
            startdate = f.attrs.get("file_time")
            for scan in map(str, sorted(map(float, list(f)))):
                sample_name = _read_hdf5_dataset(
                    f, f"/{scan}/sample/name", default=None
                )
                if sample_name is not None:
                    dataset_metadata["Sample_name"] = str(sample_name)
                enddate = _read_hdf5_dataset(f, f"/{scan}/end_time", default=enddate)
    except Exception as e:
        raise RuntimeError(f"HDF5 reading error ({e})") from e

    if startdate is not None:
        dataset_metadata["startDate"] = startdate
    if enddate is not None:
        dataset_metadata["endDate"] = enddate

    return dataset_metadata


def _raw_dataset_metadata_id16bspec(dataset_dir: str) -> Dict[str, str]:
    dataset_metadata = dict()
    path = ESRFPath(dataset_dir)
    filename = f"{path.proposal}-{path.collection}-{path.dataset}.h5"
    dataset_file = os.path.join(dataset_dir, filename)

    if not os.path.exists(dataset_file):
        raise FileNotFoundError("HDF5 file does not exist")

    startdate = None
    enddate = None
    try:
        with h5py.File(dataset_file, "r", locking=False) as f:
            for name in f:
                entry = f[name]
                try:
                    startdate = _read_hdf5_dataset(entry, "start_time", default=None)
                    enddate = _read_hdf5_dataset(entry, "end_time", default=None)
                except KeyError as e:
                    raise ValueError(f"Time could not be read from HDF5 ({e})") from e
                break
    except Exception as e:
        raise RuntimeError(f"HDF5 reading error ({e})") from e

    if startdate is not None:
        dataset_metadata["startDate"] = startdate
    if enddate is not None:
        dataset_metadata["endDate"] = enddate
    dataset_metadata["Sample_name"] = path.collection
    return dataset_metadata


def _raw_dataset_metadata_mx(dataset_dir: str) -> Dict[str, str]:
    """Read metadata from MX_METADATA_FILENAME for 'mx' format."""
    metadata_file = os.path.join(dataset_dir, MX_METADATA_FILENAME)

    if not os.path.isfile(metadata_file):
        raise FileNotFoundError(f"{MX_METADATA_FILENAME} not found in {dataset_dir}")

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    return {key: str(value) for key, value in metadata.items() if value is not None}


def _is_bliss_raw_dataset_file(f: h5py.File) -> bool:
    return f.attrs.get("creator", "").lower() in ("bliss", "blissdata", "blisswriter")


def _read_hdf5_dataset(parent: h5py.Group, name: str, default=None) -> Any:
    try:
        value = parent[name][()]
    except KeyError:
        return default
    try:
        return value.decode()
    except AttributeError:
        pass
    return value
