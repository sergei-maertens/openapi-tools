import logging

from openapi_parser import parse as _parse
from openapi_parser.parser import Specification

logger = logging.getLogger(__name__)


def parse(uri: str) -> Specification:
    return _parse(uri, strict_enum=False)
