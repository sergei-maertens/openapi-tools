import logging

from openapi_parser.builders import (
    ContentBuilder as BaseContentBuilder,
    SchemaFactory as BaseSchemaFactory,
)
from openapi_parser.builders.common import PropertyMeta
from openapi_parser.builders.schema import extract_attrs

from .specification import Content, ContentType, Format, String

logger = logging.getLogger(__name__)


class ContentBuilder(BaseContentBuilder):
    def _create_content(self, content_type: str, content_value: dict) -> Content:
        logger.debug(f"Content building [type={content_type}]")
        return Content(
            type=ContentType(content_type),
            schema=self.schema_factory.create(content_value),
        )


class SchemaFactory(BaseSchemaFactory):
    @staticmethod
    def _string(data: dict) -> String:
        attrs_map = {
            "max_length": PropertyMeta(name="maxLength", cast=int),
            "min_length": PropertyMeta(name="minLength", cast=int),
            "pattern": PropertyMeta(name="pattern", cast=None),
            "format": PropertyMeta(name="format", cast=Format),
        }
        return String(**extract_attrs(data, attrs_map))
