from google.protobuf import struct_pb2 as _struct_pb2
from opensearch.protobufs.schemas import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OP_TYPE_UNSPECIFIED: _ClassVar[OpType]
    OP_TYPE_CREATE: _ClassVar[OpType]
    OP_TYPE_INDEX: _ClassVar[OpType]

class VersionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VERSION_TYPE_UNSPECIFIED: _ClassVar[VersionType]
    VERSION_TYPE_EXTERNAL: _ClassVar[VersionType]
    VERSION_TYPE_EXTERNAL_GTE: _ClassVar[VersionType]
    VERSION_TYPE_INTERNAL: _ClassVar[VersionType]

class ResponseOpType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_OP_TYPE_CREATE: _ClassVar[ResponseOpType]
    RESPONSE_OP_TYPE_INDEX: _ClassVar[ResponseOpType]
    RESPONSE_OP_TYPE_UPDATE: _ClassVar[ResponseOpType]
    RESPONSE_OP_TYPE_DELETE: _ClassVar[ResponseOpType]

class Refresh(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REFRESH_UNSPECIFIED: _ClassVar[Refresh]
    REFRESH_FALSE: _ClassVar[Refresh]
    REFRESH_TRUE: _ClassVar[Refresh]
    REFRESH_WAIT_FOR: _ClassVar[Refresh]

class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_UNSPECIFIED: _ClassVar[Result]
    RESULT_CREATED: _ClassVar[Result]
    RESULT_DELETED: _ClassVar[Result]
    RESULT_NOOP: _ClassVar[Result]
    RESULT_NOT_FOUND: _ClassVar[Result]
    RESULT_UPDATED: _ClassVar[Result]
OP_TYPE_UNSPECIFIED: OpType
OP_TYPE_CREATE: OpType
OP_TYPE_INDEX: OpType
VERSION_TYPE_UNSPECIFIED: VersionType
VERSION_TYPE_EXTERNAL: VersionType
VERSION_TYPE_EXTERNAL_GTE: VersionType
VERSION_TYPE_INTERNAL: VersionType
RESPONSE_OP_TYPE_CREATE: ResponseOpType
RESPONSE_OP_TYPE_INDEX: ResponseOpType
RESPONSE_OP_TYPE_UPDATE: ResponseOpType
RESPONSE_OP_TYPE_DELETE: ResponseOpType
REFRESH_UNSPECIFIED: Refresh
REFRESH_FALSE: Refresh
REFRESH_TRUE: Refresh
REFRESH_WAIT_FOR: Refresh
RESULT_UNSPECIFIED: Result
RESULT_CREATED: Result
RESULT_DELETED: Result
RESULT_NOOP: Result
RESULT_NOT_FOUND: Result
RESULT_UPDATED: Result

class BulkRequest(_message.Message):
    __slots__ = ("index", "x_source", "x_source_excludes", "x_source_includes", "pipeline", "refresh", "require_alias", "routing", "timeout", "type", "wait_for_active_shards", "bulk_request_body", "global_params")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_ACTIVE_SHARDS_FIELD_NUMBER: _ClassVar[int]
    BULK_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    index: str
    x_source: _common_pb2.SourceConfigParam
    x_source_excludes: _containers.RepeatedScalarFieldContainer[str]
    x_source_includes: _containers.RepeatedScalarFieldContainer[str]
    pipeline: str
    refresh: Refresh
    require_alias: bool
    routing: str
    timeout: str
    type: str
    wait_for_active_shards: _common_pb2.WaitForActiveShards
    bulk_request_body: _containers.RepeatedCompositeFieldContainer[BulkRequestBody]
    global_params: _common_pb2.GlobalParams
    def __init__(self, index: _Optional[str] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfigParam, _Mapping]] = ..., x_source_excludes: _Optional[_Iterable[str]] = ..., x_source_includes: _Optional[_Iterable[str]] = ..., pipeline: _Optional[str] = ..., refresh: _Optional[_Union[Refresh, str]] = ..., require_alias: bool = ..., routing: _Optional[str] = ..., timeout: _Optional[str] = ..., type: _Optional[str] = ..., wait_for_active_shards: _Optional[_Union[_common_pb2.WaitForActiveShards, _Mapping]] = ..., bulk_request_body: _Optional[_Iterable[_Union[BulkRequestBody, _Mapping]]] = ..., global_params: _Optional[_Union[_common_pb2.GlobalParams, _Mapping]] = ...) -> None: ...

class BulkRequestBody(_message.Message):
    __slots__ = ("operation_container", "update_action", "object")
    OPERATION_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ACTION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    operation_container: OperationContainer
    update_action: UpdateAction
    object: bytes
    def __init__(self, operation_container: _Optional[_Union[OperationContainer, _Mapping]] = ..., update_action: _Optional[_Union[UpdateAction, _Mapping]] = ..., object: _Optional[bytes] = ...) -> None: ...

class OperationContainer(_message.Message):
    __slots__ = ("index", "create", "update", "delete")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    CREATE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    index: IndexOperation
    create: WriteOperation
    update: UpdateOperation
    delete: DeleteOperation
    def __init__(self, index: _Optional[_Union[IndexOperation, _Mapping]] = ..., create: _Optional[_Union[WriteOperation, _Mapping]] = ..., update: _Optional[_Union[UpdateOperation, _Mapping]] = ..., delete: _Optional[_Union[DeleteOperation, _Mapping]] = ...) -> None: ...

class UpdateAction(_message.Message):
    __slots__ = ("detect_noop", "doc", "doc_as_upsert", "script", "scripted_upsert", "upsert", "x_source")
    DETECT_NOOP_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    DOC_AS_UPSERT_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    SCRIPTED_UPSERT_FIELD_NUMBER: _ClassVar[int]
    UPSERT_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    detect_noop: bool
    doc: bytes
    doc_as_upsert: bool
    script: _common_pb2.Script
    scripted_upsert: bool
    upsert: bytes
    x_source: _common_pb2.SourceConfig
    def __init__(self, detect_noop: bool = ..., doc: _Optional[bytes] = ..., doc_as_upsert: bool = ..., script: _Optional[_Union[_common_pb2.Script, _Mapping]] = ..., scripted_upsert: bool = ..., upsert: _Optional[bytes] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfig, _Mapping]] = ...) -> None: ...

class IndexOperation(_message.Message):
    __slots__ = ("x_id", "x_index", "routing", "if_primary_term", "if_seq_no", "op_type", "version", "version_type", "pipeline", "require_alias")
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    OP_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    x_id: str
    x_index: str
    routing: str
    if_primary_term: int
    if_seq_no: int
    op_type: OpType
    version: int
    version_type: VersionType
    pipeline: str
    require_alias: bool
    def __init__(self, x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., routing: _Optional[str] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., op_type: _Optional[_Union[OpType, str]] = ..., version: _Optional[int] = ..., version_type: _Optional[_Union[VersionType, str]] = ..., pipeline: _Optional[str] = ..., require_alias: bool = ...) -> None: ...

class WriteOperation(_message.Message):
    __slots__ = ("routing", "x_id", "x_index", "pipeline", "require_alias")
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    routing: str
    x_id: str
    x_index: str
    pipeline: str
    require_alias: bool
    def __init__(self, routing: _Optional[str] = ..., x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., pipeline: _Optional[str] = ..., require_alias: bool = ...) -> None: ...

class UpdateOperation(_message.Message):
    __slots__ = ("x_id", "x_index", "routing", "if_primary_term", "if_seq_no", "require_alias", "retry_on_conflict")
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    RETRY_ON_CONFLICT_FIELD_NUMBER: _ClassVar[int]
    x_id: str
    x_index: str
    routing: str
    if_primary_term: int
    if_seq_no: int
    require_alias: bool
    retry_on_conflict: int
    def __init__(self, x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., routing: _Optional[str] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., require_alias: bool = ..., retry_on_conflict: _Optional[int] = ...) -> None: ...

class DeleteOperation(_message.Message):
    __slots__ = ("x_id", "x_index", "routing", "if_primary_term", "if_seq_no", "version", "version_type")
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    x_id: str
    x_index: str
    routing: str
    if_primary_term: int
    if_seq_no: int
    version: int
    version_type: VersionType
    def __init__(self, x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., routing: _Optional[str] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., version: _Optional[int] = ..., version_type: _Optional[_Union[VersionType, str]] = ...) -> None: ...

class BulkResponse(_message.Message):
    __slots__ = ("errors", "items", "took", "ingest_took")
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOOK_FIELD_NUMBER: _ClassVar[int]
    INGEST_TOOK_FIELD_NUMBER: _ClassVar[int]
    errors: bool
    items: _containers.RepeatedCompositeFieldContainer[Item]
    took: int
    ingest_took: int
    def __init__(self, errors: bool = ..., items: _Optional[_Iterable[_Union[Item, _Mapping]]] = ..., took: _Optional[int] = ..., ingest_took: _Optional[int] = ...) -> None: ...

class Item(_message.Message):
    __slots__ = ("create", "delete", "index", "update")
    CREATE_FIELD_NUMBER: _ClassVar[int]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    create: ResponseItem
    delete: ResponseItem
    index: ResponseItem
    update: ResponseItem
    def __init__(self, create: _Optional[_Union[ResponseItem, _Mapping]] = ..., delete: _Optional[_Union[ResponseItem, _Mapping]] = ..., index: _Optional[_Union[ResponseItem, _Mapping]] = ..., update: _Optional[_Union[ResponseItem, _Mapping]] = ...) -> None: ...

class ResponseItem(_message.Message):
    __slots__ = ("x_index", "status", "x_type", "x_id", "error", "x_primary_term", "result", "x_seq_no", "x_shards", "x_version", "forced_refresh", "get")
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_SHARDS_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCED_REFRESH_FIELD_NUMBER: _ClassVar[int]
    GET_FIELD_NUMBER: _ClassVar[int]
    x_index: str
    status: int
    x_type: str
    x_id: _common_pb2.Id
    error: _common_pb2.ErrorCause
    x_primary_term: int
    result: str
    x_seq_no: int
    x_shards: _common_pb2.ShardInfo
    x_version: int
    forced_refresh: bool
    get: InlineGetDictUserDefined
    def __init__(self, x_index: _Optional[str] = ..., status: _Optional[int] = ..., x_type: _Optional[str] = ..., x_id: _Optional[_Union[_common_pb2.Id, _Mapping]] = ..., error: _Optional[_Union[_common_pb2.ErrorCause, _Mapping]] = ..., x_primary_term: _Optional[int] = ..., result: _Optional[str] = ..., x_seq_no: _Optional[int] = ..., x_shards: _Optional[_Union[_common_pb2.ShardInfo, _Mapping]] = ..., x_version: _Optional[int] = ..., forced_refresh: bool = ..., get: _Optional[_Union[InlineGetDictUserDefined, _Mapping]] = ...) -> None: ...

class InlineGetDictUserDefined(_message.Message):
    __slots__ = ("metadata_fields", "fields", "found", "seq_no", "x_primary_term", "x_routing", "x_source")
    METADATA_FIELDS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    X_ROUTING_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    metadata_fields: _common_pb2.ObjectMap
    fields: _common_pb2.ObjectMap
    found: bool
    seq_no: int
    x_primary_term: int
    x_routing: str
    x_source: bytes
    def __init__(self, metadata_fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., found: bool = ..., seq_no: _Optional[int] = ..., x_primary_term: _Optional[int] = ..., x_routing: _Optional[str] = ..., x_source: _Optional[bytes] = ...) -> None: ...

class IndexDocumentRequest(_message.Message):
    __slots__ = ("id", "index", "if_primary_term", "if_seq_no", "op_type", "pipeline", "refresh", "require_alias", "routing", "timeout", "version", "version_type", "wait_for_active_shards", "request_body", "bytes_request_body", "source_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    OP_TYPE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_ACTIVE_SHARDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    BYTES_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: str
    if_primary_term: int
    if_seq_no: int
    op_type: OpType
    pipeline: str
    refresh: Refresh
    require_alias: bool
    routing: str
    timeout: str
    version: int
    version_type: VersionType
    wait_for_active_shards: _common_pb2.WaitForActiveShards
    request_body: _common_pb2.ObjectMap
    bytes_request_body: bytes
    source_type: _common_pb2.SourceType
    def __init__(self, id: _Optional[str] = ..., index: _Optional[str] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., op_type: _Optional[_Union[OpType, str]] = ..., pipeline: _Optional[str] = ..., refresh: _Optional[_Union[Refresh, str]] = ..., require_alias: bool = ..., routing: _Optional[str] = ..., timeout: _Optional[str] = ..., version: _Optional[int] = ..., version_type: _Optional[_Union[VersionType, str]] = ..., wait_for_active_shards: _Optional[_Union[_common_pb2.WaitForActiveShards, _Mapping]] = ..., request_body: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., bytes_request_body: _Optional[bytes] = ..., source_type: _Optional[_Union[_common_pb2.SourceType, str]] = ...) -> None: ...

class IndexDocumentResponse(_message.Message):
    __slots__ = ("index_document_response_body", "index_document_error_response")
    INDEX_DOCUMENT_RESPONSE_BODY_FIELD_NUMBER: _ClassVar[int]
    INDEX_DOCUMENT_ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    index_document_response_body: IndexDocumentResponseBody
    index_document_error_response: IndexDocumentErrorResponse
    def __init__(self, index_document_response_body: _Optional[_Union[IndexDocumentResponseBody, _Mapping]] = ..., index_document_error_response: _Optional[_Union[IndexDocumentErrorResponse, _Mapping]] = ...) -> None: ...

class IndexDocumentErrorResponse(_message.Message):
    __slots__ = ("error", "status")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    status: int
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., status: _Optional[int] = ...) -> None: ...

class IndexDocumentResponseBody(_message.Message):
    __slots__ = ("x_type", "x_id", "x_index", "x_primary_term", "result", "x_seq_no", "x_shards", "x_version", "forced_refresh")
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_SHARDS_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCED_REFRESH_FIELD_NUMBER: _ClassVar[int]
    x_type: str
    x_id: str
    x_index: str
    x_primary_term: int
    result: Result
    x_seq_no: int
    x_shards: _common_pb2.ShardStatistics
    x_version: int
    forced_refresh: bool
    def __init__(self, x_type: _Optional[str] = ..., x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., x_primary_term: _Optional[int] = ..., result: _Optional[_Union[Result, str]] = ..., x_seq_no: _Optional[int] = ..., x_shards: _Optional[_Union[_common_pb2.ShardStatistics, _Mapping]] = ..., x_version: _Optional[int] = ..., forced_refresh: bool = ...) -> None: ...

class DeleteDocumentRequest(_message.Message):
    __slots__ = ("id", "index", "if_primary_term", "if_seq_no", "refresh", "routing", "timeout", "version", "version_type", "wait_for_active_shards")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_ACTIVE_SHARDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: str
    if_primary_term: int
    if_seq_no: int
    refresh: Refresh
    routing: str
    timeout: str
    version: int
    version_type: VersionType
    wait_for_active_shards: _common_pb2.WaitForActiveShards
    def __init__(self, id: _Optional[str] = ..., index: _Optional[str] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., refresh: _Optional[_Union[Refresh, str]] = ..., routing: _Optional[str] = ..., timeout: _Optional[str] = ..., version: _Optional[int] = ..., version_type: _Optional[_Union[VersionType, str]] = ..., wait_for_active_shards: _Optional[_Union[_common_pb2.WaitForActiveShards, _Mapping]] = ...) -> None: ...

class DeleteDocumentResponseBody(_message.Message):
    __slots__ = ("x_type", "x_id", "x_index", "x_primary_term", "result", "x_seq_no", "x_shards", "x_version", "forced_refresh")
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_SHARDS_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCED_REFRESH_FIELD_NUMBER: _ClassVar[int]
    x_type: str
    x_id: str
    x_index: str
    x_primary_term: int
    result: Result
    x_seq_no: int
    x_shards: _common_pb2.ShardStatistics
    x_version: int
    forced_refresh: bool
    def __init__(self, x_type: _Optional[str] = ..., x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., x_primary_term: _Optional[int] = ..., result: _Optional[_Union[Result, str]] = ..., x_seq_no: _Optional[int] = ..., x_shards: _Optional[_Union[_common_pb2.ShardStatistics, _Mapping]] = ..., x_version: _Optional[int] = ..., forced_refresh: bool = ...) -> None: ...

class DeleteDocumentResponse(_message.Message):
    __slots__ = ("delete_document_response_body", "delete_document_error_response")
    DELETE_DOCUMENT_RESPONSE_BODY_FIELD_NUMBER: _ClassVar[int]
    DELETE_DOCUMENT_ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    delete_document_response_body: DeleteDocumentResponseBody
    delete_document_error_response: DeleteDocumentErrorResponse
    def __init__(self, delete_document_response_body: _Optional[_Union[DeleteDocumentResponseBody, _Mapping]] = ..., delete_document_error_response: _Optional[_Union[DeleteDocumentErrorResponse, _Mapping]] = ...) -> None: ...

class DeleteDocumentErrorResponse(_message.Message):
    __slots__ = ("error", "status")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    status: int
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., status: _Optional[int] = ...) -> None: ...

class UpdateDocumentRequest(_message.Message):
    __slots__ = ("id", "index", "x_source", "x_source_excludes", "x_source_includes", "if_primary_term", "if_seq_no", "lang", "refresh", "require_alias", "retry_on_conflict", "routing", "timeout", "wait_for_active_shards", "request_body", "source_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    IF_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    IF_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_ALIAS_FIELD_NUMBER: _ClassVar[int]
    RETRY_ON_CONFLICT_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_ACTIVE_SHARDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: str
    x_source: _common_pb2.SourceConfigParam
    x_source_excludes: _containers.RepeatedScalarFieldContainer[str]
    x_source_includes: _containers.RepeatedScalarFieldContainer[str]
    if_primary_term: int
    if_seq_no: int
    lang: str
    refresh: Refresh
    require_alias: bool
    retry_on_conflict: int
    routing: str
    timeout: str
    wait_for_active_shards: _common_pb2.WaitForActiveShards
    request_body: UpdateDocumentRequestBody
    source_type: _common_pb2.SourceType
    def __init__(self, id: _Optional[str] = ..., index: _Optional[str] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfigParam, _Mapping]] = ..., x_source_excludes: _Optional[_Iterable[str]] = ..., x_source_includes: _Optional[_Iterable[str]] = ..., if_primary_term: _Optional[int] = ..., if_seq_no: _Optional[int] = ..., lang: _Optional[str] = ..., refresh: _Optional[_Union[Refresh, str]] = ..., require_alias: bool = ..., retry_on_conflict: _Optional[int] = ..., routing: _Optional[str] = ..., timeout: _Optional[str] = ..., wait_for_active_shards: _Optional[_Union[_common_pb2.WaitForActiveShards, _Mapping]] = ..., request_body: _Optional[_Union[UpdateDocumentRequestBody, _Mapping]] = ..., source_type: _Optional[_Union[_common_pb2.SourceType, str]] = ...) -> None: ...

class UpdateDocumentRequestBody(_message.Message):
    __slots__ = ("detect_noop", "doc", "bytes_doc", "doc_as_upsert", "script", "scripted_upsert", "x_source", "upsert", "bytes_upsert")
    DETECT_NOOP_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    BYTES_DOC_FIELD_NUMBER: _ClassVar[int]
    DOC_AS_UPSERT_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    SCRIPTED_UPSERT_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    UPSERT_FIELD_NUMBER: _ClassVar[int]
    BYTES_UPSERT_FIELD_NUMBER: _ClassVar[int]
    detect_noop: bool
    doc: _common_pb2.ObjectMap
    bytes_doc: bytes
    doc_as_upsert: bool
    script: _common_pb2.Script
    scripted_upsert: bool
    x_source: _common_pb2.SourceConfig
    upsert: _common_pb2.ObjectMap
    bytes_upsert: bytes
    def __init__(self, detect_noop: bool = ..., doc: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., bytes_doc: _Optional[bytes] = ..., doc_as_upsert: bool = ..., script: _Optional[_Union[_common_pb2.Script, _Mapping]] = ..., scripted_upsert: bool = ..., x_source: _Optional[_Union[_common_pb2.SourceConfig, _Mapping]] = ..., upsert: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., bytes_upsert: _Optional[bytes] = ...) -> None: ...

class UpdateDocumentResponse(_message.Message):
    __slots__ = ("update_document_response_body", "update_document_error_response")
    UPDATE_DOCUMENT_RESPONSE_BODY_FIELD_NUMBER: _ClassVar[int]
    UPDATE_DOCUMENT_ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    update_document_response_body: UpdateDocumentResponseBody
    update_document_error_response: UpdateDocumentErrorResponse
    def __init__(self, update_document_response_body: _Optional[_Union[UpdateDocumentResponseBody, _Mapping]] = ..., update_document_error_response: _Optional[_Union[UpdateDocumentErrorResponse, _Mapping]] = ...) -> None: ...

class UpdateDocumentErrorResponse(_message.Message):
    __slots__ = ("error", "status")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    status: int
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., status: _Optional[int] = ...) -> None: ...

class UpdateDocumentResponseBody(_message.Message):
    __slots__ = ("x_type", "x_id", "x_index", "x_primary_term", "result", "x_seq_no", "x_shards", "x_version", "forced_refresh", "get")
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_SHARDS_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCED_REFRESH_FIELD_NUMBER: _ClassVar[int]
    GET_FIELD_NUMBER: _ClassVar[int]
    x_type: str
    x_id: str
    x_index: str
    x_primary_term: int
    result: Result
    x_seq_no: int
    x_shards: _common_pb2.ShardStatistics
    x_version: int
    forced_refresh: bool
    get: _common_pb2.InlineGet
    def __init__(self, x_type: _Optional[str] = ..., x_id: _Optional[str] = ..., x_index: _Optional[str] = ..., x_primary_term: _Optional[int] = ..., result: _Optional[_Union[Result, str]] = ..., x_seq_no: _Optional[int] = ..., x_shards: _Optional[_Union[_common_pb2.ShardStatistics, _Mapping]] = ..., x_version: _Optional[int] = ..., forced_refresh: bool = ..., get: _Optional[_Union[_common_pb2.InlineGet, _Mapping]] = ...) -> None: ...

class GetDocumentRequest(_message.Message):
    __slots__ = ("id", "index", "x_source", "x_source_excludes", "x_source_includes", "preference", "realtime", "refresh", "routing", "stored_fields", "version", "version_type", "source_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    REALTIME_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    STORED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VERSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    index: str
    x_source: _common_pb2.SourceConfigParam
    x_source_excludes: _containers.RepeatedScalarFieldContainer[str]
    x_source_includes: _containers.RepeatedScalarFieldContainer[str]
    preference: str
    realtime: bool
    refresh: bool
    routing: str
    stored_fields: _containers.RepeatedScalarFieldContainer[str]
    version: int
    version_type: VersionType
    source_type: _common_pb2.SourceType
    def __init__(self, id: _Optional[str] = ..., index: _Optional[str] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfigParam, _Mapping]] = ..., x_source_excludes: _Optional[_Iterable[str]] = ..., x_source_includes: _Optional[_Iterable[str]] = ..., preference: _Optional[str] = ..., realtime: bool = ..., refresh: bool = ..., routing: _Optional[str] = ..., stored_fields: _Optional[_Iterable[str]] = ..., version: _Optional[int] = ..., version_type: _Optional[_Union[VersionType, str]] = ..., source_type: _Optional[_Union[_common_pb2.SourceType, str]] = ...) -> None: ...

class GetDocumentResponseBody(_message.Message):
    __slots__ = ("x_type", "x_index", "fields", "found", "x_id", "x_primary_term", "x_routing", "x_seq_no", "struct_source", "x_source", "x_version")
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    X_ROUTING_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    STRUCT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    x_type: str
    x_index: str
    fields: _common_pb2.ObjectMap
    found: bool
    x_id: str
    x_primary_term: int
    x_routing: str
    x_seq_no: int
    struct_source: _struct_pb2.Struct
    x_source: bytes
    x_version: int
    def __init__(self, x_type: _Optional[str] = ..., x_index: _Optional[str] = ..., fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., found: bool = ..., x_id: _Optional[str] = ..., x_primary_term: _Optional[int] = ..., x_routing: _Optional[str] = ..., x_seq_no: _Optional[int] = ..., struct_source: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., x_source: _Optional[bytes] = ..., x_version: _Optional[int] = ...) -> None: ...

class GetDocumentResponse(_message.Message):
    __slots__ = ("get_document_response_body", "get_document_error_response")
    GET_DOCUMENT_RESPONSE_BODY_FIELD_NUMBER: _ClassVar[int]
    GET_DOCUMENT_ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    get_document_response_body: GetDocumentResponseBody
    get_document_error_response: GetDocumentErrorResponse
    def __init__(self, get_document_response_body: _Optional[_Union[GetDocumentResponseBody, _Mapping]] = ..., get_document_error_response: _Optional[_Union[GetDocumentErrorResponse, _Mapping]] = ...) -> None: ...

class GetDocumentErrorResponse(_message.Message):
    __slots__ = ("error", "status")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    status: int
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., status: _Optional[int] = ...) -> None: ...
