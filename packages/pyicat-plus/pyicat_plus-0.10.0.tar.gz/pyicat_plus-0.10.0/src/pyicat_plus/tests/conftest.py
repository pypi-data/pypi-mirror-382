import pytest

from ..metadata.definitions import load_icat_fields
from .fixtures.icat import *  # noqa F401


@pytest.fixture
def icat_namespace():
    metadict = dict()

    def getter(key):
        return metadict[key]

    def setter(key, value):
        metadict[key] = value

    icat_fields = load_icat_fields()
    metadata = icat_fields.namespace(getter=getter, setter=setter)

    return icat_fields, metadata, metadict
