import os
from typing import List
from typing import Optional

from blissdata.beacon.files import read_config

from .main import IcatClient


def get_icat_client(
    timeout: Optional[float] = None, metadata_urls: Optional[List[str]] = None
) -> IcatClient:
    """
    Create and return an instance of `IcatClient` using configuration retrieved from a Beacon server.
    It is determined from the `BEACON_HOST` environment variable.
    If the configuration is unavailable, a `RuntimeError` is raised.
    :param timeout: optional timeout for the ICAT client operations.
    :param metadata_urls: URLs of the ActiveMQ message brokers to be used for creating
    ICAT datasets from a directory with metadata.
    If provided, these URLs will override the configuration retrieved from Beacon.
    :returns: the ICAT Client.
    """
    beacon_host = os.environ.setdefault("BEACON_HOST", "id00:25000")

    url = f"beacon://{beacon_host}/__init__.yml"
    config = read_config(url).get("icat_servers")

    if not config:
        raise RuntimeError(
            f"Beacon host {beacon_host} does not provide ICAT configuration"
        )
    return IcatClient(
        metadata_urls=metadata_urls if metadata_urls else config["metadata_urls"],
        elogbook_url=config["elogbook_url"],
        elogbook_token=config["elogbook_token"],
        feedback_timeout=timeout,
        add_files_urls=config["metadata_urls"],
    )
