from google.protobuf import struct_pb2 as _struct_pb2
from opensearch.protobufs.schemas import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TotalHitsRelation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TOTAL_HITS_RELATION_UNSPECIFIED: _ClassVar[TotalHitsRelation]
    TOTAL_HITS_RELATION_EQ: _ClassVar[TotalHitsRelation]
    TOTAL_HITS_RELATION_GTE: _ClassVar[TotalHitsRelation]

class ClusterSearchStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLUSTER_SEARCH_STATUS_UNSPECIFIED: _ClassVar[ClusterSearchStatus]
    CLUSTER_SEARCH_STATUS_FAILED: _ClassVar[ClusterSearchStatus]
    CLUSTER_SEARCH_STATUS_PARTIAL: _ClassVar[ClusterSearchStatus]
    CLUSTER_SEARCH_STATUS_RUNNING: _ClassVar[ClusterSearchStatus]
    CLUSTER_SEARCH_STATUS_SKIPPED: _ClassVar[ClusterSearchStatus]
    CLUSTER_SEARCH_STATUS_SUCCESSFUL: _ClassVar[ClusterSearchStatus]

class ScoreMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCORE_MODE_UNSPECIFIED: _ClassVar[ScoreMode]
    SCORE_MODE_AVG: _ClassVar[ScoreMode]
    SCORE_MODE_MAX: _ClassVar[ScoreMode]
    SCORE_MODE_MIN: _ClassVar[ScoreMode]
    SCORE_MODE_MULTIPLY: _ClassVar[ScoreMode]
    SCORE_MODE_TOTAL: _ClassVar[ScoreMode]
TOTAL_HITS_RELATION_UNSPECIFIED: TotalHitsRelation
TOTAL_HITS_RELATION_EQ: TotalHitsRelation
TOTAL_HITS_RELATION_GTE: TotalHitsRelation
CLUSTER_SEARCH_STATUS_UNSPECIFIED: ClusterSearchStatus
CLUSTER_SEARCH_STATUS_FAILED: ClusterSearchStatus
CLUSTER_SEARCH_STATUS_PARTIAL: ClusterSearchStatus
CLUSTER_SEARCH_STATUS_RUNNING: ClusterSearchStatus
CLUSTER_SEARCH_STATUS_SKIPPED: ClusterSearchStatus
CLUSTER_SEARCH_STATUS_SUCCESSFUL: ClusterSearchStatus
SCORE_MODE_UNSPECIFIED: ScoreMode
SCORE_MODE_AVG: ScoreMode
SCORE_MODE_MAX: ScoreMode
SCORE_MODE_MIN: ScoreMode
SCORE_MODE_MULTIPLY: ScoreMode
SCORE_MODE_TOTAL: ScoreMode

class SearchRequest(_message.Message):
    __slots__ = ("index", "x_source", "x_source_excludes", "x_source_includes", "allow_no_indices", "allow_partial_search_results", "analyze_wildcard", "batched_reduce_size", "cancel_after_time_interval", "ccs_minimize_roundtrips", "default_operator", "df", "docvalue_fields", "expand_wildcards", "ignore_throttled", "ignore_unavailable", "max_concurrent_shard_requests", "phase_took", "pre_filter_shard_size", "preference", "q", "request_cache", "total_hits_as_int", "routing", "scroll", "search_type", "suggest_field", "suggest_mode", "suggest_size", "suggest_text", "typed_keys", "search_request_body", "global_params")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_INCLUDES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_NO_INDICES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SEARCH_RESULTS_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_WILDCARD_FIELD_NUMBER: _ClassVar[int]
    BATCHED_REDUCE_SIZE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_AFTER_TIME_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    CCS_MINIMIZE_ROUNDTRIPS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_OPERATOR_FIELD_NUMBER: _ClassVar[int]
    DF_FIELD_NUMBER: _ClassVar[int]
    DOCVALUE_FIELDS_FIELD_NUMBER: _ClassVar[int]
    EXPAND_WILDCARDS_FIELD_NUMBER: _ClassVar[int]
    IGNORE_THROTTLED_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_CONCURRENT_SHARD_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    PHASE_TOOK_FIELD_NUMBER: _ClassVar[int]
    PRE_FILTER_SHARD_SIZE_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    REQUEST_CACHE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_HITS_AS_INT_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    SCROLL_FIELD_NUMBER: _ClassVar[int]
    SEARCH_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUGGEST_FIELD_FIELD_NUMBER: _ClassVar[int]
    SUGGEST_MODE_FIELD_NUMBER: _ClassVar[int]
    SUGGEST_SIZE_FIELD_NUMBER: _ClassVar[int]
    SUGGEST_TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPED_KEYS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_REQUEST_BODY_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_PARAMS_FIELD_NUMBER: _ClassVar[int]
    index: _containers.RepeatedScalarFieldContainer[str]
    x_source: _common_pb2.SourceConfigParam
    x_source_excludes: _containers.RepeatedScalarFieldContainer[str]
    x_source_includes: _containers.RepeatedScalarFieldContainer[str]
    allow_no_indices: bool
    allow_partial_search_results: bool
    analyze_wildcard: bool
    batched_reduce_size: int
    cancel_after_time_interval: str
    ccs_minimize_roundtrips: bool
    default_operator: _common_pb2.Operator
    df: str
    docvalue_fields: _containers.RepeatedScalarFieldContainer[str]
    expand_wildcards: _containers.RepeatedScalarFieldContainer[_common_pb2.ExpandWildcard]
    ignore_throttled: bool
    ignore_unavailable: bool
    max_concurrent_shard_requests: int
    phase_took: bool
    pre_filter_shard_size: int
    preference: str
    q: str
    request_cache: bool
    total_hits_as_int: bool
    routing: _containers.RepeatedScalarFieldContainer[str]
    scroll: str
    search_type: _common_pb2.SearchType
    suggest_field: str
    suggest_mode: _common_pb2.SuggestMode
    suggest_size: int
    suggest_text: str
    typed_keys: bool
    search_request_body: SearchRequestBody
    global_params: _common_pb2.GlobalParams
    def __init__(self, index: _Optional[_Iterable[str]] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfigParam, _Mapping]] = ..., x_source_excludes: _Optional[_Iterable[str]] = ..., x_source_includes: _Optional[_Iterable[str]] = ..., allow_no_indices: bool = ..., allow_partial_search_results: bool = ..., analyze_wildcard: bool = ..., batched_reduce_size: _Optional[int] = ..., cancel_after_time_interval: _Optional[str] = ..., ccs_minimize_roundtrips: bool = ..., default_operator: _Optional[_Union[_common_pb2.Operator, str]] = ..., df: _Optional[str] = ..., docvalue_fields: _Optional[_Iterable[str]] = ..., expand_wildcards: _Optional[_Iterable[_Union[_common_pb2.ExpandWildcard, str]]] = ..., ignore_throttled: bool = ..., ignore_unavailable: bool = ..., max_concurrent_shard_requests: _Optional[int] = ..., phase_took: bool = ..., pre_filter_shard_size: _Optional[int] = ..., preference: _Optional[str] = ..., q: _Optional[str] = ..., request_cache: bool = ..., total_hits_as_int: bool = ..., routing: _Optional[_Iterable[str]] = ..., scroll: _Optional[str] = ..., search_type: _Optional[_Union[_common_pb2.SearchType, str]] = ..., suggest_field: _Optional[str] = ..., suggest_mode: _Optional[_Union[_common_pb2.SuggestMode, str]] = ..., suggest_size: _Optional[int] = ..., suggest_text: _Optional[str] = ..., typed_keys: bool = ..., search_request_body: _Optional[_Union[SearchRequestBody, _Mapping]] = ..., global_params: _Optional[_Union[_common_pb2.GlobalParams, _Mapping]] = ...) -> None: ...

class SearchRequestBody(_message.Message):
    __slots__ = ("collapse", "explain", "ext", "highlight", "track_total_hits", "indices_boost", "docvalue_fields", "min_score", "post_filter", "profile", "search_pipeline", "verbose_pipeline", "query", "rescore", "script_fields", "search_after", "size", "slice", "sort", "x_source", "fields", "suggest", "terminate_after", "timeout", "track_scores", "include_named_queries_score", "version", "seq_no_primary_term", "stored_fields", "pit", "stats", "derived")
    class IndicesBoostEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    class ScriptFieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.ScriptField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.ScriptField, _Mapping]] = ...) -> None: ...
    class DerivedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DerivedField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DerivedField, _Mapping]] = ...) -> None: ...
    COLLAPSE_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    EXT_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_FIELD_NUMBER: _ClassVar[int]
    TRACK_TOTAL_HITS_FIELD_NUMBER: _ClassVar[int]
    INDICES_BOOST_FIELD_NUMBER: _ClassVar[int]
    DOCVALUE_FIELDS_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    POST_FILTER_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PIPELINE_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_PIPELINE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    RESCORE_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_AFTER_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SLICE_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    SUGGEST_FIELD_NUMBER: _ClassVar[int]
    TERMINATE_AFTER_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    TRACK_SCORES_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_NAMED_QUERIES_SCORE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SEQ_NO_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    STORED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    PIT_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    DERIVED_FIELD_NUMBER: _ClassVar[int]
    collapse: _common_pb2.FieldCollapse
    explain: bool
    ext: _common_pb2.ObjectMap
    highlight: _common_pb2.Highlight
    track_total_hits: TrackHits
    indices_boost: _containers.ScalarMap[str, float]
    docvalue_fields: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldAndFormat]
    min_score: float
    post_filter: _common_pb2.QueryContainer
    profile: bool
    search_pipeline: str
    verbose_pipeline: bool
    query: _common_pb2.QueryContainer
    rescore: _containers.RepeatedCompositeFieldContainer[Rescore]
    script_fields: _containers.MessageMap[str, _common_pb2.ScriptField]
    search_after: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldValue]
    size: int
    slice: SlicedScroll
    sort: _containers.RepeatedCompositeFieldContainer[_common_pb2.SortCombinations]
    x_source: _common_pb2.SourceConfig
    fields: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldAndFormat]
    suggest: Suggester
    terminate_after: int
    timeout: str
    track_scores: bool
    include_named_queries_score: bool
    version: bool
    seq_no_primary_term: bool
    stored_fields: _containers.RepeatedScalarFieldContainer[str]
    pit: PointInTimeReference
    stats: _containers.RepeatedScalarFieldContainer[str]
    derived: _containers.MessageMap[str, DerivedField]
    def __init__(self, collapse: _Optional[_Union[_common_pb2.FieldCollapse, _Mapping]] = ..., explain: bool = ..., ext: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., highlight: _Optional[_Union[_common_pb2.Highlight, _Mapping]] = ..., track_total_hits: _Optional[_Union[TrackHits, _Mapping]] = ..., indices_boost: _Optional[_Mapping[str, float]] = ..., docvalue_fields: _Optional[_Iterable[_Union[_common_pb2.FieldAndFormat, _Mapping]]] = ..., min_score: _Optional[float] = ..., post_filter: _Optional[_Union[_common_pb2.QueryContainer, _Mapping]] = ..., profile: bool = ..., search_pipeline: _Optional[str] = ..., verbose_pipeline: bool = ..., query: _Optional[_Union[_common_pb2.QueryContainer, _Mapping]] = ..., rescore: _Optional[_Iterable[_Union[Rescore, _Mapping]]] = ..., script_fields: _Optional[_Mapping[str, _common_pb2.ScriptField]] = ..., search_after: _Optional[_Iterable[_Union[_common_pb2.FieldValue, _Mapping]]] = ..., size: _Optional[int] = ..., slice: _Optional[_Union[SlicedScroll, _Mapping]] = ..., sort: _Optional[_Iterable[_Union[_common_pb2.SortCombinations, _Mapping]]] = ..., x_source: _Optional[_Union[_common_pb2.SourceConfig, _Mapping]] = ..., fields: _Optional[_Iterable[_Union[_common_pb2.FieldAndFormat, _Mapping]]] = ..., suggest: _Optional[_Union[Suggester, _Mapping]] = ..., terminate_after: _Optional[int] = ..., timeout: _Optional[str] = ..., track_scores: bool = ..., include_named_queries_score: bool = ..., version: bool = ..., seq_no_primary_term: bool = ..., stored_fields: _Optional[_Iterable[str]] = ..., pit: _Optional[_Union[PointInTimeReference, _Mapping]] = ..., stats: _Optional[_Iterable[str]] = ..., derived: _Optional[_Mapping[str, DerivedField]] = ..., **kwargs) -> None: ...

class DerivedField(_message.Message):
    __slots__ = ("name", "type", "script", "prefilter_field", "properties", "ignore_malformed", "format")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.ObjectMap
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    PREFILTER_FIELD_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    IGNORE_MALFORMED_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    script: _common_pb2.Script
    prefilter_field: str
    properties: _containers.MessageMap[str, _common_pb2.ObjectMap]
    ignore_malformed: bool
    format: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., script: _Optional[_Union[_common_pb2.Script, _Mapping]] = ..., prefilter_field: _Optional[str] = ..., properties: _Optional[_Mapping[str, _common_pb2.ObjectMap]] = ..., ignore_malformed: bool = ..., format: _Optional[str] = ...) -> None: ...

class TrackHits(_message.Message):
    __slots__ = ("enabled", "count")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    count: int
    def __init__(self, enabled: bool = ..., count: _Optional[int] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("took", "timed_out", "x_shards", "phase_took", "hits", "processor_results", "x_clusters", "fields", "num_reduce_phases", "profile", "pit_id", "x_scroll_id", "terminated_early")
    TOOK_FIELD_NUMBER: _ClassVar[int]
    TIMED_OUT_FIELD_NUMBER: _ClassVar[int]
    X_SHARDS_FIELD_NUMBER: _ClassVar[int]
    PHASE_TOOK_FIELD_NUMBER: _ClassVar[int]
    HITS_FIELD_NUMBER: _ClassVar[int]
    PROCESSOR_RESULTS_FIELD_NUMBER: _ClassVar[int]
    X_CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    NUM_REDUCE_PHASES_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    PIT_ID_FIELD_NUMBER: _ClassVar[int]
    X_SCROLL_ID_FIELD_NUMBER: _ClassVar[int]
    TERMINATED_EARLY_FIELD_NUMBER: _ClassVar[int]
    took: int
    timed_out: bool
    x_shards: _common_pb2.ShardStatistics
    phase_took: PhaseTook
    hits: HitsMetadata
    processor_results: _containers.RepeatedCompositeFieldContainer[ProcessorExecutionDetail]
    x_clusters: ClusterStatistics
    fields: _common_pb2.ObjectMap
    num_reduce_phases: int
    profile: Profile
    pit_id: str
    x_scroll_id: str
    terminated_early: bool
    def __init__(self, took: _Optional[int] = ..., timed_out: bool = ..., x_shards: _Optional[_Union[_common_pb2.ShardStatistics, _Mapping]] = ..., phase_took: _Optional[_Union[PhaseTook, _Mapping]] = ..., hits: _Optional[_Union[HitsMetadata, _Mapping]] = ..., processor_results: _Optional[_Iterable[_Union[ProcessorExecutionDetail, _Mapping]]] = ..., x_clusters: _Optional[_Union[ClusterStatistics, _Mapping]] = ..., fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., num_reduce_phases: _Optional[int] = ..., profile: _Optional[_Union[Profile, _Mapping]] = ..., pit_id: _Optional[str] = ..., x_scroll_id: _Optional[str] = ..., terminated_early: bool = ...) -> None: ...

class ProcessorExecutionDetail(_message.Message):
    __slots__ = ("processor_name", "duration_millis", "input_data", "output_data", "status", "tag", "error")
    PROCESSOR_NAME_FIELD_NUMBER: _ClassVar[int]
    DURATION_MILLIS_FIELD_NUMBER: _ClassVar[int]
    INPUT_DATA_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    processor_name: str
    duration_millis: int
    input_data: _common_pb2.ObjectMap
    output_data: _common_pb2.ObjectMap
    status: str
    tag: str
    error: str
    def __init__(self, processor_name: _Optional[str] = ..., duration_millis: _Optional[int] = ..., input_data: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., output_data: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., status: _Optional[str] = ..., tag: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class PhaseTook(_message.Message):
    __slots__ = ("dfs_pre_query", "query", "fetch", "dfs_query", "expand", "can_match")
    DFS_PRE_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    FETCH_FIELD_NUMBER: _ClassVar[int]
    DFS_QUERY_FIELD_NUMBER: _ClassVar[int]
    EXPAND_FIELD_NUMBER: _ClassVar[int]
    CAN_MATCH_FIELD_NUMBER: _ClassVar[int]
    dfs_pre_query: int
    query: int
    fetch: int
    dfs_query: int
    expand: int
    can_match: int
    def __init__(self, dfs_pre_query: _Optional[int] = ..., query: _Optional[int] = ..., fetch: _Optional[int] = ..., dfs_query: _Optional[int] = ..., expand: _Optional[int] = ..., can_match: _Optional[int] = ...) -> None: ...

class HitsMetadataTotal(_message.Message):
    __slots__ = ("total_hits", "int64")
    TOTAL_HITS_FIELD_NUMBER: _ClassVar[int]
    INT64_FIELD_NUMBER: _ClassVar[int]
    total_hits: TotalHits
    int64: int
    def __init__(self, total_hits: _Optional[_Union[TotalHits, _Mapping]] = ..., int64: _Optional[int] = ...) -> None: ...

class HitsMetadataMaxScore(_message.Message):
    __slots__ = ("float", "null_value")
    FLOAT_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    float: float
    null_value: _common_pb2.NullValue
    def __init__(self, float: _Optional[float] = ..., null_value: _Optional[_Union[_common_pb2.NullValue, str]] = ...) -> None: ...

class HitsMetadata(_message.Message):
    __slots__ = ("total", "hits", "max_score")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    HITS_FIELD_NUMBER: _ClassVar[int]
    MAX_SCORE_FIELD_NUMBER: _ClassVar[int]
    total: HitsMetadataTotal
    hits: _containers.RepeatedCompositeFieldContainer[HitsMetadataHitsInner]
    max_score: HitsMetadataMaxScore
    def __init__(self, total: _Optional[_Union[HitsMetadataTotal, _Mapping]] = ..., hits: _Optional[_Iterable[_Union[HitsMetadataHitsInner, _Mapping]]] = ..., max_score: _Optional[_Union[HitsMetadataMaxScore, _Mapping]] = ...) -> None: ...

class TotalHits(_message.Message):
    __slots__ = ("relation", "value")
    RELATION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    relation: TotalHitsRelation
    value: int
    def __init__(self, relation: _Optional[_Union[TotalHitsRelation, str]] = ..., value: _Optional[int] = ...) -> None: ...

class InnerHitsResult(_message.Message):
    __slots__ = ("hits",)
    HITS_FIELD_NUMBER: _ClassVar[int]
    hits: HitsMetadata
    def __init__(self, hits: _Optional[_Union[HitsMetadata, _Mapping]] = ...) -> None: ...

class HitXScore(_message.Message):
    __slots__ = ("null_value", "double")
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    null_value: _common_pb2.NullValue
    double: float
    def __init__(self, null_value: _Optional[_Union[_common_pb2.NullValue, str]] = ..., double: _Optional[float] = ...) -> None: ...

class HitsMetadataHitsInner(_message.Message):
    __slots__ = ("x_type", "x_index", "x_id", "x_score", "explanation", "fields", "highlight", "inner_hits", "matched_queries", "x_nested", "x_ignored", "ignored_field_values", "x_shard", "x_node", "x_routing", "x_source", "x_seq_no", "x_primary_term", "x_version", "sort", "meta_fields")
    class HighlightEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.StringArray
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.StringArray, _Mapping]] = ...) -> None: ...
    class InnerHitsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: InnerHitsResult
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[InnerHitsResult, _Mapping]] = ...) -> None: ...
    class IgnoredFieldValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.StringArray
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.StringArray, _Mapping]] = ...) -> None: ...
    X_TYPE_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_FIELD_NUMBER: _ClassVar[int]
    X_ID_FIELD_NUMBER: _ClassVar[int]
    X_SCORE_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_FIELD_NUMBER: _ClassVar[int]
    INNER_HITS_FIELD_NUMBER: _ClassVar[int]
    MATCHED_QUERIES_FIELD_NUMBER: _ClassVar[int]
    X_NESTED_FIELD_NUMBER: _ClassVar[int]
    X_IGNORED_FIELD_NUMBER: _ClassVar[int]
    IGNORED_FIELD_VALUES_FIELD_NUMBER: _ClassVar[int]
    X_SHARD_FIELD_NUMBER: _ClassVar[int]
    X_NODE_FIELD_NUMBER: _ClassVar[int]
    X_ROUTING_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    X_VERSION_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    META_FIELDS_FIELD_NUMBER: _ClassVar[int]
    x_type: str
    x_index: str
    x_id: str
    x_score: HitXScore
    explanation: Explanation
    fields: _common_pb2.ObjectMap
    highlight: _containers.MessageMap[str, _common_pb2.StringArray]
    inner_hits: _containers.MessageMap[str, InnerHitsResult]
    matched_queries: _containers.RepeatedScalarFieldContainer[str]
    x_nested: NestedIdentity
    x_ignored: _containers.RepeatedScalarFieldContainer[str]
    ignored_field_values: _containers.MessageMap[str, _common_pb2.StringArray]
    x_shard: str
    x_node: str
    x_routing: str
    x_source: bytes
    x_seq_no: int
    x_primary_term: int
    x_version: int
    sort: _containers.RepeatedCompositeFieldContainer[_common_pb2.FieldValue]
    meta_fields: _common_pb2.ObjectMap
    def __init__(self, x_type: _Optional[str] = ..., x_index: _Optional[str] = ..., x_id: _Optional[str] = ..., x_score: _Optional[_Union[HitXScore, _Mapping]] = ..., explanation: _Optional[_Union[Explanation, _Mapping]] = ..., fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ..., highlight: _Optional[_Mapping[str, _common_pb2.StringArray]] = ..., inner_hits: _Optional[_Mapping[str, InnerHitsResult]] = ..., matched_queries: _Optional[_Iterable[str]] = ..., x_nested: _Optional[_Union[NestedIdentity, _Mapping]] = ..., x_ignored: _Optional[_Iterable[str]] = ..., ignored_field_values: _Optional[_Mapping[str, _common_pb2.StringArray]] = ..., x_shard: _Optional[str] = ..., x_node: _Optional[str] = ..., x_routing: _Optional[str] = ..., x_source: _Optional[bytes] = ..., x_seq_no: _Optional[int] = ..., x_primary_term: _Optional[int] = ..., x_version: _Optional[int] = ..., sort: _Optional[_Iterable[_Union[_common_pb2.FieldValue, _Mapping]]] = ..., meta_fields: _Optional[_Union[_common_pb2.ObjectMap, _Mapping]] = ...) -> None: ...

class ClusterStatistics(_message.Message):
    __slots__ = ("skipped", "successful", "total")
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    skipped: int
    successful: int
    total: int
    def __init__(self, skipped: _Optional[int] = ..., successful: _Optional[int] = ..., total: _Optional[int] = ...) -> None: ...

class ClusterDetails(_message.Message):
    __slots__ = ("status", "indices", "took", "timed_out", "shards", "failures")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INDICES_FIELD_NUMBER: _ClassVar[int]
    TOOK_FIELD_NUMBER: _ClassVar[int]
    TIMED_OUT_FIELD_NUMBER: _ClassVar[int]
    SHARDS_FIELD_NUMBER: _ClassVar[int]
    FAILURES_FIELD_NUMBER: _ClassVar[int]
    status: ClusterSearchStatus
    indices: str
    took: int
    timed_out: bool
    shards: _common_pb2.ShardStatistics
    failures: _containers.RepeatedCompositeFieldContainer[_common_pb2.ShardSearchFailure]
    def __init__(self, status: _Optional[_Union[ClusterSearchStatus, str]] = ..., indices: _Optional[str] = ..., took: _Optional[int] = ..., timed_out: bool = ..., shards: _Optional[_Union[_common_pb2.ShardStatistics, _Mapping]] = ..., failures: _Optional[_Iterable[_Union[_common_pb2.ShardSearchFailure, _Mapping]]] = ...) -> None: ...

class Profile(_message.Message):
    __slots__ = ("shards",)
    SHARDS_FIELD_NUMBER: _ClassVar[int]
    shards: _containers.RepeatedCompositeFieldContainer[ShardProfile]
    def __init__(self, shards: _Optional[_Iterable[_Union[ShardProfile, _Mapping]]] = ...) -> None: ...

class RescoreQuery(_message.Message):
    __slots__ = ("rescore_query", "query_weight", "rescore_query_weight", "score_mode")
    RESCORE_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    RESCORE_QUERY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SCORE_MODE_FIELD_NUMBER: _ClassVar[int]
    rescore_query: _common_pb2.QueryContainer
    query_weight: float
    rescore_query_weight: float
    score_mode: ScoreMode
    def __init__(self, rescore_query: _Optional[_Union[_common_pb2.QueryContainer, _Mapping]] = ..., query_weight: _Optional[float] = ..., rescore_query_weight: _Optional[float] = ..., score_mode: _Optional[_Union[ScoreMode, str]] = ...) -> None: ...

class Rescore(_message.Message):
    __slots__ = ("query", "window_size")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    query: RescoreQuery
    window_size: int
    def __init__(self, query: _Optional[_Union[RescoreQuery, _Mapping]] = ..., window_size: _Optional[int] = ...) -> None: ...

class SlicedScroll(_message.Message):
    __slots__ = ("field", "id", "max")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    field: str
    id: int
    max: int
    def __init__(self, field: _Optional[str] = ..., id: _Optional[int] = ..., max: _Optional[int] = ...) -> None: ...

class Suggester(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class ShardProfile(_message.Message):
    __slots__ = ("aggregations", "id", "searches", "fetch")
    AGGREGATIONS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SEARCHES_FIELD_NUMBER: _ClassVar[int]
    FETCH_FIELD_NUMBER: _ClassVar[int]
    aggregations: _containers.RepeatedCompositeFieldContainer[AggregationProfile]
    id: str
    searches: _containers.RepeatedCompositeFieldContainer[SearchProfile]
    fetch: FetchProfile
    def __init__(self, aggregations: _Optional[_Iterable[_Union[AggregationProfile, _Mapping]]] = ..., id: _Optional[str] = ..., searches: _Optional[_Iterable[_Union[SearchProfile, _Mapping]]] = ..., fetch: _Optional[_Union[FetchProfile, _Mapping]] = ...) -> None: ...

class AggregationProfile(_message.Message):
    __slots__ = ("breakdown", "description", "time_in_nanos", "type", "debug", "children")
    BREAKDOWN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_NANOS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    breakdown: AggregationBreakdown
    description: str
    time_in_nanos: int
    type: str
    debug: AggregationProfileDebug
    children: _containers.RepeatedCompositeFieldContainer[AggregationProfile]
    def __init__(self, breakdown: _Optional[_Union[AggregationBreakdown, _Mapping]] = ..., description: _Optional[str] = ..., time_in_nanos: _Optional[int] = ..., type: _Optional[str] = ..., debug: _Optional[_Union[AggregationProfileDebug, _Mapping]] = ..., children: _Optional[_Iterable[_Union[AggregationProfile, _Mapping]]] = ...) -> None: ...

class AggregationBreakdown(_message.Message):
    __slots__ = ("build_aggregation", "build_aggregation_count", "build_leaf_collector", "build_leaf_collector_count", "collect", "collect_count", "initialize", "initialize_count", "post_collection", "post_collection_count", "reduce", "reduce_count")
    BUILD_AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    BUILD_AGGREGATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    BUILD_LEAF_COLLECTOR_FIELD_NUMBER: _ClassVar[int]
    BUILD_LEAF_COLLECTOR_COUNT_FIELD_NUMBER: _ClassVar[int]
    COLLECT_FIELD_NUMBER: _ClassVar[int]
    COLLECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    INITIALIZE_COUNT_FIELD_NUMBER: _ClassVar[int]
    POST_COLLECTION_FIELD_NUMBER: _ClassVar[int]
    POST_COLLECTION_COUNT_FIELD_NUMBER: _ClassVar[int]
    REDUCE_FIELD_NUMBER: _ClassVar[int]
    REDUCE_COUNT_FIELD_NUMBER: _ClassVar[int]
    build_aggregation: int
    build_aggregation_count: int
    build_leaf_collector: int
    build_leaf_collector_count: int
    collect: int
    collect_count: int
    initialize: int
    initialize_count: int
    post_collection: int
    post_collection_count: int
    reduce: int
    reduce_count: int
    def __init__(self, build_aggregation: _Optional[int] = ..., build_aggregation_count: _Optional[int] = ..., build_leaf_collector: _Optional[int] = ..., build_leaf_collector_count: _Optional[int] = ..., collect: _Optional[int] = ..., collect_count: _Optional[int] = ..., initialize: _Optional[int] = ..., initialize_count: _Optional[int] = ..., post_collection: _Optional[int] = ..., post_collection_count: _Optional[int] = ..., reduce: _Optional[int] = ..., reduce_count: _Optional[int] = ...) -> None: ...

class SearchProfile(_message.Message):
    __slots__ = ("collector", "query", "rewrite_time")
    COLLECTOR_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    REWRITE_TIME_FIELD_NUMBER: _ClassVar[int]
    collector: _containers.RepeatedCompositeFieldContainer[Collector]
    query: _containers.RepeatedCompositeFieldContainer[QueryProfile]
    rewrite_time: int
    def __init__(self, collector: _Optional[_Iterable[_Union[Collector, _Mapping]]] = ..., query: _Optional[_Iterable[_Union[QueryProfile, _Mapping]]] = ..., rewrite_time: _Optional[int] = ...) -> None: ...

class NumberMap(_message.Message):
    __slots__ = ("number_map",)
    class NumberMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    NUMBER_MAP_FIELD_NUMBER: _ClassVar[int]
    number_map: _containers.ScalarMap[str, float]
    def __init__(self, number_map: _Optional[_Mapping[str, float]] = ...) -> None: ...

class PointInTimeReference(_message.Message):
    __slots__ = ("id", "keep_alive")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEEP_ALIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    keep_alive: str
    def __init__(self, id: _Optional[str] = ..., keep_alive: _Optional[str] = ...) -> None: ...

class Collector(_message.Message):
    __slots__ = ("name", "reason", "time_in_nanos", "children")
    NAME_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_NANOS_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    name: str
    reason: str
    time_in_nanos: int
    children: _containers.RepeatedCompositeFieldContainer[Collector]
    def __init__(self, name: _Optional[str] = ..., reason: _Optional[str] = ..., time_in_nanos: _Optional[int] = ..., children: _Optional[_Iterable[_Union[Collector, _Mapping]]] = ...) -> None: ...

class QueryProfile(_message.Message):
    __slots__ = ("breakdown", "description", "time_in_nanos", "type", "children")
    BREAKDOWN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_NANOS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    breakdown: QueryBreakdown
    description: str
    time_in_nanos: int
    type: str
    children: _containers.RepeatedCompositeFieldContainer[QueryProfile]
    def __init__(self, breakdown: _Optional[_Union[QueryBreakdown, _Mapping]] = ..., description: _Optional[str] = ..., time_in_nanos: _Optional[int] = ..., type: _Optional[str] = ..., children: _Optional[_Iterable[_Union[QueryProfile, _Mapping]]] = ...) -> None: ...

class QueryBreakdown(_message.Message):
    __slots__ = ("advance", "advance_count", "build_scorer", "build_scorer_count", "create_weight", "create_weight_count", "match", "match_count", "shallow_advance", "shallow_advance_count", "next_doc", "next_doc_count", "score", "score_count", "compute_max_score", "compute_max_score_count", "set_min_competitive_score", "set_min_competitive_score_count")
    ADVANCE_FIELD_NUMBER: _ClassVar[int]
    ADVANCE_COUNT_FIELD_NUMBER: _ClassVar[int]
    BUILD_SCORER_FIELD_NUMBER: _ClassVar[int]
    BUILD_SCORER_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATE_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    CREATE_WEIGHT_COUNT_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    MATCH_COUNT_FIELD_NUMBER: _ClassVar[int]
    SHALLOW_ADVANCE_FIELD_NUMBER: _ClassVar[int]
    SHALLOW_ADVANCE_COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_DOC_FIELD_NUMBER: _ClassVar[int]
    NEXT_DOC_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    SCORE_COUNT_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_MAX_SCORE_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_MAX_SCORE_COUNT_FIELD_NUMBER: _ClassVar[int]
    SET_MIN_COMPETITIVE_SCORE_FIELD_NUMBER: _ClassVar[int]
    SET_MIN_COMPETITIVE_SCORE_COUNT_FIELD_NUMBER: _ClassVar[int]
    advance: int
    advance_count: int
    build_scorer: int
    build_scorer_count: int
    create_weight: int
    create_weight_count: int
    match: int
    match_count: int
    shallow_advance: int
    shallow_advance_count: int
    next_doc: int
    next_doc_count: int
    score: int
    score_count: int
    compute_max_score: int
    compute_max_score_count: int
    set_min_competitive_score: int
    set_min_competitive_score_count: int
    def __init__(self, advance: _Optional[int] = ..., advance_count: _Optional[int] = ..., build_scorer: _Optional[int] = ..., build_scorer_count: _Optional[int] = ..., create_weight: _Optional[int] = ..., create_weight_count: _Optional[int] = ..., match: _Optional[int] = ..., match_count: _Optional[int] = ..., shallow_advance: _Optional[int] = ..., shallow_advance_count: _Optional[int] = ..., next_doc: _Optional[int] = ..., next_doc_count: _Optional[int] = ..., score: _Optional[int] = ..., score_count: _Optional[int] = ..., compute_max_score: _Optional[int] = ..., compute_max_score_count: _Optional[int] = ..., set_min_competitive_score: _Optional[int] = ..., set_min_competitive_score_count: _Optional[int] = ...) -> None: ...

class FetchProfileDebug(_message.Message):
    __slots__ = ("stored_fields", "fast_path")
    STORED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    FAST_PATH_FIELD_NUMBER: _ClassVar[int]
    stored_fields: _containers.RepeatedScalarFieldContainer[str]
    fast_path: int
    def __init__(self, stored_fields: _Optional[_Iterable[str]] = ..., fast_path: _Optional[int] = ...) -> None: ...

class FetchProfile(_message.Message):
    __slots__ = ("type", "description", "time_in_nanos", "breakdown", "debug", "children")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_NANOS_FIELD_NUMBER: _ClassVar[int]
    BREAKDOWN_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    type: str
    description: str
    time_in_nanos: int
    breakdown: FetchProfileBreakdown
    debug: FetchProfileDebug
    children: _containers.RepeatedCompositeFieldContainer[FetchProfile]
    def __init__(self, type: _Optional[str] = ..., description: _Optional[str] = ..., time_in_nanos: _Optional[int] = ..., breakdown: _Optional[_Union[FetchProfileBreakdown, _Mapping]] = ..., debug: _Optional[_Union[FetchProfileDebug, _Mapping]] = ..., children: _Optional[_Iterable[_Union[FetchProfile, _Mapping]]] = ...) -> None: ...

class FetchProfileBreakdown(_message.Message):
    __slots__ = ("load_stored_fields", "load_stored_fields_count", "next_reader", "next_reader_count", "process_count", "process")
    LOAD_STORED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    LOAD_STORED_FIELDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_READER_FIELD_NUMBER: _ClassVar[int]
    NEXT_READER_COUNT_FIELD_NUMBER: _ClassVar[int]
    PROCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    load_stored_fields: int
    load_stored_fields_count: int
    next_reader: int
    next_reader_count: int
    process_count: int
    process: int
    def __init__(self, load_stored_fields: _Optional[int] = ..., load_stored_fields_count: _Optional[int] = ..., next_reader: _Optional[int] = ..., next_reader_count: _Optional[int] = ..., process_count: _Optional[int] = ..., process: _Optional[int] = ...) -> None: ...

class AggregationProfileDebug(_message.Message):
    __slots__ = ("segments_with_multi_valued_ords", "collection_strategy", "segments_with_single_valued_ords", "total_buckets", "built_buckets", "result_strategy", "has_filter", "delegate", "delegate_debug", "chars_fetched", "extract_count", "extract_ns", "values_fetched", "collect_analyzed_ns", "collect_analyzed_count", "surviving_buckets", "ordinals_collectors_used", "ordinals_collectors_overhead_too_high", "string_hashing_collectors_used", "numeric_collectors_used", "empty_collectors_used", "deferred_aggregators", "map_reducer")
    SEGMENTS_WITH_MULTI_VALUED_ORDS_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_WITH_SINGLE_VALUED_ORDS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    BUILT_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    RESULT_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    HAS_FILTER_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_DEBUG_FIELD_NUMBER: _ClassVar[int]
    CHARS_FETCHED_FIELD_NUMBER: _ClassVar[int]
    EXTRACT_COUNT_FIELD_NUMBER: _ClassVar[int]
    EXTRACT_NS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FETCHED_FIELD_NUMBER: _ClassVar[int]
    COLLECT_ANALYZED_NS_FIELD_NUMBER: _ClassVar[int]
    COLLECT_ANALYZED_COUNT_FIELD_NUMBER: _ClassVar[int]
    SURVIVING_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    ORDINALS_COLLECTORS_USED_FIELD_NUMBER: _ClassVar[int]
    ORDINALS_COLLECTORS_OVERHEAD_TOO_HIGH_FIELD_NUMBER: _ClassVar[int]
    STRING_HASHING_COLLECTORS_USED_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_COLLECTORS_USED_FIELD_NUMBER: _ClassVar[int]
    EMPTY_COLLECTORS_USED_FIELD_NUMBER: _ClassVar[int]
    DEFERRED_AGGREGATORS_FIELD_NUMBER: _ClassVar[int]
    MAP_REDUCER_FIELD_NUMBER: _ClassVar[int]
    segments_with_multi_valued_ords: int
    collection_strategy: str
    segments_with_single_valued_ords: int
    total_buckets: int
    built_buckets: int
    result_strategy: str
    has_filter: bool
    delegate: str
    delegate_debug: AggregationProfileDelegateDebug
    chars_fetched: int
    extract_count: int
    extract_ns: int
    values_fetched: int
    collect_analyzed_ns: int
    collect_analyzed_count: int
    surviving_buckets: int
    ordinals_collectors_used: int
    ordinals_collectors_overhead_too_high: int
    string_hashing_collectors_used: int
    numeric_collectors_used: int
    empty_collectors_used: int
    deferred_aggregators: _containers.RepeatedScalarFieldContainer[str]
    map_reducer: str
    def __init__(self, segments_with_multi_valued_ords: _Optional[int] = ..., collection_strategy: _Optional[str] = ..., segments_with_single_valued_ords: _Optional[int] = ..., total_buckets: _Optional[int] = ..., built_buckets: _Optional[int] = ..., result_strategy: _Optional[str] = ..., has_filter: bool = ..., delegate: _Optional[str] = ..., delegate_debug: _Optional[_Union[AggregationProfileDelegateDebug, _Mapping]] = ..., chars_fetched: _Optional[int] = ..., extract_count: _Optional[int] = ..., extract_ns: _Optional[int] = ..., values_fetched: _Optional[int] = ..., collect_analyzed_ns: _Optional[int] = ..., collect_analyzed_count: _Optional[int] = ..., surviving_buckets: _Optional[int] = ..., ordinals_collectors_used: _Optional[int] = ..., ordinals_collectors_overhead_too_high: _Optional[int] = ..., string_hashing_collectors_used: _Optional[int] = ..., numeric_collectors_used: _Optional[int] = ..., empty_collectors_used: _Optional[int] = ..., deferred_aggregators: _Optional[_Iterable[str]] = ..., map_reducer: _Optional[str] = ...) -> None: ...

class AggregationProfileDelegateDebug(_message.Message):
    __slots__ = ("segments_with_doc_count_field", "segments_with_deleted_docs", "filters", "segments_counted", "segments_collected")
    SEGMENTS_WITH_DOC_COUNT_FIELD_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_WITH_DELETED_DOCS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_COUNTED_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_COLLECTED_FIELD_NUMBER: _ClassVar[int]
    segments_with_doc_count_field: int
    segments_with_deleted_docs: int
    filters: _containers.RepeatedCompositeFieldContainer[AggregationProfileDelegateDebugFilter]
    segments_counted: int
    segments_collected: int
    def __init__(self, segments_with_doc_count_field: _Optional[int] = ..., segments_with_deleted_docs: _Optional[int] = ..., filters: _Optional[_Iterable[_Union[AggregationProfileDelegateDebugFilter, _Mapping]]] = ..., segments_counted: _Optional[int] = ..., segments_collected: _Optional[int] = ...) -> None: ...

class AggregationProfileDelegateDebugFilter(_message.Message):
    __slots__ = ("results_from_metadata", "query", "specialized_for", "segments_counted_in_constant_time")
    RESULTS_FROM_METADATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SPECIALIZED_FOR_FIELD_NUMBER: _ClassVar[int]
    SEGMENTS_COUNTED_IN_CONSTANT_TIME_FIELD_NUMBER: _ClassVar[int]
    results_from_metadata: int
    query: str
    specialized_for: str
    segments_counted_in_constant_time: int
    def __init__(self, results_from_metadata: _Optional[int] = ..., query: _Optional[str] = ..., specialized_for: _Optional[str] = ..., segments_counted_in_constant_time: _Optional[int] = ...) -> None: ...

class Explanation(_message.Message):
    __slots__ = ("description", "details", "value")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    description: str
    details: _containers.RepeatedCompositeFieldContainer[Explanation]
    value: float
    def __init__(self, description: _Optional[str] = ..., details: _Optional[_Iterable[_Union[Explanation, _Mapping]]] = ..., value: _Optional[float] = ...) -> None: ...

class NestedIdentity(_message.Message):
    __slots__ = ("field", "offset", "x_nested")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    X_NESTED_FIELD_NUMBER: _ClassVar[int]
    field: str
    offset: int
    x_nested: NestedIdentity
    def __init__(self, field: _Optional[str] = ..., offset: _Optional[int] = ..., x_nested: _Optional[_Union[NestedIdentity, _Mapping]] = ...) -> None: ...
