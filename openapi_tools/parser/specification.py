from dataclasses import dataclass
from typing import Optional

from openapi_parser.specification import Content as BaseContent, String as BaseString


@dataclass
class ContentType:
    value: str


@dataclass
class Content(BaseContent):
    type: ContentType


@dataclass
class Format:
    value: Optional[str] = None


@dataclass
class String(BaseString):
    format: Format
