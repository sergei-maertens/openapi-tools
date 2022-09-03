import logging

from openapi_parser.builders import (
    ExternalDocBuilder,
    HeaderBuilder,
    InfoBuilder,
    OAuthFlowBuilder,
    OperationBuilder,
    ParameterBuilder,
    PathBuilder,
    RequestBuilder,
    ResponseBuilder,
    SchemasBuilder,
    SecurityBuilder,
    ServerBuilder,
    TagBuilder,
)
from openapi_parser.parser import OpenAPIResolver, Parser, Specification

from .builders import ContentBuilder, SchemaFactory

logger = logging.getLogger(__name__)


def _create_parser() -> Parser:
    logger.info("Initializing parser")
    info_builder = InfoBuilder()
    server_builder = ServerBuilder()
    external_doc_builder = ExternalDocBuilder()
    tag_builder = TagBuilder(external_doc_builder)
    schema_factory = SchemaFactory()
    content_builder = ContentBuilder(schema_factory)
    header_builder = HeaderBuilder(schema_factory)
    parameter_builder = ParameterBuilder(schema_factory)
    schemas_builder = SchemasBuilder(schema_factory)
    response_builder = ResponseBuilder(content_builder, header_builder)
    request_builder = RequestBuilder(content_builder)
    operation_builder = OperationBuilder(
        response_builder, external_doc_builder, request_builder, parameter_builder
    )
    path_builder = PathBuilder(operation_builder, parameter_builder)
    oauth_flow_builder = OAuthFlowBuilder()
    security_builder = SecurityBuilder(oauth_flow_builder)

    return Parser(
        info_builder,
        server_builder,
        tag_builder,
        external_doc_builder,
        path_builder,
        security_builder,
        schemas_builder,
    )


default_parser = _create_parser()


def parse(uri: str, parser: Parser = default_parser) -> Specification:
    resolver = OpenAPIResolver(uri)
    specification = resolver.resolve()
    return parser.load_specification(specification)
