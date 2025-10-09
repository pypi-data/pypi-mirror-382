import datetime
from typing import List
from typing import Optional
from urllib.parse import urljoin

import requests

from ..utils.url import normalize_url
from .deprecation_utils import deprecated_argument
from .types import SampleMetadata


class IcatPlusRestrictedClient:
    """Client for the restricted part of the ICAT+ REST API.

    REST API docs:
    https://icatplus.esrf.fr/api-docs/

    The ICAT+ server project:
    https://gitlab.esrf.fr/icat/icat-plus/-/blob/master/README.md
    """

    DEFAULT_SCHEME = "https"

    def __init__(
        self, url: str, password: Optional[str] = None, session_id: Optional[str] = None
    ):
        url = normalize_url(url, default_scheme=self.DEFAULT_SCHEME)

        path = "catalogue/{session_id}/investigation"
        self._investigation_url = urljoin(url, path)

        path = "catalogue/{session_id}/samples"
        self._sample_url = urljoin(url, path)

        path = "catalogue/{session_id}/dataset"
        self._dataset_url = urljoin(url, path)

        path = "tracking/{session_id}/parcel"
        self._parcel_url = urljoin(url, path)

        path = "/session/{session_id}"
        self._session_info_url = urljoin(url, path)

        path = "session"
        self._authentication_url = urljoin(url, path)

        path = "samplemetadata/{session_id}/samples/acquisition"
        self._sample_metadata_url = urljoin(url, path)

        self._session_id = None

        if password:
            _ = self.login(password)

        if session_id:
            self._session_id = session_id

    def login(
        self, password: str, username: Optional[str] = None, plugin: str = "esrf"
    ) -> dict:
        credentials = {
            "plugin": plugin,
            "password": password,
        }
        if username is not None:
            credentials["username"] = username
        response = requests.post(self._authentication_url, json=credentials)
        response.raise_for_status()
        authentication_response = response.json()
        self._session_id = authentication_response["sessionId"]
        return authentication_response

    @property
    def session_id(self) -> str:
        """
        :raises RuntimeError: No session ID is available.
        """
        if self._session_id:
            return self._session_id

        raise RuntimeError("Login is required.")

    def get_investigations_by(
        self,
        filter: Optional[str] = None,
        instrument_name: Optional[str] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        ids: Optional[str] = None,
    ) -> List[dict]:
        """Returns a list of investigations matching the provided criteria.

        API Reference: https://icatplus.esrf.fr/api-docs/#/Catalogue/get_catalogue__sessionId__investigation

        :raises RuntimeError: No session ID is available.
        """
        params = {
            "filter": filter,
            "instrumentName": instrument_name,
            "ids": ids,
            "startDate": start_date.strftime("%Y-%m-%d") if start_date else None,
            "endDate": end_date.strftime("%Y-%m-%d") if end_date else None,
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        url = self._investigation_url.format(session_id=self.session_id)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_parcels_by(self, investigation_id: str) -> List[dict]:
        """Returns the list of parcels associated to an investigation.

        :raises RuntimeError: No session ID is available.
        """
        params = {"investigationId": investigation_id}

        url = self._parcel_url.format(session_id=self.session_id)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_datasets_by(
        self, investigation_id: Optional[str] = None, dataset_ids: Optional[str] = None
    ) -> List[dict]:
        """Returns the list of dataset associated to an investigation of by ids.

        API Reference: https://icatplus.esrf.fr/api-docs/#/Catalogue/get_catalogue__sessionId__dataset
        """
        if investigation_id is None and dataset_ids is None:
            raise ValueError(
                "Either 'investigationId' or 'dataset_ids' must be provided."
            )

        params = {"investigationIds": investigation_id, "datasetIds": dataset_ids}
        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        url = self._dataset_url.format(session_id=self.session_id)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_session_information(self) -> dict:
        """Fetches and returns session information from ICAT.

        API Reference: https://icatplus.esrf.fr/api-docs/#/Session/get_session__sessionId_

        :raises RuntimeError: No session ID is available.
        """
        url = self._session_info_url.format(session_id=self.session_id)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_samples_by(
        self,
        investigation_id: Optional[str] = None,
        sample_ids: Optional[str] = None,
        investigationId: Optional[str] = None,  # noqa N803
        sampleIds: Optional[str] = None,  # noqa N803
    ) -> List[dict]:
        """Returns a list of samples matching the provided criteria.

        API Reference: https://icatplus.esrf.fr/api-docs/#/Catalogue/get_catalogue__sessionId__samples
        """
        investigation_id = deprecated_argument(
            "investigation_id", investigation_id, "investigationId", investigationId
        )
        sample_ids = deprecated_argument(
            "sample_ids", investigation_id, "sampleIds", sampleIds
        )

        if investigation_id is None and sample_ids is None:
            raise ValueError(
                "Either 'investigationId' or 'sampleIds' must be provided."
            )

        params = {
            "investigationId": investigation_id,
            "sampleIds": sample_ids,
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        url = self._sample_url.format(session_id=self.session_id)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_sample_metadata_by(
        self, proposal: str, beamline: str
    ) -> List[SampleMetadata]:
        params = {"proposal": proposal, "beamline": beamline}

        url = self._sample_metadata_url.format(session_id=self.session_id)
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
