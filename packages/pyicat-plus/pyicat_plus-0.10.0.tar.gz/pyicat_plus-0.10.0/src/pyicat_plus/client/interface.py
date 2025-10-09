import datetime
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from .deprecation_utils import deprecated_method
from .deprecation_utils import warn_deprecated_module
from .types import ArchiveStatusLevel
from .types import ArchiveStatusLevel as StatusLevel  # noqa F401 deprecated
from .types import ArchiveStatusType
from .types import ArchiveStatusType as StatusType  # noqa F401 deprecated
from .types import Dataset
from .types import DatasetId
from .types import DatasetMetadata  # noqa F401
from .types import SampleMetadata

warn_deprecated_module()


class IcatClientInterface:
    def send_message(
        self,
        msg: str,
        msg_type: Optional[str] = None,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        investigation_id: Optional[str] = None,
        dataset: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        """
        Send a message to the proposal or beamline e-logbook.

        :param msg: The message content.
        :param msg_type: {'comment', 'debug', 'info', 'error', 'commandLine'}, optional.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param investigation_id: The investigation identifier in the ICAT database.
        :param dataset: The specific dataset name to link the message to.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param editable: Used with the `formatted` field, to determine the category of message. Annotation characterizes editable and unformatted messages, while Notification charaterizes non-editable and formatted messages.
        :param formatted: Used with the `editable` field, to determine the category of message. Annotation characterizes editable and unformatted messages, while Notification charaterizes non-editable and formatted messages.
        :param mimetype: {'text/plain', 'text/html'}, optional.
        :param payload: Additional payload for the message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        raise NotImplementedError

    def disconnect(self):
        pass

    def send_binary_data(
        self,
        data: bytes,
        mimetype: Optional[str] = None,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        investigation_id: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        """
        Send an image in base64 format to the proposal or beamline e-logbook.

        :param data: The binary message content.
        :param mimetype: {'text/plain', 'text/html'}, optional.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param investigation_id: The investigation identifier in the ICAT database.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        raise NotImplementedError

    def send_text_file(
        self,
        filename: str,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        dataset: Optional[str] = None,
        investigation_id: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        """
        Send the content of a text file as a message to the proposal or beamline e-logbook.

        :param filename: The filename containing the message to be sent.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param investigation_id: The investigation identifier in the ICAT database.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        raise NotImplementedError

    def send_binary_file(
        self,
        filename: str,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        """
        Send the content of a file as a binary image to the proposal or beamline e-logbook.

        :param filename: The filename of the image to be sent.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        raise NotImplementedError

    def start_investigation(
        self,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        start_datetime=None,
        end_datetime=None,
    ):
        """
        Send a message to ActiveMQ to either synchronize the experiment session from the User Portal in ICAT or to create a test experiment session in ICAT.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param start_datetime: The start date of the experiment session, timezone local time. Current date time by default.
        :param end_datetime: The end date of the experiment session, timezone local time.
        """
        raise NotImplementedError

    def store_dataset(
        self,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        dataset: Optional[str] = None,
        path: Optional[str] = None,
        metadata: dict = None,
        store_filename: Optional[str] = None,
    ):
        """
        Request icat to store raw dataset.

        :param beamline str: beamline name like id01, id15a, bm18...
        :param proposal str: proposal name like in1169, blc14795, ihma429...
        :param str dataset: dataset name.
        :param str path: path to the raw dataset to store. Must be a folder.
        :param dict metadata: metadata to associate with the dataset. Must contain keys defined by the appropriate application definition, available at https://icat-esrf-definitions.readthedocs.io.
        :param str store_filename: xml file with metadata to be stored.
        """

        raise NotImplementedError

    def store_processed_data(
        self,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        dataset: Optional[str] = None,
        path: Optional[str] = None,
        metadata: dict = None,
        raw: Sequence = tuple(),
        store_filename: Optional[str] = None,
    ):
        """
        Request icat to store a processed dataset.

        :param beamline str: beamline name like id01, id15a, bm18...
        :param proposal str: proposal name like in1169, blc14795, ihma429...
        :param str dataset: dataset name like sample_XYZ.
        :param str path: path to the processed dataset to store. Can be a file or a folder.
        :param dict metadata: metadata to associate with the dataset. Must contain keys defined by the appropriate application definition, available at https://icat-esrf-definitions.readthedocs.io.
        :param tuple raw: Path(s) to the raw dataset(s). Should point to the 'bliss dataset' folder(s).
                          If processing relies on multiple datasets, all corresponding folders must be provided.
        :param str store_filename: xml file with metadata to be stored.
        """
        raise NotImplementedError

    def store_dataset_from_file(self, store_filename: Optional[str] = None):
        """
        Send a message to ActiveMQ to store a dataset and the associated metadata from a xml file stored on the disk.

        :param store_filename: The XML filename containing all dataset metadata.
        """
        raise NotImplementedError

    def investigation_info(
        self,
        beamline: str,
        proposal: str,
        date: Optional[Union[datetime.datetime, datetime.date]] = None,
        allow_open_ended: bool = True,
        timeout: Optional[float] = None,
    ) -> Optional[dict]:
        """
        Return the information of the experiment session corresponding to a beamline, proposal and date.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the proposal, beamline, e-logbbok url and data portal url of the experiment session.
        """
        raise NotImplementedError

    def registered_dataset_ids(
        self,
        beamline: str,
        proposal: str,
        date: Optional[Union[datetime.datetime, datetime.date]] = None,
        allow_open_ended: bool = True,
        timeout: Optional[float] = None,
    ) -> Optional[List[DatasetId]]:
        """
        Return the dataset list of an experiment session.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: The list of datasets (name and path).
        """
        raise NotImplementedError

    def registered_datasets(
        self,
        beamline: str,
        proposal: str,
        date: Optional[Union[datetime.datetime, datetime.date]] = None,
        allow_open_ended: bool = True,
        timeout: Optional[float] = None,
    ) -> Optional[List[Dataset]]:
        """
        Return the dataset information list of an experiment session.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: The list of datasets (name, path, ICAT identifier, and :class:`.DatasetMetadata`).
        """
        raise NotImplementedError

    def investigation_info_string(
        self,
        beamline: str,
        proposal: str,
        date: Optional[Union[datetime.datetime, datetime.date]] = None,
        allow_open_ended: bool = True,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Return the experiment session information as a string.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the experiment session information from the metadata catalog as a string.
        """
        raise NotImplementedError

    def investigation_summary(
        self,
        beamline: str,
        proposal: str,
        date: Optional[Union[datetime.datetime, datetime.date]] = None,
        allow_open_ended: bool = True,
        timeout: Optional[float] = None,
    ) -> List[Tuple]:
        """
        Return the experiment session information as a `Tuple`.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the experiment session information from the metadata catalog as a `Tuple`.
        """
        raise NotImplementedError

    @deprecated_method
    def update_archive_restore_status(
        self,
        dataset_id: int = None,
        type: ArchiveStatusType = None,
        level: ArchiveStatusLevel = ArchiveStatusLevel.INFO,
        message: Optional[str] = None,
    ):
        """
        DEPRECATED: This method is deprecated and may be removed in future versions.
        Update the archiving or restore status of a dataset.

        :param dataset_id: The ICAT dataset identifier.
        :param type: The type of the status, possible options are {'archiving', 'restoration'}.
        :param level: The level of the status message; possible options are {'info', 'warning', 'error'}.
        :param message: The optional status' message.
        """
        raise NotImplementedError

    def update_metadata(
        self,
        proposal: str = None,
        beamline: str = None,
        dataset_paths: str = None,
        metadata_name: str = None,
        metadata_value: str = None,
    ):
        """
        Update or create datasets metadata.

        :param proposal: The proposal name.
        :param beamline: The beamline name of the proposal.
        :param dataset_paths: Comma-separated list of the dataset locations.
        :param metadata_name: The name of the metadata to update.
        :param metadata_value: The new value of the metadata.
        """
        raise NotImplementedError

    def add_files(
        self,
        dataset_id: int = None,
    ):
        """
        Add missing files to a dataset already ingested.

        :param dataset_id: The ICAT dataset identifier.
        """
        raise NotImplementedError

    def reschedule_investigation(self, investigation_id: str):
        """
        Reschedule an investigation defined by its id.

        :param investigation_id:
        """
        raise NotImplementedError

    def do_log_in(
        self, password: str, username: Optional[str] = None, plugin: str = "esrf"
    ) -> dict:
        """
        Login to access the restricted part of the API.

        :param password:
        :param username: optional username
        :param plugin: authentication plugin, defaults to 'esrf'
        :returns: authentication info
        """
        raise NotImplementedError

    def get_investigations_by(
        self,
        filter: Optional[str] = None,
        instrument_name: Optional[str] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        ids: Optional[str] = None,
    ) -> List[dict]:
        """
        Returns a list of investigations matching the provided criteria.

        :param filter:
        :param instrument_name:
        :param start_date:
        :param end_date:
        :param ids:
        :returns: list of investigations
        """
        raise NotImplementedError

    def get_samples_by(
        self,
        investigation_id: Optional[str] = None,
        sample_ids: Optional[str] = None,
    ) -> List[dict]:
        """
        Returns a list of samples matching the provided criteria.

        :param investigation_id: an investigationId
        :param sample_ids: comma separated list of sampleIds
        """
        return NotImplementedError

    def get_datasets_by(
        self,
        investigation_id: Optional[str] = None,
        dataset_ids: Optional[str] = None,
    ) -> List[dict]:
        """
        Returns a list of dataset matching the provided criteria.

        :param investigation_id: an investigationId
        :param dataset_ids: comma separated list of dataset Ids
        """
        return NotImplementedError

    def get_parcels_by(self, investigation_id: str) -> List[dict]:
        """
        Returns the list of parcels associated to an investigation.

        :param investigation_id:
        :returns: list of parcel information
        """
        raise NotImplementedError

    def get_session_information(self) -> List[dict]:
        """
        Returns the information about a session.

        :returns: session information
        """
        raise NotImplementedError

    def get_sample_metadata_by(
        self, proposal: str, beamline: str
    ) -> List[SampleMetadata]:
        """
        Returns the list of sample metadata associated to a proposal and a beamline.

        :param proposal: Proposal identifier (e.g., "hg237").
        :param beamline: Beamline identifier (e.g., "id13").
        :returns: List of sample metadata.
        """
        raise NotImplementedError

    @property
    def expire_datasets_on_close(self) -> bool:
        """
        A flag indicating whether the dataset expires when it is closed or if it is synchronized with the metadata catalog.
        """
        raise NotImplementedError

    @property
    def reason_for_missing_information(self) -> str:
        """
        A string explaining why some information is missing in the metadata catalog.
        """
        raise NotImplementedError
