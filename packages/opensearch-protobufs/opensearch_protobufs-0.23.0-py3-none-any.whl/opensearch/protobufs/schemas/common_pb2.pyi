from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WaitForActiveShardOptions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WAIT_FOR_ACTIVE_SHARD_OPTIONS_UNSPECIFIED: _ClassVar[WaitForActiveShardOptions]
    WAIT_FOR_ACTIVE_SHARD_OPTIONS_ALL: _ClassVar[WaitForActiveShardOptions]
    WAIT_FOR_ACTIVE_SHARD_OPTIONS_NULL: _ClassVar[WaitForActiveShardOptions]

class BuiltinScriptLanguage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUILTIN_SCRIPT_LANGUAGE_UNSPECIFIED: _ClassVar[BuiltinScriptLanguage]
    BUILTIN_SCRIPT_LANGUAGE_EXPRESSION: _ClassVar[BuiltinScriptLanguage]
    BUILTIN_SCRIPT_LANGUAGE_JAVA: _ClassVar[BuiltinScriptLanguage]
    BUILTIN_SCRIPT_LANGUAGE_MUSTACHE: _ClassVar[BuiltinScriptLanguage]
    BUILTIN_SCRIPT_LANGUAGE_PAINLESS: _ClassVar[BuiltinScriptLanguage]

class ExpandWildcard(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXPAND_WILDCARD_UNSPECIFIED: _ClassVar[ExpandWildcard]
    EXPAND_WILDCARD_ALL: _ClassVar[ExpandWildcard]
    EXPAND_WILDCARD_CLOSED: _ClassVar[ExpandWildcard]
    EXPAND_WILDCARD_HIDDEN: _ClassVar[ExpandWildcard]
    EXPAND_WILDCARD_NONE: _ClassVar[ExpandWildcard]
    EXPAND_WILDCARD_OPEN: _ClassVar[ExpandWildcard]

class SearchType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEARCH_TYPE_UNSPECIFIED: _ClassVar[SearchType]
    SEARCH_TYPE_DFS_QUERY_THEN_FETCH: _ClassVar[SearchType]
    SEARCH_TYPE_QUERY_THEN_FETCH: _ClassVar[SearchType]

class SuggestMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUGGEST_MODE_UNSPECIFIED: _ClassVar[SuggestMode]
    SUGGEST_MODE_ALWAYS: _ClassVar[SuggestMode]
    SUGGEST_MODE_MISSING: _ClassVar[SuggestMode]
    SUGGEST_MODE_POPULAR: _ClassVar[SuggestMode]

class NullValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NULL_VALUE_UNSPECIFIED: _ClassVar[NullValue]
    NULL_VALUE_NULL: _ClassVar[NullValue]

class SourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOURCE_TYPE_UNSPECIFIED: _ClassVar[SourceType]
    SOURCE_TYPE_STRUCT: _ClassVar[SourceType]

class RuntimeFieldType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RUNTIME_FIELD_TYPE_UNSPECIFIED: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_BOOLEAN: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_DATE: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_DOUBLE: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_GEO_POINT: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_IP: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_KEYWORD: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_LONG: _ClassVar[RuntimeFieldType]
    RUNTIME_FIELD_TYPE_LOOKUP: _ClassVar[RuntimeFieldType]

class GeoExecution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GEO_EXECUTION_UNSPECIFIED: _ClassVar[GeoExecution]
    GEO_EXECUTION_INDEXED: _ClassVar[GeoExecution]
    GEO_EXECUTION_MEMORY: _ClassVar[GeoExecution]

class DistanceUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISTANCE_UNIT_UNSPECIFIED: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_CM: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_FT: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_IN: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_KM: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_M: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_MI: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_MM: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_NMI: _ClassVar[DistanceUnit]
    DISTANCE_UNIT_YD: _ClassVar[DistanceUnit]

class ChildScoreMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHILD_SCORE_MODE_UNSPECIFIED: _ClassVar[ChildScoreMode]
    CHILD_SCORE_MODE_AVG: _ClassVar[ChildScoreMode]
    CHILD_SCORE_MODE_MAX: _ClassVar[ChildScoreMode]
    CHILD_SCORE_MODE_MIN: _ClassVar[ChildScoreMode]
    CHILD_SCORE_MODE_NONE: _ClassVar[ChildScoreMode]
    CHILD_SCORE_MODE_SUM: _ClassVar[ChildScoreMode]

class BuiltinHighlighterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUILTIN_HIGHLIGHTER_TYPE_UNSPECIFIED: _ClassVar[BuiltinHighlighterType]
    BUILTIN_HIGHLIGHTER_TYPE_PLAIN: _ClassVar[BuiltinHighlighterType]
    BUILTIN_HIGHLIGHTER_TYPE_FVH: _ClassVar[BuiltinHighlighterType]
    BUILTIN_HIGHLIGHTER_TYPE_UNIFIED: _ClassVar[BuiltinHighlighterType]

class BoundaryScanner(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BOUNDARY_SCANNER_UNSPECIFIED: _ClassVar[BoundaryScanner]
    BOUNDARY_SCANNER_CHARS: _ClassVar[BoundaryScanner]
    BOUNDARY_SCANNER_SENTENCE: _ClassVar[BoundaryScanner]
    BOUNDARY_SCANNER_WORD: _ClassVar[BoundaryScanner]

class HighlighterFragmenter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HIGHLIGHTER_FRAGMENTER_UNSPECIFIED: _ClassVar[HighlighterFragmenter]
    HIGHLIGHTER_FRAGMENTER_SIMPLE: _ClassVar[HighlighterFragmenter]
    HIGHLIGHTER_FRAGMENTER_SPAN: _ClassVar[HighlighterFragmenter]

class HighlighterOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HIGHLIGHTER_ORDER_UNSPECIFIED: _ClassVar[HighlighterOrder]
    HIGHLIGHTER_ORDER_SCORE: _ClassVar[HighlighterOrder]

class HighlighterTagsSchema(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HIGHLIGHTER_TAGS_SCHEMA_UNSPECIFIED: _ClassVar[HighlighterTagsSchema]
    HIGHLIGHTER_TAGS_SCHEMA_STYLED: _ClassVar[HighlighterTagsSchema]

class HighlighterEncoder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HIGHLIGHTER_ENCODER_UNSPECIFIED: _ClassVar[HighlighterEncoder]
    HIGHLIGHTER_ENCODER_DEFAULT: _ClassVar[HighlighterEncoder]
    HIGHLIGHTER_ENCODER_HTML: _ClassVar[HighlighterEncoder]

class FieldSortNumericType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIELD_SORT_NUMERIC_TYPE_UNSPECIFIED: _ClassVar[FieldSortNumericType]
    FIELD_SORT_NUMERIC_TYPE_DATE: _ClassVar[FieldSortNumericType]
    FIELD_SORT_NUMERIC_TYPE_DATE_NANOS: _ClassVar[FieldSortNumericType]
    FIELD_SORT_NUMERIC_TYPE_DOUBLE: _ClassVar[FieldSortNumericType]
    FIELD_SORT_NUMERIC_TYPE_LONG: _ClassVar[FieldSortNumericType]

class FieldType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIELD_TYPE_UNSPECIFIED: _ClassVar[FieldType]
    FIELD_TYPE_AGGREGATE_METRIC_DOUBLE: _ClassVar[FieldType]
    FIELD_TYPE_ALIAS: _ClassVar[FieldType]
    FIELD_TYPE_BINARY: _ClassVar[FieldType]
    FIELD_TYPE_BOOLEAN: _ClassVar[FieldType]
    FIELD_TYPE_BYTE: _ClassVar[FieldType]
    FIELD_TYPE_COMPLETION: _ClassVar[FieldType]
    FIELD_TYPE_CONSTANT_KEYWORD: _ClassVar[FieldType]
    FIELD_TYPE_DATE: _ClassVar[FieldType]
    FIELD_TYPE_DATE_NANOS: _ClassVar[FieldType]
    FIELD_TYPE_DATE_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_DOUBLE: _ClassVar[FieldType]
    FIELD_TYPE_DOUBLE_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_FLAT_OBJECT: _ClassVar[FieldType]
    FIELD_TYPE_FLOAT: _ClassVar[FieldType]
    FIELD_TYPE_FLOAT_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_GEO_POINT: _ClassVar[FieldType]
    FIELD_TYPE_GEO_SHAPE: _ClassVar[FieldType]
    FIELD_TYPE_HALF_FLOAT: _ClassVar[FieldType]
    FIELD_TYPE_HISTOGRAM: _ClassVar[FieldType]
    FIELD_TYPE_ICU_COLLATION_KEYWORD: _ClassVar[FieldType]
    FIELD_TYPE_INTEGER: _ClassVar[FieldType]
    FIELD_TYPE_INTEGER_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_IP: _ClassVar[FieldType]
    FIELD_TYPE_IP_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_JOIN: _ClassVar[FieldType]
    FIELD_TYPE_KEYWORD: _ClassVar[FieldType]
    FIELD_TYPE_KNN_VECTOR: _ClassVar[FieldType]
    FIELD_TYPE_LONG: _ClassVar[FieldType]
    FIELD_TYPE_LONG_RANGE: _ClassVar[FieldType]
    FIELD_TYPE_MATCH_ONLY_TEXT: _ClassVar[FieldType]
    FIELD_TYPE_MURMUR3: _ClassVar[FieldType]
    FIELD_TYPE_NESTED: _ClassVar[FieldType]
    FIELD_TYPE_OBJECT: _ClassVar[FieldType]
    FIELD_TYPE_PERCOLATOR: _ClassVar[FieldType]
    FIELD_TYPE_RANK_FEATURE: _ClassVar[FieldType]
    FIELD_TYPE_RANK_FEATURES: _ClassVar[FieldType]
    FIELD_TYPE_SCALED_FLOAT: _ClassVar[FieldType]
    FIELD_TYPE_SEARCH_AS_YOU_TYPE: _ClassVar[FieldType]
    FIELD_TYPE_SHORT: _ClassVar[FieldType]
    FIELD_TYPE_TEXT: _ClassVar[FieldType]
    FIELD_TYPE_TOKEN_COUNT: _ClassVar[FieldType]
    FIELD_TYPE_UNSIGNED_LONG: _ClassVar[FieldType]
    FIELD_TYPE_VERSION: _ClassVar[FieldType]
    FIELD_TYPE_WILDCARD: _ClassVar[FieldType]
    FIELD_TYPE_XY_POINT: _ClassVar[FieldType]
    FIELD_TYPE_XY_SHAPE: _ClassVar[FieldType]

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ORDER_UNSPECIFIED: _ClassVar[SortOrder]
    SORT_ORDER_ASC: _ClassVar[SortOrder]
    SORT_ORDER_DESC: _ClassVar[SortOrder]

class SortMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_MODE_UNSPECIFIED: _ClassVar[SortMode]
    SORT_MODE_AVG: _ClassVar[SortMode]
    SORT_MODE_MAX: _ClassVar[SortMode]
    SORT_MODE_MEDIAN: _ClassVar[SortMode]
    SORT_MODE_MIN: _ClassVar[SortMode]
    SORT_MODE_SUM: _ClassVar[SortMode]

class GeoDistanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GEO_DISTANCE_TYPE_UNSPECIFIED: _ClassVar[GeoDistanceType]
    GEO_DISTANCE_TYPE_ARC: _ClassVar[GeoDistanceType]
    GEO_DISTANCE_TYPE_PLANE: _ClassVar[GeoDistanceType]

class GeoValidationMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GEO_VALIDATION_METHOD_UNSPECIFIED: _ClassVar[GeoValidationMethod]
    GEO_VALIDATION_METHOD_COERCE: _ClassVar[GeoValidationMethod]
    GEO_VALIDATION_METHOD_IGNORE_MALFORMED: _ClassVar[GeoValidationMethod]
    GEO_VALIDATION_METHOD_STRICT: _ClassVar[GeoValidationMethod]

class ScriptSortType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCRIPT_SORT_TYPE_UNSPECIFIED: _ClassVar[ScriptSortType]
    SCRIPT_SORT_TYPE_NUMBER: _ClassVar[ScriptSortType]
    SCRIPT_SORT_TYPE_STRING: _ClassVar[ScriptSortType]
    SCRIPT_SORT_TYPE_VERSION: _ClassVar[ScriptSortType]

class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_UNSPECIFIED: _ClassVar[Operator]
    OPERATOR_AND: _ClassVar[Operator]
    OPERATOR_OR: _ClassVar[Operator]

class MultiTermQueryRewrite(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MULTI_TERM_QUERY_REWRITE_UNSPECIFIED: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_CONSTANT_SCORE: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_CONSTANT_SCORE_BOOLEAN: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_SCORING_BOOLEAN: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_TOP_TERMS_N: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_TOP_TERMS_BLENDED_FREQS_N: _ClassVar[MultiTermQueryRewrite]
    MULTI_TERM_QUERY_REWRITE_TOP_TERMS_BOOST_N: _ClassVar[MultiTermQueryRewrite]

class SimpleQueryStringFlag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIMPLE_QUERY_STRING_FLAG_UNSPECIFIED: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_ALL: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_AND: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_ESCAPE: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_FUZZY: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_NEAR: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_NONE: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_NOT: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_OR: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_PHRASE: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_PRECEDENCE: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_PREFIX: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_SLOP: _ClassVar[SimpleQueryStringFlag]
    SIMPLE_QUERY_STRING_FLAG_WHITESPACE: _ClassVar[SimpleQueryStringFlag]

class FunctionBoostMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTION_BOOST_MODE_UNSPECIFIED: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_AVG: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_MAX: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_MIN: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_MULTIPLY: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_REPLACE: _ClassVar[FunctionBoostMode]
    FUNCTION_BOOST_MODE_SUM: _ClassVar[FunctionBoostMode]

class FunctionScoreMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTION_SCORE_MODE_UNSPECIFIED: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_AVG: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_FIRST: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_MAX: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_MIN: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_MULTIPLY: _ClassVar[FunctionScoreMode]
    FUNCTION_SCORE_MODE_SUM: _ClassVar[FunctionScoreMode]

class MultiValueMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MULTI_VALUE_MODE_UNSPECIFIED: _ClassVar[MultiValueMode]
    MULTI_VALUE_MODE_AVG: _ClassVar[MultiValueMode]
    MULTI_VALUE_MODE_MAX: _ClassVar[MultiValueMode]
    MULTI_VALUE_MODE_MIN: _ClassVar[MultiValueMode]
    MULTI_VALUE_MODE_SUM: _ClassVar[MultiValueMode]

class ValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_TYPE_UNSPECIFIED: _ClassVar[ValueType]
    VALUE_TYPE_BITMAP: _ClassVar[ValueType]
    VALUE_TYPE_DEFAULT: _ClassVar[ValueType]

class TermsQueryValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TERMS_QUERY_VALUE_TYPE_UNSPECIFIED: _ClassVar[TermsQueryValueType]
    TERMS_QUERY_VALUE_TYPE_BITMAP: _ClassVar[TermsQueryValueType]
    TERMS_QUERY_VALUE_TYPE_DEFAULT: _ClassVar[TermsQueryValueType]

class TextQueryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEXT_QUERY_TYPE_UNSPECIFIED: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_BEST_FIELDS: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_BOOL_PREFIX: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_CROSS_FIELDS: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_MOST_FIELDS: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_PHRASE: _ClassVar[TextQueryType]
    TEXT_QUERY_TYPE_PHRASE_PREFIX: _ClassVar[TextQueryType]

class RangeRelation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANGE_RELATION_UNSPECIFIED: _ClassVar[RangeRelation]
    RANGE_RELATION_CONTAINS: _ClassVar[RangeRelation]
    RANGE_RELATION_INTERSECTS: _ClassVar[RangeRelation]
    RANGE_RELATION_WITHIN: _ClassVar[RangeRelation]

class ZeroTermsQuery(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ZERO_TERMS_QUERY_UNSPECIFIED: _ClassVar[ZeroTermsQuery]
    ZERO_TERMS_QUERY_ALL: _ClassVar[ZeroTermsQuery]
    ZERO_TERMS_QUERY_NONE: _ClassVar[ZeroTermsQuery]

class FieldValueFactorModifier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIELD_VALUE_FACTOR_MODIFIER_UNSPECIFIED: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LN: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LN1P: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LN2P: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LOG: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LOG1P: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_LOG2P: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_NONE: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_RECIPROCAL: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_SQRT: _ClassVar[FieldValueFactorModifier]
    FIELD_VALUE_FACTOR_MODIFIER_SQUARE: _ClassVar[FieldValueFactorModifier]

class DutchAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DUTCH_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[DutchAnalyzerType]
    DUTCH_ANALYZER_TYPE_DUTCH: _ClassVar[DutchAnalyzerType]

class FingerprintAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FINGERPRINT_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[FingerprintAnalyzerType]
    FINGERPRINT_ANALYZER_TYPE_FINGERPRINT: _ClassVar[FingerprintAnalyzerType]

class IcuAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ICU_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[IcuAnalyzerType]
    ICU_ANALYZER_TYPE_ICU_ANALYZER: _ClassVar[IcuAnalyzerType]

class IcuNormalizationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ICU_NORMALIZATION_MODE_UNSPECIFIED: _ClassVar[IcuNormalizationMode]
    ICU_NORMALIZATION_MODE_COMPOSE: _ClassVar[IcuNormalizationMode]
    ICU_NORMALIZATION_MODE_DECOMPOSE: _ClassVar[IcuNormalizationMode]

class IcuNormalizationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ICU_NORMALIZATION_TYPE_UNSPECIFIED: _ClassVar[IcuNormalizationType]
    ICU_NORMALIZATION_TYPE_NFC: _ClassVar[IcuNormalizationType]
    ICU_NORMALIZATION_TYPE_NFKC: _ClassVar[IcuNormalizationType]
    ICU_NORMALIZATION_TYPE_NFKC_CF: _ClassVar[IcuNormalizationType]

class KeywordAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KEYWORD_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[KeywordAnalyzerType]
    KEYWORD_ANALYZER_TYPE_KEYWORD: _ClassVar[KeywordAnalyzerType]

class LanguageAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LANGUAGE_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[LanguageAnalyzerType]
    LANGUAGE_ANALYZER_TYPE_LANGUAGE: _ClassVar[LanguageAnalyzerType]

class Language(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LANGUAGE_UNSPECIFIED: _ClassVar[Language]
    LANGUAGE_ARABIC: _ClassVar[Language]
    LANGUAGE_ARMENIAN: _ClassVar[Language]
    LANGUAGE_BASQUE: _ClassVar[Language]
    LANGUAGE_BRAZILIAN: _ClassVar[Language]
    LANGUAGE_BULGARIAN: _ClassVar[Language]
    LANGUAGE_CATALAN: _ClassVar[Language]
    LANGUAGE_CHINESE: _ClassVar[Language]
    LANGUAGE_CJK: _ClassVar[Language]
    LANGUAGE_CZECH: _ClassVar[Language]
    LANGUAGE_DANISH: _ClassVar[Language]
    LANGUAGE_DUTCH: _ClassVar[Language]
    LANGUAGE_ENGLISH: _ClassVar[Language]
    LANGUAGE_ESTONIAN: _ClassVar[Language]
    LANGUAGE_FINNISH: _ClassVar[Language]
    LANGUAGE_FRENCH: _ClassVar[Language]
    LANGUAGE_GALICIAN: _ClassVar[Language]
    LANGUAGE_GERMAN: _ClassVar[Language]
    LANGUAGE_GREEK: _ClassVar[Language]
    LANGUAGE_HINDI: _ClassVar[Language]
    LANGUAGE_HUNGARIAN: _ClassVar[Language]
    LANGUAGE_INDONESIAN: _ClassVar[Language]
    LANGUAGE_IRISH: _ClassVar[Language]
    LANGUAGE_ITALIAN: _ClassVar[Language]
    LANGUAGE_LATVIAN: _ClassVar[Language]
    LANGUAGE_NORWEGIAN: _ClassVar[Language]
    LANGUAGE_PERSIAN: _ClassVar[Language]
    LANGUAGE_PORTUGUESE: _ClassVar[Language]
    LANGUAGE_ROMANIAN: _ClassVar[Language]
    LANGUAGE_RUSSIAN: _ClassVar[Language]
    LANGUAGE_SORANI: _ClassVar[Language]
    LANGUAGE_SPANISH: _ClassVar[Language]
    LANGUAGE_SWEDISH: _ClassVar[Language]
    LANGUAGE_THAI: _ClassVar[Language]
    LANGUAGE_TURKISH: _ClassVar[Language]

class NoriAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NORI_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[NoriAnalyzerType]
    NORI_ANALYZER_TYPE_NORI: _ClassVar[NoriAnalyzerType]

class NoriDecompoundMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NORI_DECOMPOUND_MODE_UNSPECIFIED: _ClassVar[NoriDecompoundMode]
    NORI_DECOMPOUND_MODE_DISCARD: _ClassVar[NoriDecompoundMode]
    NORI_DECOMPOUND_MODE_MIXED: _ClassVar[NoriDecompoundMode]
    NORI_DECOMPOUND_MODE_NONE: _ClassVar[NoriDecompoundMode]

class PatternAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PATTERN_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[PatternAnalyzerType]
    PATTERN_ANALYZER_TYPE_PATTERN: _ClassVar[PatternAnalyzerType]

class StandardAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STANDARD_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[StandardAnalyzerType]
    STANDARD_ANALYZER_TYPE_STANDARD: _ClassVar[StandardAnalyzerType]

class StopAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOP_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[StopAnalyzerType]
    STOP_ANALYZER_TYPE_STOP: _ClassVar[StopAnalyzerType]

class WhitespaceAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WHITESPACE_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[WhitespaceAnalyzerType]
    WHITESPACE_ANALYZER_TYPE_WHITESPACE: _ClassVar[WhitespaceAnalyzerType]

class CustomAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CUSTOM_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[CustomAnalyzerType]
    CUSTOM_ANALYZER_TYPE_CUSTOM: _ClassVar[CustomAnalyzerType]

class KuromojiAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KUROMOJI_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[KuromojiAnalyzerType]
    KUROMOJI_ANALYZER_TYPE_KUROMOJI: _ClassVar[KuromojiAnalyzerType]

class KuromojiTokenizationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KUROMOJI_TOKENIZATION_MODE_UNSPECIFIED: _ClassVar[KuromojiTokenizationMode]
    KUROMOJI_TOKENIZATION_MODE_EXTENDED: _ClassVar[KuromojiTokenizationMode]
    KUROMOJI_TOKENIZATION_MODE_NORMAL: _ClassVar[KuromojiTokenizationMode]
    KUROMOJI_TOKENIZATION_MODE_SEARCH: _ClassVar[KuromojiTokenizationMode]

class SnowballAnalyzerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SNOWBALL_ANALYZER_TYPE_UNSPECIFIED: _ClassVar[SnowballAnalyzerType]
    SNOWBALL_ANALYZER_TYPE_SNOWBALL: _ClassVar[SnowballAnalyzerType]

class SnowballLanguage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SNOWBALL_LANGUAGE_UNSPECIFIED: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_ARMENIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_BASQUE: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_CATALAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_DANISH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_DUTCH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_ENGLISH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_FINNISH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_FRENCH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_GERMAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_GERMAN2: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_HUNGARIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_ITALIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_KP: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_LOVINS: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_NORWEGIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_PORTER: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_PORTUGUESE: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_ROMANIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_RUSSIAN: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_SPANISH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_SWEDISH: _ClassVar[SnowballLanguage]
    SNOWBALL_LANGUAGE_TURKISH: _ClassVar[SnowballLanguage]
WAIT_FOR_ACTIVE_SHARD_OPTIONS_UNSPECIFIED: WaitForActiveShardOptions
WAIT_FOR_ACTIVE_SHARD_OPTIONS_ALL: WaitForActiveShardOptions
WAIT_FOR_ACTIVE_SHARD_OPTIONS_NULL: WaitForActiveShardOptions
BUILTIN_SCRIPT_LANGUAGE_UNSPECIFIED: BuiltinScriptLanguage
BUILTIN_SCRIPT_LANGUAGE_EXPRESSION: BuiltinScriptLanguage
BUILTIN_SCRIPT_LANGUAGE_JAVA: BuiltinScriptLanguage
BUILTIN_SCRIPT_LANGUAGE_MUSTACHE: BuiltinScriptLanguage
BUILTIN_SCRIPT_LANGUAGE_PAINLESS: BuiltinScriptLanguage
EXPAND_WILDCARD_UNSPECIFIED: ExpandWildcard
EXPAND_WILDCARD_ALL: ExpandWildcard
EXPAND_WILDCARD_CLOSED: ExpandWildcard
EXPAND_WILDCARD_HIDDEN: ExpandWildcard
EXPAND_WILDCARD_NONE: ExpandWildcard
EXPAND_WILDCARD_OPEN: ExpandWildcard
SEARCH_TYPE_UNSPECIFIED: SearchType
SEARCH_TYPE_DFS_QUERY_THEN_FETCH: SearchType
SEARCH_TYPE_QUERY_THEN_FETCH: SearchType
SUGGEST_MODE_UNSPECIFIED: SuggestMode
SUGGEST_MODE_ALWAYS: SuggestMode
SUGGEST_MODE_MISSING: SuggestMode
SUGGEST_MODE_POPULAR: SuggestMode
NULL_VALUE_UNSPECIFIED: NullValue
NULL_VALUE_NULL: NullValue
SOURCE_TYPE_UNSPECIFIED: SourceType
SOURCE_TYPE_STRUCT: SourceType
RUNTIME_FIELD_TYPE_UNSPECIFIED: RuntimeFieldType
RUNTIME_FIELD_TYPE_BOOLEAN: RuntimeFieldType
RUNTIME_FIELD_TYPE_DATE: RuntimeFieldType
RUNTIME_FIELD_TYPE_DOUBLE: RuntimeFieldType
RUNTIME_FIELD_TYPE_GEO_POINT: RuntimeFieldType
RUNTIME_FIELD_TYPE_IP: RuntimeFieldType
RUNTIME_FIELD_TYPE_KEYWORD: RuntimeFieldType
RUNTIME_FIELD_TYPE_LONG: RuntimeFieldType
RUNTIME_FIELD_TYPE_LOOKUP: RuntimeFieldType
GEO_EXECUTION_UNSPECIFIED: GeoExecution
GEO_EXECUTION_INDEXED: GeoExecution
GEO_EXECUTION_MEMORY: GeoExecution
DISTANCE_UNIT_UNSPECIFIED: DistanceUnit
DISTANCE_UNIT_CM: DistanceUnit
DISTANCE_UNIT_FT: DistanceUnit
DISTANCE_UNIT_IN: DistanceUnit
DISTANCE_UNIT_KM: DistanceUnit
DISTANCE_UNIT_M: DistanceUnit
DISTANCE_UNIT_MI: DistanceUnit
DISTANCE_UNIT_MM: DistanceUnit
DISTANCE_UNIT_NMI: DistanceUnit
DISTANCE_UNIT_YD: DistanceUnit
CHILD_SCORE_MODE_UNSPECIFIED: ChildScoreMode
CHILD_SCORE_MODE_AVG: ChildScoreMode
CHILD_SCORE_MODE_MAX: ChildScoreMode
CHILD_SCORE_MODE_MIN: ChildScoreMode
CHILD_SCORE_MODE_NONE: ChildScoreMode
CHILD_SCORE_MODE_SUM: ChildScoreMode
BUILTIN_HIGHLIGHTER_TYPE_UNSPECIFIED: BuiltinHighlighterType
BUILTIN_HIGHLIGHTER_TYPE_PLAIN: BuiltinHighlighterType
BUILTIN_HIGHLIGHTER_TYPE_FVH: BuiltinHighlighterType
BUILTIN_HIGHLIGHTER_TYPE_UNIFIED: BuiltinHighlighterType
BOUNDARY_SCANNER_UNSPECIFIED: BoundaryScanner
BOUNDARY_SCANNER_CHARS: BoundaryScanner
BOUNDARY_SCANNER_SENTENCE: BoundaryScanner
BOUNDARY_SCANNER_WORD: BoundaryScanner
HIGHLIGHTER_FRAGMENTER_UNSPECIFIED: HighlighterFragmenter
HIGHLIGHTER_FRAGMENTER_SIMPLE: HighlighterFragmenter
HIGHLIGHTER_FRAGMENTER_SPAN: HighlighterFragmenter
HIGHLIGHTER_ORDER_UNSPECIFIED: HighlighterOrder
HIGHLIGHTER_ORDER_SCORE: HighlighterOrder
HIGHLIGHTER_TAGS_SCHEMA_UNSPECIFIED: HighlighterTagsSchema
HIGHLIGHTER_TAGS_SCHEMA_STYLED: HighlighterTagsSchema
HIGHLIGHTER_ENCODER_UNSPECIFIED: HighlighterEncoder
HIGHLIGHTER_ENCODER_DEFAULT: HighlighterEncoder
HIGHLIGHTER_ENCODER_HTML: HighlighterEncoder
FIELD_SORT_NUMERIC_TYPE_UNSPECIFIED: FieldSortNumericType
FIELD_SORT_NUMERIC_TYPE_DATE: FieldSortNumericType
FIELD_SORT_NUMERIC_TYPE_DATE_NANOS: FieldSortNumericType
FIELD_SORT_NUMERIC_TYPE_DOUBLE: FieldSortNumericType
FIELD_SORT_NUMERIC_TYPE_LONG: FieldSortNumericType
FIELD_TYPE_UNSPECIFIED: FieldType
FIELD_TYPE_AGGREGATE_METRIC_DOUBLE: FieldType
FIELD_TYPE_ALIAS: FieldType
FIELD_TYPE_BINARY: FieldType
FIELD_TYPE_BOOLEAN: FieldType
FIELD_TYPE_BYTE: FieldType
FIELD_TYPE_COMPLETION: FieldType
FIELD_TYPE_CONSTANT_KEYWORD: FieldType
FIELD_TYPE_DATE: FieldType
FIELD_TYPE_DATE_NANOS: FieldType
FIELD_TYPE_DATE_RANGE: FieldType
FIELD_TYPE_DOUBLE: FieldType
FIELD_TYPE_DOUBLE_RANGE: FieldType
FIELD_TYPE_FLAT_OBJECT: FieldType
FIELD_TYPE_FLOAT: FieldType
FIELD_TYPE_FLOAT_RANGE: FieldType
FIELD_TYPE_GEO_POINT: FieldType
FIELD_TYPE_GEO_SHAPE: FieldType
FIELD_TYPE_HALF_FLOAT: FieldType
FIELD_TYPE_HISTOGRAM: FieldType
FIELD_TYPE_ICU_COLLATION_KEYWORD: FieldType
FIELD_TYPE_INTEGER: FieldType
FIELD_TYPE_INTEGER_RANGE: FieldType
FIELD_TYPE_IP: FieldType
FIELD_TYPE_IP_RANGE: FieldType
FIELD_TYPE_JOIN: FieldType
FIELD_TYPE_KEYWORD: FieldType
FIELD_TYPE_KNN_VECTOR: FieldType
FIELD_TYPE_LONG: FieldType
FIELD_TYPE_LONG_RANGE: FieldType
FIELD_TYPE_MATCH_ONLY_TEXT: FieldType
FIELD_TYPE_MURMUR3: FieldType
FIELD_TYPE_NESTED: FieldType
FIELD_TYPE_OBJECT: FieldType
FIELD_TYPE_PERCOLATOR: FieldType
FIELD_TYPE_RANK_FEATURE: FieldType
FIELD_TYPE_RANK_FEATURES: FieldType
FIELD_TYPE_SCALED_FLOAT: FieldType
FIELD_TYPE_SEARCH_AS_YOU_TYPE: FieldType
FIELD_TYPE_SHORT: FieldType
FIELD_TYPE_TEXT: FieldType
FIELD_TYPE_TOKEN_COUNT: FieldType
FIELD_TYPE_UNSIGNED_LONG: FieldType
FIELD_TYPE_VERSION: FieldType
FIELD_TYPE_WILDCARD: FieldType
FIELD_TYPE_XY_POINT: FieldType
FIELD_TYPE_XY_SHAPE: FieldType
SORT_ORDER_UNSPECIFIED: SortOrder
SORT_ORDER_ASC: SortOrder
SORT_ORDER_DESC: SortOrder
SORT_MODE_UNSPECIFIED: SortMode
SORT_MODE_AVG: SortMode
SORT_MODE_MAX: SortMode
SORT_MODE_MEDIAN: SortMode
SORT_MODE_MIN: SortMode
SORT_MODE_SUM: SortMode
GEO_DISTANCE_TYPE_UNSPECIFIED: GeoDistanceType
GEO_DISTANCE_TYPE_ARC: GeoDistanceType
GEO_DISTANCE_TYPE_PLANE: GeoDistanceType
GEO_VALIDATION_METHOD_UNSPECIFIED: GeoValidationMethod
GEO_VALIDATION_METHOD_COERCE: GeoValidationMethod
GEO_VALIDATION_METHOD_IGNORE_MALFORMED: GeoValidationMethod
GEO_VALIDATION_METHOD_STRICT: GeoValidationMethod
SCRIPT_SORT_TYPE_UNSPECIFIED: ScriptSortType
SCRIPT_SORT_TYPE_NUMBER: ScriptSortType
SCRIPT_SORT_TYPE_STRING: ScriptSortType
SCRIPT_SORT_TYPE_VERSION: ScriptSortType
OPERATOR_UNSPECIFIED: Operator
OPERATOR_AND: Operator
OPERATOR_OR: Operator
MULTI_TERM_QUERY_REWRITE_UNSPECIFIED: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_CONSTANT_SCORE: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_CONSTANT_SCORE_BOOLEAN: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_SCORING_BOOLEAN: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_TOP_TERMS_N: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_TOP_TERMS_BLENDED_FREQS_N: MultiTermQueryRewrite
MULTI_TERM_QUERY_REWRITE_TOP_TERMS_BOOST_N: MultiTermQueryRewrite
SIMPLE_QUERY_STRING_FLAG_UNSPECIFIED: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_ALL: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_AND: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_ESCAPE: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_FUZZY: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_NEAR: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_NONE: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_NOT: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_OR: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_PHRASE: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_PRECEDENCE: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_PREFIX: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_SLOP: SimpleQueryStringFlag
SIMPLE_QUERY_STRING_FLAG_WHITESPACE: SimpleQueryStringFlag
FUNCTION_BOOST_MODE_UNSPECIFIED: FunctionBoostMode
FUNCTION_BOOST_MODE_AVG: FunctionBoostMode
FUNCTION_BOOST_MODE_MAX: FunctionBoostMode
FUNCTION_BOOST_MODE_MIN: FunctionBoostMode
FUNCTION_BOOST_MODE_MULTIPLY: FunctionBoostMode
FUNCTION_BOOST_MODE_REPLACE: FunctionBoostMode
FUNCTION_BOOST_MODE_SUM: FunctionBoostMode
FUNCTION_SCORE_MODE_UNSPECIFIED: FunctionScoreMode
FUNCTION_SCORE_MODE_AVG: FunctionScoreMode
FUNCTION_SCORE_MODE_FIRST: FunctionScoreMode
FUNCTION_SCORE_MODE_MAX: FunctionScoreMode
FUNCTION_SCORE_MODE_MIN: FunctionScoreMode
FUNCTION_SCORE_MODE_MULTIPLY: FunctionScoreMode
FUNCTION_SCORE_MODE_SUM: FunctionScoreMode
MULTI_VALUE_MODE_UNSPECIFIED: MultiValueMode
MULTI_VALUE_MODE_AVG: MultiValueMode
MULTI_VALUE_MODE_MAX: MultiValueMode
MULTI_VALUE_MODE_MIN: MultiValueMode
MULTI_VALUE_MODE_SUM: MultiValueMode
VALUE_TYPE_UNSPECIFIED: ValueType
VALUE_TYPE_BITMAP: ValueType
VALUE_TYPE_DEFAULT: ValueType
TERMS_QUERY_VALUE_TYPE_UNSPECIFIED: TermsQueryValueType
TERMS_QUERY_VALUE_TYPE_BITMAP: TermsQueryValueType
TERMS_QUERY_VALUE_TYPE_DEFAULT: TermsQueryValueType
TEXT_QUERY_TYPE_UNSPECIFIED: TextQueryType
TEXT_QUERY_TYPE_BEST_FIELDS: TextQueryType
TEXT_QUERY_TYPE_BOOL_PREFIX: TextQueryType
TEXT_QUERY_TYPE_CROSS_FIELDS: TextQueryType
TEXT_QUERY_TYPE_MOST_FIELDS: TextQueryType
TEXT_QUERY_TYPE_PHRASE: TextQueryType
TEXT_QUERY_TYPE_PHRASE_PREFIX: TextQueryType
RANGE_RELATION_UNSPECIFIED: RangeRelation
RANGE_RELATION_CONTAINS: RangeRelation
RANGE_RELATION_INTERSECTS: RangeRelation
RANGE_RELATION_WITHIN: RangeRelation
ZERO_TERMS_QUERY_UNSPECIFIED: ZeroTermsQuery
ZERO_TERMS_QUERY_ALL: ZeroTermsQuery
ZERO_TERMS_QUERY_NONE: ZeroTermsQuery
FIELD_VALUE_FACTOR_MODIFIER_UNSPECIFIED: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LN: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LN1P: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LN2P: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LOG: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LOG1P: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_LOG2P: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_NONE: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_RECIPROCAL: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_SQRT: FieldValueFactorModifier
FIELD_VALUE_FACTOR_MODIFIER_SQUARE: FieldValueFactorModifier
DUTCH_ANALYZER_TYPE_UNSPECIFIED: DutchAnalyzerType
DUTCH_ANALYZER_TYPE_DUTCH: DutchAnalyzerType
FINGERPRINT_ANALYZER_TYPE_UNSPECIFIED: FingerprintAnalyzerType
FINGERPRINT_ANALYZER_TYPE_FINGERPRINT: FingerprintAnalyzerType
ICU_ANALYZER_TYPE_UNSPECIFIED: IcuAnalyzerType
ICU_ANALYZER_TYPE_ICU_ANALYZER: IcuAnalyzerType
ICU_NORMALIZATION_MODE_UNSPECIFIED: IcuNormalizationMode
ICU_NORMALIZATION_MODE_COMPOSE: IcuNormalizationMode
ICU_NORMALIZATION_MODE_DECOMPOSE: IcuNormalizationMode
ICU_NORMALIZATION_TYPE_UNSPECIFIED: IcuNormalizationType
ICU_NORMALIZATION_TYPE_NFC: IcuNormalizationType
ICU_NORMALIZATION_TYPE_NFKC: IcuNormalizationType
ICU_NORMALIZATION_TYPE_NFKC_CF: IcuNormalizationType
KEYWORD_ANALYZER_TYPE_UNSPECIFIED: KeywordAnalyzerType
KEYWORD_ANALYZER_TYPE_KEYWORD: KeywordAnalyzerType
LANGUAGE_ANALYZER_TYPE_UNSPECIFIED: LanguageAnalyzerType
LANGUAGE_ANALYZER_TYPE_LANGUAGE: LanguageAnalyzerType
LANGUAGE_UNSPECIFIED: Language
LANGUAGE_ARABIC: Language
LANGUAGE_ARMENIAN: Language
LANGUAGE_BASQUE: Language
LANGUAGE_BRAZILIAN: Language
LANGUAGE_BULGARIAN: Language
LANGUAGE_CATALAN: Language
LANGUAGE_CHINESE: Language
LANGUAGE_CJK: Language
LANGUAGE_CZECH: Language
LANGUAGE_DANISH: Language
LANGUAGE_DUTCH: Language
LANGUAGE_ENGLISH: Language
LANGUAGE_ESTONIAN: Language
LANGUAGE_FINNISH: Language
LANGUAGE_FRENCH: Language
LANGUAGE_GALICIAN: Language
LANGUAGE_GERMAN: Language
LANGUAGE_GREEK: Language
LANGUAGE_HINDI: Language
LANGUAGE_HUNGARIAN: Language
LANGUAGE_INDONESIAN: Language
LANGUAGE_IRISH: Language
LANGUAGE_ITALIAN: Language
LANGUAGE_LATVIAN: Language
LANGUAGE_NORWEGIAN: Language
LANGUAGE_PERSIAN: Language
LANGUAGE_PORTUGUESE: Language
LANGUAGE_ROMANIAN: Language
LANGUAGE_RUSSIAN: Language
LANGUAGE_SORANI: Language
LANGUAGE_SPANISH: Language
LANGUAGE_SWEDISH: Language
LANGUAGE_THAI: Language
LANGUAGE_TURKISH: Language
NORI_ANALYZER_TYPE_UNSPECIFIED: NoriAnalyzerType
NORI_ANALYZER_TYPE_NORI: NoriAnalyzerType
NORI_DECOMPOUND_MODE_UNSPECIFIED: NoriDecompoundMode
NORI_DECOMPOUND_MODE_DISCARD: NoriDecompoundMode
NORI_DECOMPOUND_MODE_MIXED: NoriDecompoundMode
NORI_DECOMPOUND_MODE_NONE: NoriDecompoundMode
PATTERN_ANALYZER_TYPE_UNSPECIFIED: PatternAnalyzerType
PATTERN_ANALYZER_TYPE_PATTERN: PatternAnalyzerType
STANDARD_ANALYZER_TYPE_UNSPECIFIED: StandardAnalyzerType
STANDARD_ANALYZER_TYPE_STANDARD: StandardAnalyzerType
STOP_ANALYZER_TYPE_UNSPECIFIED: StopAnalyzerType
STOP_ANALYZER_TYPE_STOP: StopAnalyzerType
WHITESPACE_ANALYZER_TYPE_UNSPECIFIED: WhitespaceAnalyzerType
WHITESPACE_ANALYZER_TYPE_WHITESPACE: WhitespaceAnalyzerType
CUSTOM_ANALYZER_TYPE_UNSPECIFIED: CustomAnalyzerType
CUSTOM_ANALYZER_TYPE_CUSTOM: CustomAnalyzerType
KUROMOJI_ANALYZER_TYPE_UNSPECIFIED: KuromojiAnalyzerType
KUROMOJI_ANALYZER_TYPE_KUROMOJI: KuromojiAnalyzerType
KUROMOJI_TOKENIZATION_MODE_UNSPECIFIED: KuromojiTokenizationMode
KUROMOJI_TOKENIZATION_MODE_EXTENDED: KuromojiTokenizationMode
KUROMOJI_TOKENIZATION_MODE_NORMAL: KuromojiTokenizationMode
KUROMOJI_TOKENIZATION_MODE_SEARCH: KuromojiTokenizationMode
SNOWBALL_ANALYZER_TYPE_UNSPECIFIED: SnowballAnalyzerType
SNOWBALL_ANALYZER_TYPE_SNOWBALL: SnowballAnalyzerType
SNOWBALL_LANGUAGE_UNSPECIFIED: SnowballLanguage
SNOWBALL_LANGUAGE_ARMENIAN: SnowballLanguage
SNOWBALL_LANGUAGE_BASQUE: SnowballLanguage
SNOWBALL_LANGUAGE_CATALAN: SnowballLanguage
SNOWBALL_LANGUAGE_DANISH: SnowballLanguage
SNOWBALL_LANGUAGE_DUTCH: SnowballLanguage
SNOWBALL_LANGUAGE_ENGLISH: SnowballLanguage
SNOWBALL_LANGUAGE_FINNISH: SnowballLanguage
SNOWBALL_LANGUAGE_FRENCH: SnowballLanguage
SNOWBALL_LANGUAGE_GERMAN: SnowballLanguage
SNOWBALL_LANGUAGE_GERMAN2: SnowballLanguage
SNOWBALL_LANGUAGE_HUNGARIAN: SnowballLanguage
SNOWBALL_LANGUAGE_ITALIAN: SnowballLanguage
SNOWBALL_LANGUAGE_KP: SnowballLanguage
SNOWBALL_LANGUAGE_LOVINS: SnowballLanguage
SNOWBALL_LANGUAGE_NORWEGIAN: SnowballLanguage
SNOWBALL_LANGUAGE_PORTER: SnowballLanguage
SNOWBALL_LANGUAGE_PORTUGUESE: SnowballLanguage
SNOWBALL_LANGUAGE_ROMANIAN: SnowballLanguage
SNOWBALL_LANGUAGE_RUSSIAN: SnowballLanguage
SNOWBALL_LANGUAGE_SPANISH: SnowballLanguage
SNOWBALL_LANGUAGE_SWEDISH: SnowballLanguage
SNOWBALL_LANGUAGE_TURKISH: SnowballLanguage

class GlobalParams(_message.Message):
    __slots__ = ("human", "error_trace", "filter_path")
    HUMAN_FIELD_NUMBER: _ClassVar[int]
    ERROR_TRACE_FIELD_NUMBER: _ClassVar[int]
    FILTER_PATH_FIELD_NUMBER: _ClassVar[int]
    human: bool
    error_trace: bool
    filter_path: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, human: bool = ..., error_trace: bool = ..., filter_path: _Optional[_Iterable[str]] = ...) -> None: ...

class WaitForActiveShards(_message.Message):
    __slots__ = ("int32", "wait_for_active_shard_options")
    INT32_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_ACTIVE_SHARD_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    int32: int
    wait_for_active_shard_options: WaitForActiveShardOptions
    def __init__(self, int32: _Optional[int] = ..., wait_for_active_shard_options: _Optional[_Union[WaitForActiveShardOptions, str]] = ...) -> None: ...

class Script(_message.Message):
    __slots__ = ("inline", "stored")
    INLINE_FIELD_NUMBER: _ClassVar[int]
    STORED_FIELD_NUMBER: _ClassVar[int]
    inline: InlineScript
    stored: StoredScriptId
    def __init__(self, inline: _Optional[_Union[InlineScript, _Mapping]] = ..., stored: _Optional[_Union[StoredScriptId, _Mapping]] = ...) -> None: ...

class InlineScript(_message.Message):
    __slots__ = ("params", "lang", "options", "source")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    LANG_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    params: ObjectMap
    lang: ScriptLanguage
    options: _containers.ScalarMap[str, str]
    source: str
    def __init__(self, params: _Optional[_Union[ObjectMap, _Mapping]] = ..., lang: _Optional[_Union[ScriptLanguage, _Mapping]] = ..., options: _Optional[_Mapping[str, str]] = ..., source: _Optional[str] = ...) -> None: ...

class ScriptLanguage(_message.Message):
    __slots__ = ("builtin", "custom")
    BUILTIN_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
    builtin: BuiltinScriptLanguage
    custom: str
    def __init__(self, builtin: _Optional[_Union[BuiltinScriptLanguage, str]] = ..., custom: _Optional[str] = ...) -> None: ...

class StoredScriptId(_message.Message):
    __slots__ = ("params", "id")
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    params: ObjectMap
    id: str
    def __init__(self, params: _Optional[_Union[ObjectMap, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class ObjectMap(_message.Message):
    __slots__ = ("fields",)
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ObjectMap.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ObjectMap.Value, _Mapping]] = ...) -> None: ...
    class Value(_message.Message):
        __slots__ = ("null_value", "int32", "int64", "float", "double", "string", "bool", "object_map", "list_value")
        NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
        INT32_FIELD_NUMBER: _ClassVar[int]
        INT64_FIELD_NUMBER: _ClassVar[int]
        FLOAT_FIELD_NUMBER: _ClassVar[int]
        DOUBLE_FIELD_NUMBER: _ClassVar[int]
        STRING_FIELD_NUMBER: _ClassVar[int]
        BOOL_FIELD_NUMBER: _ClassVar[int]
        OBJECT_MAP_FIELD_NUMBER: _ClassVar[int]
        LIST_VALUE_FIELD_NUMBER: _ClassVar[int]
        null_value: NullValue
        int32: int
        int64: int
        float: float
        double: float
        string: str
        bool: bool
        object_map: ObjectMap
        list_value: ObjectMap.ListValue
        def __init__(self, null_value: _Optional[_Union[NullValue, str]] = ..., int32: _Optional[int] = ..., int64: _Optional[int] = ..., float: _Optional[float] = ..., double: _Optional[float] = ..., string: _Optional[str] = ..., bool: bool = ..., object_map: _Optional[_Union[ObjectMap, _Mapping]] = ..., list_value: _Optional[_Union[ObjectMap.ListValue, _Mapping]] = ...) -> None: ...
    class ListValue(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: _containers.RepeatedCompositeFieldContainer[ObjectMap.Value]
        def __init__(self, value: _Optional[_Iterable[_Union[ObjectMap.Value, _Mapping]]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.MessageMap[str, ObjectMap.Value]
    def __init__(self, fields: _Optional[_Mapping[str, ObjectMap.Value]] = ...) -> None: ...

class GeoLocation(_message.Message):
    __slots__ = ("latlon", "geohash", "double_array", "text")
    LATLON_FIELD_NUMBER: _ClassVar[int]
    GEOHASH_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_ARRAY_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    latlon: LatLonGeoLocation
    geohash: GeoHashLocation
    double_array: DoubleArray
    text: str
    def __init__(self, latlon: _Optional[_Union[LatLonGeoLocation, _Mapping]] = ..., geohash: _Optional[_Union[GeoHashLocation, _Mapping]] = ..., double_array: _Optional[_Union[DoubleArray, _Mapping]] = ..., text: _Optional[str] = ...) -> None: ...

class DoubleArray(_message.Message):
    __slots__ = ("double_array",)
    DOUBLE_ARRAY_FIELD_NUMBER: _ClassVar[int]
    double_array: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, double_array: _Optional[_Iterable[float]] = ...) -> None: ...

class NumberArray(_message.Message):
    __slots__ = ("number_array",)
    NUMBER_ARRAY_FIELD_NUMBER: _ClassVar[int]
    number_array: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, number_array: _Optional[_Iterable[float]] = ...) -> None: ...

class LatLonGeoLocation(_message.Message):
    __slots__ = ("lat", "lon")
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    lat: float
    lon: float
    def __init__(self, lat: _Optional[float] = ..., lon: _Optional[float] = ...) -> None: ...

class GeoHashLocation(_message.Message):
    __slots__ = ("geohash",)
    GEOHASH_FIELD_NUMBER: _ClassVar[int]
    geohash: str
    def __init__(self, geohash: _Optional[str] = ...) -> None: ...

class GeneralNumber(_message.Message):
    __slots__ = ("int32_value", "int64_value", "float_value", "double_value")
    INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    int32_value: int
    int64_value: int
    float_value: float
    double_value: float
    def __init__(self, int32_value: _Optional[int] = ..., int64_value: _Optional[int] = ..., float_value: _Optional[float] = ..., double_value: _Optional[float] = ...) -> None: ...

class SourceConfigParam(_message.Message):
    __slots__ = ("bool", "string_array")
    BOOL_FIELD_NUMBER: _ClassVar[int]
    STRING_ARRAY_FIELD_NUMBER: _ClassVar[int]
    bool: bool
    string_array: StringArray
    def __init__(self, bool: bool = ..., string_array: _Optional[_Union[StringArray, _Mapping]] = ...) -> None: ...

class StringArray(_message.Message):
    __slots__ = ("string_array",)
    STRING_ARRAY_FIELD_NUMBER: _ClassVar[int]
    string_array: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, string_array: _Optional[_Iterable[str]] = ...) -> None: ...

class StringOrStringArray(_message.Message):
    __slots__ = ("string", "string_array")
    STRING_FIELD_NUMBER: _ClassVar[int]
    STRING_ARRAY_FIELD_NUMBER: _ClassVar[int]
    string: str
    string_array: StringArray
    def __init__(self, string: _Optional[str] = ..., string_array: _Optional[_Union[StringArray, _Mapping]] = ...) -> None: ...

class Id(_message.Message):
    __slots__ = ("null_value", "string")
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    null_value: NullValue
    string: str
    def __init__(self, null_value: _Optional[_Union[NullValue, str]] = ..., string: _Optional[str] = ...) -> None: ...

class SourceConfig(_message.Message):
    __slots__ = ("fetch", "filter")
    FETCH_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    fetch: bool
    filter: SourceFilter
    def __init__(self, fetch: bool = ..., filter: _Optional[_Union[SourceFilter, _Mapping]] = ...) -> None: ...

class RuntimeField(_message.Message):
    __slots__ = ("fetch_fields", "format", "input_field", "target_field", "target_index", "script", "type")
    FETCH_FIELDS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_FIELD_NUMBER: _ClassVar[int]
    TARGET_INDEX_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    fetch_fields: _containers.RepeatedCompositeFieldContainer[RuntimeFieldFetchFields]
    format: str
    input_field: str
    target_field: str
    target_index: str
    script: Script
    type: RuntimeFieldType
    def __init__(self, fetch_fields: _Optional[_Iterable[_Union[RuntimeFieldFetchFields, _Mapping]]] = ..., format: _Optional[str] = ..., input_field: _Optional[str] = ..., target_field: _Optional[str] = ..., target_index: _Optional[str] = ..., script: _Optional[_Union[Script, _Mapping]] = ..., type: _Optional[_Union[RuntimeFieldType, str]] = ...) -> None: ...

class RuntimeFieldFetchFields(_message.Message):
    __slots__ = ("field", "format")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    field: str
    format: str
    def __init__(self, field: _Optional[str] = ..., format: _Optional[str] = ...) -> None: ...

class SourceFilter(_message.Message):
    __slots__ = ("excludes", "includes")
    EXCLUDES_FIELD_NUMBER: _ClassVar[int]
    INCLUDES_FIELD_NUMBER: _ClassVar[int]
    excludes: _containers.RepeatedScalarFieldContainer[str]
    includes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, excludes: _Optional[_Iterable[str]] = ..., includes: _Optional[_Iterable[str]] = ...) -> None: ...

class ErrorCause(_message.Message):
    __slots__ = ("type", "reason", "stack_trace", "caused_by", "root_cause", "suppressed", "index", "shard", "index_uuid", "metadata", "header")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ObjectMap.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ObjectMap.Value, _Mapping]] = ...) -> None: ...
    class HeaderEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: StringOrStringArray
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[StringOrStringArray, _Mapping]] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    CAUSED_BY_FIELD_NUMBER: _ClassVar[int]
    ROOT_CAUSE_FIELD_NUMBER: _ClassVar[int]
    SUPPRESSED_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SHARD_FIELD_NUMBER: _ClassVar[int]
    INDEX_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    type: str
    reason: str
    stack_trace: str
    caused_by: ErrorCause
    root_cause: _containers.RepeatedCompositeFieldContainer[ErrorCause]
    suppressed: _containers.RepeatedCompositeFieldContainer[ErrorCause]
    index: str
    shard: str
    index_uuid: str
    metadata: _containers.MessageMap[str, ObjectMap.Value]
    header: _containers.MessageMap[str, StringOrStringArray]
    def __init__(self, type: _Optional[str] = ..., reason: _Optional[str] = ..., stack_trace: _Optional[str] = ..., caused_by: _Optional[_Union[ErrorCause, _Mapping]] = ..., root_cause: _Optional[_Iterable[_Union[ErrorCause, _Mapping]]] = ..., suppressed: _Optional[_Iterable[_Union[ErrorCause, _Mapping]]] = ..., index: _Optional[str] = ..., shard: _Optional[str] = ..., index_uuid: _Optional[str] = ..., metadata: _Optional[_Mapping[str, ObjectMap.Value]] = ..., header: _Optional[_Mapping[str, StringOrStringArray]] = ...) -> None: ...

class ShardStatistics(_message.Message):
    __slots__ = ("failed", "successful", "total", "failures", "skipped")
    FAILED_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    FAILURES_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    failed: int
    successful: int
    total: int
    failures: _containers.RepeatedCompositeFieldContainer[ShardFailure]
    skipped: int
    def __init__(self, failed: _Optional[int] = ..., successful: _Optional[int] = ..., total: _Optional[int] = ..., failures: _Optional[_Iterable[_Union[ShardFailure, _Mapping]]] = ..., skipped: _Optional[int] = ...) -> None: ...

class ShardInfo(_message.Message):
    __slots__ = ("failed", "successful", "total", "failures")
    FAILED_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    FAILURES_FIELD_NUMBER: _ClassVar[int]
    failed: int
    successful: int
    total: int
    failures: _containers.RepeatedCompositeFieldContainer[ShardFailure]
    def __init__(self, failed: _Optional[int] = ..., successful: _Optional[int] = ..., total: _Optional[int] = ..., failures: _Optional[_Iterable[_Union[ShardFailure, _Mapping]]] = ...) -> None: ...

class ShardFailure(_message.Message):
    __slots__ = ("index", "node", "reason", "shard", "status", "primary")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SHARD_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_FIELD_NUMBER: _ClassVar[int]
    index: str
    node: str
    reason: ErrorCause
    shard: int
    status: str
    primary: bool
    def __init__(self, index: _Optional[str] = ..., node: _Optional[str] = ..., reason: _Optional[_Union[ErrorCause, _Mapping]] = ..., shard: _Optional[int] = ..., status: _Optional[str] = ..., primary: bool = ...) -> None: ...

class ShardSearchFailure(_message.Message):
    __slots__ = ("index", "node", "reason", "shard", "status")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SHARD_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    index: str
    node: str
    reason: ErrorCause
    shard: int
    status: str
    def __init__(self, index: _Optional[str] = ..., node: _Optional[str] = ..., reason: _Optional[_Union[ErrorCause, _Mapping]] = ..., shard: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class QueryContainer(_message.Message):
    __slots__ = ("bool", "boosting", "constant_score", "dis_max", "function_score", "exists", "fuzzy", "ids", "prefix", "range", "regexp", "term", "terms", "terms_set", "wildcard", "match", "match_bool_prefix", "match_phrase", "match_phrase_prefix", "multi_match", "query_string", "simple_query_string", "intervals", "knn", "match_all", "match_none", "script_score", "nested", "geo_distance", "geo_bounding_box", "script")
    BOOL_FIELD_NUMBER: _ClassVar[int]
    BOOSTING_FIELD_NUMBER: _ClassVar[int]
    CONSTANT_SCORE_FIELD_NUMBER: _ClassVar[int]
    DIS_MAX_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_SCORE_FIELD_NUMBER: _ClassVar[int]
    EXISTS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    REGEXP_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    TERMS_SET_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    MATCH_BOOL_PREFIX_FIELD_NUMBER: _ClassVar[int]
    MATCH_PHRASE_FIELD_NUMBER: _ClassVar[int]
    MATCH_PHRASE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    MULTI_MATCH_FIELD_NUMBER: _ClassVar[int]
    QUERY_STRING_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_QUERY_STRING_FIELD_NUMBER: _ClassVar[int]
    INTERVALS_FIELD_NUMBER: _ClassVar[int]
    KNN_FIELD_NUMBER: _ClassVar[int]
    MATCH_ALL_FIELD_NUMBER: _ClassVar[int]
    MATCH_NONE_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_SCORE_FIELD_NUMBER: _ClassVar[int]
    NESTED_FIELD_NUMBER: _ClassVar[int]
    GEO_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    GEO_BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    bool: BoolQuery
    boosting: BoostingQuery
    constant_score: ConstantScoreQuery
    dis_max: DisMaxQuery
    function_score: FunctionScoreQuery
    exists: ExistsQuery
    fuzzy: FuzzyQuery
    ids: IdsQuery
    prefix: PrefixQuery
    range: RangeQuery
    regexp: RegexpQuery
    term: TermQuery
    terms: TermsQuery
    terms_set: TermsSetQuery
    wildcard: WildcardQuery
    match: MatchQuery
    match_bool_prefix: MatchBoolPrefixQuery
    match_phrase: MatchPhraseQuery
    match_phrase_prefix: MatchPhrasePrefixQuery
    multi_match: MultiMatchQuery
    query_string: QueryStringQuery
    simple_query_string: SimpleQueryStringQuery
    intervals: IntervalsQuery
    knn: KnnQuery
    match_all: MatchAllQuery
    match_none: MatchNoneQuery
    script_score: ScriptScoreQuery
    nested: NestedQuery
    geo_distance: GeoDistanceQuery
    geo_bounding_box: GeoBoundingBoxQuery
    script: ScriptQuery
    def __init__(self, bool: _Optional[_Union[BoolQuery, _Mapping]] = ..., boosting: _Optional[_Union[BoostingQuery, _Mapping]] = ..., constant_score: _Optional[_Union[ConstantScoreQuery, _Mapping]] = ..., dis_max: _Optional[_Union[DisMaxQuery, _Mapping]] = ..., function_score: _Optional[_Union[FunctionScoreQuery, _Mapping]] = ..., exists: _Optional[_Union[ExistsQuery, _Mapping]] = ..., fuzzy: _Optional[_Union[FuzzyQuery, _Mapping]] = ..., ids: _Optional[_Union[IdsQuery, _Mapping]] = ..., prefix: _Optional[_Union[PrefixQuery, _Mapping]] = ..., range: _Optional[_Union[RangeQuery, _Mapping]] = ..., regexp: _Optional[_Union[RegexpQuery, _Mapping]] = ..., term: _Optional[_Union[TermQuery, _Mapping]] = ..., terms: _Optional[_Union[TermsQuery, _Mapping]] = ..., terms_set: _Optional[_Union[TermsSetQuery, _Mapping]] = ..., wildcard: _Optional[_Union[WildcardQuery, _Mapping]] = ..., match: _Optional[_Union[MatchQuery, _Mapping]] = ..., match_bool_prefix: _Optional[_Union[MatchBoolPrefixQuery, _Mapping]] = ..., match_phrase: _Optional[_Union[MatchPhraseQuery, _Mapping]] = ..., match_phrase_prefix: _Optional[_Union[MatchPhrasePrefixQuery, _Mapping]] = ..., multi_match: _Optional[_Union[MultiMatchQuery, _Mapping]] = ..., query_string: _Optional[_Union[QueryStringQuery, _Mapping]] = ..., simple_query_string: _Optional[_Union[SimpleQueryStringQuery, _Mapping]] = ..., intervals: _Optional[_Union[IntervalsQuery, _Mapping]] = ..., knn: _Optional[_Union[KnnQuery, _Mapping]] = ..., match_all: _Optional[_Union[MatchAllQuery, _Mapping]] = ..., match_none: _Optional[_Union[MatchNoneQuery, _Mapping]] = ..., script_score: _Optional[_Union[ScriptScoreQuery, _Mapping]] = ..., nested: _Optional[_Union[NestedQuery, _Mapping]] = ..., geo_distance: _Optional[_Union[GeoDistanceQuery, _Mapping]] = ..., geo_bounding_box: _Optional[_Union[GeoBoundingBoxQuery, _Mapping]] = ..., script: _Optional[_Union[ScriptQuery, _Mapping]] = ...) -> None: ...

class ScriptQuery(_message.Message):
    __slots__ = ("script", "boost", "x_name")
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    script: Script
    boost: float
    x_name: str
    def __init__(self, script: _Optional[_Union[Script, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ...) -> None: ...

class GeoBoundingBoxQuery(_message.Message):
    __slots__ = ("boost", "x_name", "type", "validation_method", "ignore_unmapped", "bounding_box")
    class BoundingBoxEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: GeoBounds
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[GeoBounds, _Mapping]] = ...) -> None: ...
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_METHOD_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    type: GeoExecution
    validation_method: GeoValidationMethod
    ignore_unmapped: bool
    bounding_box: _containers.MessageMap[str, GeoBounds]
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., type: _Optional[_Union[GeoExecution, str]] = ..., validation_method: _Optional[_Union[GeoValidationMethod, str]] = ..., ignore_unmapped: bool = ..., bounding_box: _Optional[_Mapping[str, GeoBounds]] = ...) -> None: ...

class GeoBounds(_message.Message):
    __slots__ = ("coords", "tlbr", "trbl", "wkt")
    COORDS_FIELD_NUMBER: _ClassVar[int]
    TLBR_FIELD_NUMBER: _ClassVar[int]
    TRBL_FIELD_NUMBER: _ClassVar[int]
    WKT_FIELD_NUMBER: _ClassVar[int]
    coords: CoordsGeoBounds
    tlbr: TopLeftBottomRightGeoBounds
    trbl: TopRightBottomLeftGeoBounds
    wkt: WktGeoBounds
    def __init__(self, coords: _Optional[_Union[CoordsGeoBounds, _Mapping]] = ..., tlbr: _Optional[_Union[TopLeftBottomRightGeoBounds, _Mapping]] = ..., trbl: _Optional[_Union[TopRightBottomLeftGeoBounds, _Mapping]] = ..., wkt: _Optional[_Union[WktGeoBounds, _Mapping]] = ...) -> None: ...

class WktGeoBounds(_message.Message):
    __slots__ = ("wkt",)
    WKT_FIELD_NUMBER: _ClassVar[int]
    wkt: str
    def __init__(self, wkt: _Optional[str] = ...) -> None: ...

class CoordsGeoBounds(_message.Message):
    __slots__ = ("top", "bottom", "left", "right")
    TOP_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_FIELD_NUMBER: _ClassVar[int]
    LEFT_FIELD_NUMBER: _ClassVar[int]
    RIGHT_FIELD_NUMBER: _ClassVar[int]
    top: float
    bottom: float
    left: float
    right: float
    def __init__(self, top: _Optional[float] = ..., bottom: _Optional[float] = ..., left: _Optional[float] = ..., right: _Optional[float] = ...) -> None: ...

class TopLeftBottomRightGeoBounds(_message.Message):
    __slots__ = ("top_left", "bottom_right")
    TOP_LEFT_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_RIGHT_FIELD_NUMBER: _ClassVar[int]
    top_left: GeoLocation
    bottom_right: GeoLocation
    def __init__(self, top_left: _Optional[_Union[GeoLocation, _Mapping]] = ..., bottom_right: _Optional[_Union[GeoLocation, _Mapping]] = ...) -> None: ...

class TopRightBottomLeftGeoBounds(_message.Message):
    __slots__ = ("top_right", "bottom_left")
    TOP_RIGHT_FIELD_NUMBER: _ClassVar[int]
    BOTTOM_LEFT_FIELD_NUMBER: _ClassVar[int]
    top_right: GeoLocation
    bottom_left: GeoLocation
    def __init__(self, top_right: _Optional[_Union[GeoLocation, _Mapping]] = ..., bottom_left: _Optional[_Union[GeoLocation, _Mapping]] = ...) -> None: ...

class GeoDistanceQuery(_message.Message):
    __slots__ = ("distance", "boost", "x_name", "distance_type", "validation_method", "ignore_unmapped", "unit", "location")
    class LocationEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: GeoLocation
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[GeoLocation, _Mapping]] = ...) -> None: ...
    DISTANCE_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_METHOD_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    distance: str
    boost: float
    x_name: str
    distance_type: GeoDistanceType
    validation_method: GeoValidationMethod
    ignore_unmapped: bool
    unit: DistanceUnit
    location: _containers.MessageMap[str, GeoLocation]
    def __init__(self, distance: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., distance_type: _Optional[_Union[GeoDistanceType, str]] = ..., validation_method: _Optional[_Union[GeoValidationMethod, str]] = ..., ignore_unmapped: bool = ..., unit: _Optional[_Union[DistanceUnit, str]] = ..., location: _Optional[_Mapping[str, GeoLocation]] = ...) -> None: ...

class TermsQuery(_message.Message):
    __slots__ = ("boost", "x_name", "value_type", "terms")
    class TermsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TermsQueryField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TermsQueryField, _Mapping]] = ...) -> None: ...
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    value_type: TermsQueryValueType
    terms: _containers.MessageMap[str, TermsQueryField]
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., value_type: _Optional[_Union[TermsQueryValueType, str]] = ..., terms: _Optional[_Mapping[str, TermsQueryField]] = ...) -> None: ...

class NestedQuery(_message.Message):
    __slots__ = ("path", "query", "boost", "x_name", "ignore_unmapped", "inner_hits", "score_mode")
    PATH_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    INNER_HITS_FIELD_NUMBER: _ClassVar[int]
    SCORE_MODE_FIELD_NUMBER: _ClassVar[int]
    path: str
    query: QueryContainer
    boost: float
    x_name: str
    ignore_unmapped: bool
    inner_hits: InnerHits
    score_mode: ChildScoreMode
    def __init__(self, path: _Optional[str] = ..., query: _Optional[_Union[QueryContainer, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., ignore_unmapped: bool = ..., inner_hits: _Optional[_Union[InnerHits, _Mapping]] = ..., score_mode: _Optional[_Union[ChildScoreMode, str]] = ...) -> None: ...

class InnerHits(_message.Message):
    __slots__ = ("name", "size", "collapse", "docvalue_fields", "explain", "highlight", "ignore_unmapped", "script_fields", "seq_no_primary_term", "fields", "sort", "x_source", "stored_fields", "track_scores", "version")
    class ScriptFieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ScriptField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ScriptField, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    COLLAPSE_FIELD_NUMBER: _ClassVar[int]
    DOCVALUE_FIELDS_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    SEQ_NO_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    STORED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    TRACK_SCORES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    size: int
    collapse: FieldCollapse
    docvalue_fields: _containers.RepeatedCompositeFieldContainer[FieldAndFormat]
    explain: bool
    highlight: Highlight
    ignore_unmapped: bool
    script_fields: _containers.MessageMap[str, ScriptField]
    seq_no_primary_term: bool
    fields: _containers.RepeatedCompositeFieldContainer[FieldAndFormat]
    sort: _containers.RepeatedCompositeFieldContainer[SortCombinations]
    x_source: SourceConfig
    stored_fields: _containers.RepeatedScalarFieldContainer[str]
    track_scores: bool
    version: bool
    def __init__(self, name: _Optional[str] = ..., size: _Optional[int] = ..., collapse: _Optional[_Union[FieldCollapse, _Mapping]] = ..., docvalue_fields: _Optional[_Iterable[_Union[FieldAndFormat, _Mapping]]] = ..., explain: bool = ..., highlight: _Optional[_Union[Highlight, _Mapping]] = ..., ignore_unmapped: bool = ..., script_fields: _Optional[_Mapping[str, ScriptField]] = ..., seq_no_primary_term: bool = ..., fields: _Optional[_Iterable[_Union[FieldAndFormat, _Mapping]]] = ..., sort: _Optional[_Iterable[_Union[SortCombinations, _Mapping]]] = ..., x_source: _Optional[_Union[SourceConfig, _Mapping]] = ..., stored_fields: _Optional[_Iterable[str]] = ..., track_scores: bool = ..., version: bool = ..., **kwargs) -> None: ...

class ScriptField(_message.Message):
    __slots__ = ("script", "ignore_failure")
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    IGNORE_FAILURE_FIELD_NUMBER: _ClassVar[int]
    script: Script
    ignore_failure: bool
    def __init__(self, script: _Optional[_Union[Script, _Mapping]] = ..., ignore_failure: bool = ...) -> None: ...

class HighlighterType(_message.Message):
    __slots__ = ("builtin", "custom")
    BUILTIN_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_FIELD_NUMBER: _ClassVar[int]
    builtin: BuiltinHighlighterType
    custom: str
    def __init__(self, builtin: _Optional[_Union[BuiltinHighlighterType, str]] = ..., custom: _Optional[str] = ...) -> None: ...

class SortCombinations(_message.Message):
    __slots__ = ("field", "field_with_direction", "field_with_order", "options")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FIELD_WITH_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    FIELD_WITH_ORDER_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    field: str
    field_with_direction: SortOrderMap
    field_with_order: FieldSortMap
    options: SortOptions
    def __init__(self, field: _Optional[str] = ..., field_with_direction: _Optional[_Union[SortOrderMap, _Mapping]] = ..., field_with_order: _Optional[_Union[FieldSortMap, _Mapping]] = ..., options: _Optional[_Union[SortOptions, _Mapping]] = ...) -> None: ...

class SortOrderMap(_message.Message):
    __slots__ = ("sort_order_map",)
    class SortOrderMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SortOrder
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SortOrder, str]] = ...) -> None: ...
    SORT_ORDER_MAP_FIELD_NUMBER: _ClassVar[int]
    sort_order_map: _containers.ScalarMap[str, SortOrder]
    def __init__(self, sort_order_map: _Optional[_Mapping[str, SortOrder]] = ...) -> None: ...

class FieldSortMap(_message.Message):
    __slots__ = ("field_sort_map",)
    class FieldSortMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FieldSort
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FieldSort, _Mapping]] = ...) -> None: ...
    FIELD_SORT_MAP_FIELD_NUMBER: _ClassVar[int]
    field_sort_map: _containers.MessageMap[str, FieldSort]
    def __init__(self, field_sort_map: _Optional[_Mapping[str, FieldSort]] = ...) -> None: ...

class SortOptions(_message.Message):
    __slots__ = ("x_score", "x_geo_distance", "x_script")
    X_SCORE_FIELD_NUMBER: _ClassVar[int]
    X_GEO_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    X_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    x_score: ScoreSort
    x_geo_distance: GeoDistanceSort
    x_script: ScriptSort
    def __init__(self, x_score: _Optional[_Union[ScoreSort, _Mapping]] = ..., x_geo_distance: _Optional[_Union[GeoDistanceSort, _Mapping]] = ..., x_script: _Optional[_Union[ScriptSort, _Mapping]] = ...) -> None: ...

class Highlight(_message.Message):
    __slots__ = ("type", "boundary_chars", "boundary_max_scan", "boundary_scanner", "boundary_scanner_locale", "force_source", "fragmenter", "fragment_offset", "fragment_size", "highlight_filter", "highlight_query", "max_fragment_length", "max_analyzed_offset", "no_match_size", "number_of_fragments", "options", "order", "phrase_limit", "post_tags", "pre_tags", "require_field_match", "tags_schema", "encoder", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: HighlightField
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[HighlightField, _Mapping]] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_CHARS_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_MAX_SCAN_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_SCANNER_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_SCANNER_LOCALE_FIELD_NUMBER: _ClassVar[int]
    FORCE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTER_FIELD_NUMBER: _ClassVar[int]
    FRAGMENT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    FRAGMENT_SIZE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_FILTER_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_QUERY_FIELD_NUMBER: _ClassVar[int]
    MAX_FRAGMENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MAX_ANALYZED_OFFSET_FIELD_NUMBER: _ClassVar[int]
    NO_MATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FRAGMENTS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    PHRASE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    POST_TAGS_FIELD_NUMBER: _ClassVar[int]
    PRE_TAGS_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_FIELD_MATCH_FIELD_NUMBER: _ClassVar[int]
    TAGS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    ENCODER_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    type: HighlighterType
    boundary_chars: str
    boundary_max_scan: int
    boundary_scanner: BoundaryScanner
    boundary_scanner_locale: str
    force_source: bool
    fragmenter: HighlighterFragmenter
    fragment_offset: int
    fragment_size: int
    highlight_filter: bool
    highlight_query: QueryContainer
    max_fragment_length: int
    max_analyzed_offset: int
    no_match_size: int
    number_of_fragments: int
    options: ObjectMap
    order: HighlighterOrder
    phrase_limit: int
    post_tags: _containers.RepeatedScalarFieldContainer[str]
    pre_tags: _containers.RepeatedScalarFieldContainer[str]
    require_field_match: bool
    tags_schema: HighlighterTagsSchema
    encoder: HighlighterEncoder
    fields: _containers.MessageMap[str, HighlightField]
    def __init__(self, type: _Optional[_Union[HighlighterType, _Mapping]] = ..., boundary_chars: _Optional[str] = ..., boundary_max_scan: _Optional[int] = ..., boundary_scanner: _Optional[_Union[BoundaryScanner, str]] = ..., boundary_scanner_locale: _Optional[str] = ..., force_source: bool = ..., fragmenter: _Optional[_Union[HighlighterFragmenter, str]] = ..., fragment_offset: _Optional[int] = ..., fragment_size: _Optional[int] = ..., highlight_filter: bool = ..., highlight_query: _Optional[_Union[QueryContainer, _Mapping]] = ..., max_fragment_length: _Optional[int] = ..., max_analyzed_offset: _Optional[int] = ..., no_match_size: _Optional[int] = ..., number_of_fragments: _Optional[int] = ..., options: _Optional[_Union[ObjectMap, _Mapping]] = ..., order: _Optional[_Union[HighlighterOrder, str]] = ..., phrase_limit: _Optional[int] = ..., post_tags: _Optional[_Iterable[str]] = ..., pre_tags: _Optional[_Iterable[str]] = ..., require_field_match: bool = ..., tags_schema: _Optional[_Union[HighlighterTagsSchema, str]] = ..., encoder: _Optional[_Union[HighlighterEncoder, str]] = ..., fields: _Optional[_Mapping[str, HighlightField]] = ...) -> None: ...

class HighlightField(_message.Message):
    __slots__ = ("type", "boundary_chars", "boundary_max_scan", "boundary_scanner", "boundary_scanner_locale", "force_source", "fragmenter", "fragment_size", "highlight_filter", "highlight_query", "max_fragment_length", "max_analyzed_offset", "no_match_size", "number_of_fragments", "options", "order", "phrase_limit", "post_tags", "pre_tags", "require_field_match", "tags_schema", "fragment_offset", "matched_fields")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_CHARS_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_MAX_SCAN_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_SCANNER_FIELD_NUMBER: _ClassVar[int]
    BOUNDARY_SCANNER_LOCALE_FIELD_NUMBER: _ClassVar[int]
    FORCE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTER_FIELD_NUMBER: _ClassVar[int]
    FRAGMENT_SIZE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_FILTER_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHT_QUERY_FIELD_NUMBER: _ClassVar[int]
    MAX_FRAGMENT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MAX_ANALYZED_OFFSET_FIELD_NUMBER: _ClassVar[int]
    NO_MATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_FRAGMENTS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    PHRASE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    POST_TAGS_FIELD_NUMBER: _ClassVar[int]
    PRE_TAGS_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_FIELD_MATCH_FIELD_NUMBER: _ClassVar[int]
    TAGS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FRAGMENT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    MATCHED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    type: HighlighterType
    boundary_chars: str
    boundary_max_scan: int
    boundary_scanner: BoundaryScanner
    boundary_scanner_locale: str
    force_source: bool
    fragmenter: HighlighterFragmenter
    fragment_size: int
    highlight_filter: bool
    highlight_query: QueryContainer
    max_fragment_length: int
    max_analyzed_offset: int
    no_match_size: int
    number_of_fragments: int
    options: ObjectMap
    order: HighlighterOrder
    phrase_limit: int
    post_tags: _containers.RepeatedScalarFieldContainer[str]
    pre_tags: _containers.RepeatedScalarFieldContainer[str]
    require_field_match: bool
    tags_schema: HighlighterTagsSchema
    fragment_offset: int
    matched_fields: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[HighlighterType, _Mapping]] = ..., boundary_chars: _Optional[str] = ..., boundary_max_scan: _Optional[int] = ..., boundary_scanner: _Optional[_Union[BoundaryScanner, str]] = ..., boundary_scanner_locale: _Optional[str] = ..., force_source: bool = ..., fragmenter: _Optional[_Union[HighlighterFragmenter, str]] = ..., fragment_size: _Optional[int] = ..., highlight_filter: bool = ..., highlight_query: _Optional[_Union[QueryContainer, _Mapping]] = ..., max_fragment_length: _Optional[int] = ..., max_analyzed_offset: _Optional[int] = ..., no_match_size: _Optional[int] = ..., number_of_fragments: _Optional[int] = ..., options: _Optional[_Union[ObjectMap, _Mapping]] = ..., order: _Optional[_Union[HighlighterOrder, str]] = ..., phrase_limit: _Optional[int] = ..., post_tags: _Optional[_Iterable[str]] = ..., pre_tags: _Optional[_Iterable[str]] = ..., require_field_match: bool = ..., tags_schema: _Optional[_Union[HighlighterTagsSchema, str]] = ..., fragment_offset: _Optional[int] = ..., matched_fields: _Optional[_Iterable[str]] = ...) -> None: ...

class FieldWithOrderMap(_message.Message):
    __slots__ = ("field_with_order_map",)
    class FieldWithOrderMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ScoreSort
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ScoreSort, _Mapping]] = ...) -> None: ...
    FIELD_WITH_ORDER_MAP_FIELD_NUMBER: _ClassVar[int]
    field_with_order_map: _containers.MessageMap[str, ScoreSort]
    def __init__(self, field_with_order_map: _Optional[_Mapping[str, ScoreSort]] = ...) -> None: ...

class FieldSort(_message.Message):
    __slots__ = ("missing", "mode", "nested", "order", "unmapped_type", "numeric_type")
    MISSING_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NESTED_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    UNMAPPED_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_TYPE_FIELD_NUMBER: _ClassVar[int]
    missing: FieldValue
    mode: SortMode
    nested: NestedSortValue
    order: SortOrder
    unmapped_type: FieldType
    numeric_type: FieldSortNumericType
    def __init__(self, missing: _Optional[_Union[FieldValue, _Mapping]] = ..., mode: _Optional[_Union[SortMode, str]] = ..., nested: _Optional[_Union[NestedSortValue, _Mapping]] = ..., order: _Optional[_Union[SortOrder, str]] = ..., unmapped_type: _Optional[_Union[FieldType, str]] = ..., numeric_type: _Optional[_Union[FieldSortNumericType, str]] = ...) -> None: ...

class ScoreSort(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: SortOrder
    def __init__(self, order: _Optional[_Union[SortOrder, str]] = ...) -> None: ...

class GeoDistanceSort(_message.Message):
    __slots__ = ("mode", "distance_type", "ignore_unmapped", "nested", "order", "unit", "validation_method", "location")
    class LocationEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: GeoLocationArray
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[GeoLocationArray, _Mapping]] = ...) -> None: ...
    MODE_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IGNORE_UNMAPPED_FIELD_NUMBER: _ClassVar[int]
    NESTED_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_METHOD_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    mode: SortMode
    distance_type: GeoDistanceType
    ignore_unmapped: bool
    nested: NestedSortValue
    order: SortOrder
    unit: DistanceUnit
    validation_method: GeoValidationMethod
    location: _containers.MessageMap[str, GeoLocationArray]
    def __init__(self, mode: _Optional[_Union[SortMode, str]] = ..., distance_type: _Optional[_Union[GeoDistanceType, str]] = ..., ignore_unmapped: bool = ..., nested: _Optional[_Union[NestedSortValue, _Mapping]] = ..., order: _Optional[_Union[SortOrder, str]] = ..., unit: _Optional[_Union[DistanceUnit, str]] = ..., validation_method: _Optional[_Union[GeoValidationMethod, str]] = ..., location: _Optional[_Mapping[str, GeoLocationArray]] = ...) -> None: ...

class GeoLocationArray(_message.Message):
    __slots__ = ("geo_location_array",)
    GEO_LOCATION_ARRAY_FIELD_NUMBER: _ClassVar[int]
    geo_location_array: _containers.RepeatedCompositeFieldContainer[GeoLocation]
    def __init__(self, geo_location_array: _Optional[_Iterable[_Union[GeoLocation, _Mapping]]] = ...) -> None: ...

class ScriptSort(_message.Message):
    __slots__ = ("script", "order", "type", "mode", "nested")
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    NESTED_FIELD_NUMBER: _ClassVar[int]
    script: Script
    order: SortOrder
    type: ScriptSortType
    mode: SortMode
    nested: NestedSortValue
    def __init__(self, script: _Optional[_Union[Script, _Mapping]] = ..., order: _Optional[_Union[SortOrder, str]] = ..., type: _Optional[_Union[ScriptSortType, str]] = ..., mode: _Optional[_Union[SortMode, str]] = ..., nested: _Optional[_Union[NestedSortValue, _Mapping]] = ...) -> None: ...

class NestedSortValue(_message.Message):
    __slots__ = ("path", "filter", "max_children", "nested")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_CHILDREN_FIELD_NUMBER: _ClassVar[int]
    NESTED_FIELD_NUMBER: _ClassVar[int]
    path: str
    filter: QueryContainer
    max_children: int
    nested: NestedSortValue
    def __init__(self, path: _Optional[str] = ..., filter: _Optional[_Union[QueryContainer, _Mapping]] = ..., max_children: _Optional[int] = ..., nested: _Optional[_Union[NestedSortValue, _Mapping]] = ...) -> None: ...

class FieldAndFormat(_message.Message):
    __slots__ = ("field", "format")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    field: str
    format: str
    def __init__(self, field: _Optional[str] = ..., format: _Optional[str] = ...) -> None: ...

class FieldCollapse(_message.Message):
    __slots__ = ("field", "inner_hits", "max_concurrent_group_searches")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    INNER_HITS_FIELD_NUMBER: _ClassVar[int]
    MAX_CONCURRENT_GROUP_SEARCHES_FIELD_NUMBER: _ClassVar[int]
    field: str
    inner_hits: _containers.RepeatedCompositeFieldContainer[InnerHits]
    max_concurrent_group_searches: int
    def __init__(self, field: _Optional[str] = ..., inner_hits: _Optional[_Iterable[_Union[InnerHits, _Mapping]]] = ..., max_concurrent_group_searches: _Optional[int] = ...) -> None: ...

class ScriptScoreQuery(_message.Message):
    __slots__ = ("boost", "x_name", "min_score", "query", "script")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    min_score: float
    query: QueryContainer
    script: Script
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., min_score: _Optional[float] = ..., query: _Optional[_Union[QueryContainer, _Mapping]] = ..., script: _Optional[_Union[Script, _Mapping]] = ...) -> None: ...

class ExistsQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ...) -> None: ...

class SimpleQueryStringQuery(_message.Message):
    __slots__ = ("boost", "x_name", "analyzer", "analyze_wildcard", "auto_generate_synonyms_phrase_query", "default_operator", "fields", "flags", "fuzzy_max_expansions", "fuzzy_prefix_length", "fuzzy_transpositions", "lenient", "minimum_should_match", "query", "quote_field_suffix")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_WILDCARD_FIELD_NUMBER: _ClassVar[int]
    AUTO_GENERATE_SYNONYMS_PHRASE_QUERY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_OPERATOR_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    FUZZY_TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    LENIENT_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    QUOTE_FIELD_SUFFIX_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    analyzer: str
    analyze_wildcard: bool
    auto_generate_synonyms_phrase_query: bool
    default_operator: Operator
    fields: _containers.RepeatedScalarFieldContainer[str]
    flags: SimpleQueryStringFlags
    fuzzy_max_expansions: int
    fuzzy_prefix_length: int
    fuzzy_transpositions: bool
    lenient: bool
    minimum_should_match: MinimumShouldMatch
    query: str
    quote_field_suffix: str
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., analyze_wildcard: bool = ..., auto_generate_synonyms_phrase_query: bool = ..., default_operator: _Optional[_Union[Operator, str]] = ..., fields: _Optional[_Iterable[str]] = ..., flags: _Optional[_Union[SimpleQueryStringFlags, _Mapping]] = ..., fuzzy_max_expansions: _Optional[int] = ..., fuzzy_prefix_length: _Optional[int] = ..., fuzzy_transpositions: bool = ..., lenient: bool = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., query: _Optional[str] = ..., quote_field_suffix: _Optional[str] = ...) -> None: ...

class WildcardQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name", "case_insensitive", "rewrite", "value", "wildcard")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
    REWRITE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    case_insensitive: bool
    rewrite: MultiTermQueryRewrite
    value: str
    wildcard: str
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., case_insensitive: bool = ..., rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., value: _Optional[str] = ..., wildcard: _Optional[str] = ...) -> None: ...

class SimpleQueryStringFlags(_message.Message):
    __slots__ = ("single", "multiple")
    SINGLE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLE_FIELD_NUMBER: _ClassVar[int]
    single: SimpleQueryStringFlag
    multiple: str
    def __init__(self, single: _Optional[_Union[SimpleQueryStringFlag, str]] = ..., multiple: _Optional[str] = ...) -> None: ...

class KnnQuery(_message.Message):
    __slots__ = ("field", "vector", "k", "min_score", "max_distance", "filter", "boost", "x_name", "method_parameters", "rescore", "expand_nested_docs")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    MAX_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    METHOD_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    RESCORE_FIELD_NUMBER: _ClassVar[int]
    EXPAND_NESTED_DOCS_FIELD_NUMBER: _ClassVar[int]
    field: str
    vector: _containers.RepeatedScalarFieldContainer[float]
    k: int
    min_score: float
    max_distance: float
    filter: QueryContainer
    boost: float
    x_name: str
    method_parameters: ObjectMap
    rescore: KnnQueryRescore
    expand_nested_docs: bool
    def __init__(self, field: _Optional[str] = ..., vector: _Optional[_Iterable[float]] = ..., k: _Optional[int] = ..., min_score: _Optional[float] = ..., max_distance: _Optional[float] = ..., filter: _Optional[_Union[QueryContainer, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., method_parameters: _Optional[_Union[ObjectMap, _Mapping]] = ..., rescore: _Optional[_Union[KnnQueryRescore, _Mapping]] = ..., expand_nested_docs: bool = ...) -> None: ...

class RescoreContext(_message.Message):
    __slots__ = ("oversample_factor",)
    OVERSAMPLE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    oversample_factor: float
    def __init__(self, oversample_factor: _Optional[float] = ...) -> None: ...

class KnnQueryRescore(_message.Message):
    __slots__ = ("enable", "context")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    context: RescoreContext
    def __init__(self, enable: bool = ..., context: _Optional[_Union[RescoreContext, _Mapping]] = ...) -> None: ...

class MatchQuery(_message.Message):
    __slots__ = ("field", "query", "boost", "x_name", "analyzer", "auto_generate_synonyms_phrase_query", "fuzziness", "fuzzy_rewrite", "fuzzy_transpositions", "lenient", "max_expansions", "minimum_should_match", "operator", "prefix_length", "zero_terms_query")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    AUTO_GENERATE_SYNONYMS_PHRASE_QUERY_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_REWRITE_FIELD_NUMBER: _ClassVar[int]
    FUZZY_TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    LENIENT_FIELD_NUMBER: _ClassVar[int]
    MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    ZERO_TERMS_QUERY_FIELD_NUMBER: _ClassVar[int]
    field: str
    query: FieldValue
    boost: float
    x_name: str
    analyzer: str
    auto_generate_synonyms_phrase_query: bool
    fuzziness: Fuzziness
    fuzzy_rewrite: MultiTermQueryRewrite
    fuzzy_transpositions: bool
    lenient: bool
    max_expansions: int
    minimum_should_match: MinimumShouldMatch
    operator: Operator
    prefix_length: int
    zero_terms_query: ZeroTermsQuery
    def __init__(self, field: _Optional[str] = ..., query: _Optional[_Union[FieldValue, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., auto_generate_synonyms_phrase_query: bool = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ..., fuzzy_rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., fuzzy_transpositions: bool = ..., lenient: bool = ..., max_expansions: _Optional[int] = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., operator: _Optional[_Union[Operator, str]] = ..., prefix_length: _Optional[int] = ..., zero_terms_query: _Optional[_Union[ZeroTermsQuery, str]] = ...) -> None: ...

class Query(_message.Message):
    __slots__ = ("string", "general_number", "bool")
    STRING_FIELD_NUMBER: _ClassVar[int]
    GENERAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    BOOL_FIELD_NUMBER: _ClassVar[int]
    string: str
    general_number: GeneralNumber
    bool: bool
    def __init__(self, string: _Optional[str] = ..., general_number: _Optional[_Union[GeneralNumber, _Mapping]] = ..., bool: bool = ...) -> None: ...

class BoolQuery(_message.Message):
    __slots__ = ("boost", "x_name", "filter", "minimum_should_match", "must", "must_not", "should", "adjust_pure_negative")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    MUST_FIELD_NUMBER: _ClassVar[int]
    MUST_NOT_FIELD_NUMBER: _ClassVar[int]
    SHOULD_FIELD_NUMBER: _ClassVar[int]
    ADJUST_PURE_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    filter: _containers.RepeatedCompositeFieldContainer[QueryContainer]
    minimum_should_match: MinimumShouldMatch
    must: _containers.RepeatedCompositeFieldContainer[QueryContainer]
    must_not: _containers.RepeatedCompositeFieldContainer[QueryContainer]
    should: _containers.RepeatedCompositeFieldContainer[QueryContainer]
    adjust_pure_negative: bool
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., filter: _Optional[_Iterable[_Union[QueryContainer, _Mapping]]] = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., must: _Optional[_Iterable[_Union[QueryContainer, _Mapping]]] = ..., must_not: _Optional[_Iterable[_Union[QueryContainer, _Mapping]]] = ..., should: _Optional[_Iterable[_Union[QueryContainer, _Mapping]]] = ..., adjust_pure_negative: bool = ...) -> None: ...

class MinimumShouldMatch(_message.Message):
    __slots__ = ("int32", "string")
    INT32_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    int32: int
    string: str
    def __init__(self, int32: _Optional[int] = ..., string: _Optional[str] = ...) -> None: ...

class BoostingQuery(_message.Message):
    __slots__ = ("boost", "x_name", "negative_boost", "negative", "positive")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_BOOST_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    POSITIVE_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    negative_boost: float
    negative: QueryContainer
    positive: QueryContainer
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., negative_boost: _Optional[float] = ..., negative: _Optional[_Union[QueryContainer, _Mapping]] = ..., positive: _Optional[_Union[QueryContainer, _Mapping]] = ...) -> None: ...

class ConstantScoreQuery(_message.Message):
    __slots__ = ("filter", "boost", "x_name")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    filter: QueryContainer
    boost: float
    x_name: str
    def __init__(self, filter: _Optional[_Union[QueryContainer, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ...) -> None: ...

class DisMaxQuery(_message.Message):
    __slots__ = ("boost", "x_name", "queries", "tie_breaker")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    QUERIES_FIELD_NUMBER: _ClassVar[int]
    TIE_BREAKER_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    queries: _containers.RepeatedCompositeFieldContainer[QueryContainer]
    tie_breaker: float
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., queries: _Optional[_Iterable[_Union[QueryContainer, _Mapping]]] = ..., tie_breaker: _Optional[float] = ...) -> None: ...

class FunctionScoreQuery(_message.Message):
    __slots__ = ("boost", "x_name", "boost_mode", "functions", "max_boost", "min_score", "query", "score_mode")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    BOOST_MODE_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_BOOST_FIELD_NUMBER: _ClassVar[int]
    MIN_SCORE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SCORE_MODE_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    boost_mode: FunctionBoostMode
    functions: _containers.RepeatedCompositeFieldContainer[FunctionScoreContainer]
    max_boost: float
    min_score: float
    query: QueryContainer
    score_mode: FunctionScoreMode
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., boost_mode: _Optional[_Union[FunctionBoostMode, str]] = ..., functions: _Optional[_Iterable[_Union[FunctionScoreContainer, _Mapping]]] = ..., max_boost: _Optional[float] = ..., min_score: _Optional[float] = ..., query: _Optional[_Union[QueryContainer, _Mapping]] = ..., score_mode: _Optional[_Union[FunctionScoreMode, str]] = ...) -> None: ...

class IntervalsAllOf(_message.Message):
    __slots__ = ("intervals", "max_gaps", "ordered", "filter")
    INTERVALS_FIELD_NUMBER: _ClassVar[int]
    MAX_GAPS_FIELD_NUMBER: _ClassVar[int]
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    intervals: _containers.RepeatedCompositeFieldContainer[IntervalsContainer]
    max_gaps: int
    ordered: bool
    filter: IntervalsFilter
    def __init__(self, intervals: _Optional[_Iterable[_Union[IntervalsContainer, _Mapping]]] = ..., max_gaps: _Optional[int] = ..., ordered: bool = ..., filter: _Optional[_Union[IntervalsFilter, _Mapping]] = ...) -> None: ...

class IntervalsAnyOf(_message.Message):
    __slots__ = ("intervals", "filter")
    INTERVALS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    intervals: _containers.RepeatedCompositeFieldContainer[IntervalsContainer]
    filter: IntervalsFilter
    def __init__(self, intervals: _Optional[_Iterable[_Union[IntervalsContainer, _Mapping]]] = ..., filter: _Optional[_Union[IntervalsFilter, _Mapping]] = ...) -> None: ...

class IntervalsMatch(_message.Message):
    __slots__ = ("analyzer", "max_gaps", "ordered", "query", "use_field", "filter")
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    MAX_GAPS_FIELD_NUMBER: _ClassVar[int]
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    analyzer: str
    max_gaps: int
    ordered: bool
    query: str
    use_field: str
    filter: IntervalsFilter
    def __init__(self, analyzer: _Optional[str] = ..., max_gaps: _Optional[int] = ..., ordered: bool = ..., query: _Optional[str] = ..., use_field: _Optional[str] = ..., filter: _Optional[_Union[IntervalsFilter, _Mapping]] = ...) -> None: ...

class IntervalsQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name", "all_of", "any_of", "fuzzy", "match", "prefix", "wildcard")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ALL_OF_FIELD_NUMBER: _ClassVar[int]
    ANY_OF_FIELD_NUMBER: _ClassVar[int]
    FUZZY_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    all_of: IntervalsAllOf
    any_of: IntervalsAnyOf
    fuzzy: IntervalsFuzzy
    match: IntervalsMatch
    prefix: IntervalsPrefix
    wildcard: IntervalsWildcard
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., all_of: _Optional[_Union[IntervalsAllOf, _Mapping]] = ..., any_of: _Optional[_Union[IntervalsAnyOf, _Mapping]] = ..., fuzzy: _Optional[_Union[IntervalsFuzzy, _Mapping]] = ..., match: _Optional[_Union[IntervalsMatch, _Mapping]] = ..., prefix: _Optional[_Union[IntervalsPrefix, _Mapping]] = ..., wildcard: _Optional[_Union[IntervalsWildcard, _Mapping]] = ...) -> None: ...

class FunctionScoreContainer(_message.Message):
    __slots__ = ("filter", "weight", "exp", "gauss", "linear", "field_value_factor", "random_score", "script_score")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    EXP_FIELD_NUMBER: _ClassVar[int]
    GAUSS_FIELD_NUMBER: _ClassVar[int]
    LINEAR_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALUE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    RANDOM_SCORE_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_SCORE_FIELD_NUMBER: _ClassVar[int]
    filter: QueryContainer
    weight: float
    exp: DecayFunction
    gauss: DecayFunction
    linear: DecayFunction
    field_value_factor: FieldValueFactorScoreFunction
    random_score: RandomScoreFunction
    script_score: ScriptScoreFunction
    def __init__(self, filter: _Optional[_Union[QueryContainer, _Mapping]] = ..., weight: _Optional[float] = ..., exp: _Optional[_Union[DecayFunction, _Mapping]] = ..., gauss: _Optional[_Union[DecayFunction, _Mapping]] = ..., linear: _Optional[_Union[DecayFunction, _Mapping]] = ..., field_value_factor: _Optional[_Union[FieldValueFactorScoreFunction, _Mapping]] = ..., random_score: _Optional[_Union[RandomScoreFunction, _Mapping]] = ..., script_score: _Optional[_Union[ScriptScoreFunction, _Mapping]] = ...) -> None: ...

class DecayFunction(_message.Message):
    __slots__ = ("multi_value_mode", "placement")
    class PlacementEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DecayPlacement
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DecayPlacement, _Mapping]] = ...) -> None: ...
    MULTI_VALUE_MODE_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    multi_value_mode: MultiValueMode
    placement: _containers.MessageMap[str, DecayPlacement]
    def __init__(self, multi_value_mode: _Optional[_Union[MultiValueMode, str]] = ..., placement: _Optional[_Mapping[str, DecayPlacement]] = ...) -> None: ...

class DecayPlacement(_message.Message):
    __slots__ = ("date_decay_placement", "geo_decay_placement", "numeric_decay_placement")
    DATE_DECAY_PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    GEO_DECAY_PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_DECAY_PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    date_decay_placement: DateDecayPlacement
    geo_decay_placement: GeoDecayPlacement
    numeric_decay_placement: NumericDecayPlacement
    def __init__(self, date_decay_placement: _Optional[_Union[DateDecayPlacement, _Mapping]] = ..., geo_decay_placement: _Optional[_Union[GeoDecayPlacement, _Mapping]] = ..., numeric_decay_placement: _Optional[_Union[NumericDecayPlacement, _Mapping]] = ...) -> None: ...

class DateDecayPlacement(_message.Message):
    __slots__ = ("scale", "decay", "offset", "origin")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    DECAY_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    scale: str
    decay: float
    offset: str
    origin: str
    def __init__(self, scale: _Optional[str] = ..., decay: _Optional[float] = ..., offset: _Optional[str] = ..., origin: _Optional[str] = ...) -> None: ...

class GeoDecayPlacement(_message.Message):
    __slots__ = ("scale", "origin", "decay", "offset")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DECAY_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    scale: str
    origin: GeoLocation
    decay: float
    offset: str
    def __init__(self, scale: _Optional[str] = ..., origin: _Optional[_Union[GeoLocation, _Mapping]] = ..., decay: _Optional[float] = ..., offset: _Optional[str] = ...) -> None: ...

class NumericDecayPlacement(_message.Message):
    __slots__ = ("scale", "origin", "decay", "offset")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DECAY_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    scale: float
    origin: float
    decay: float
    offset: float
    def __init__(self, scale: _Optional[float] = ..., origin: _Optional[float] = ..., decay: _Optional[float] = ..., offset: _Optional[float] = ...) -> None: ...

class ScriptScoreFunction(_message.Message):
    __slots__ = ("script",)
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    script: Script
    def __init__(self, script: _Optional[_Union[Script, _Mapping]] = ...) -> None: ...

class IntervalsFilter(_message.Message):
    __slots__ = ("after", "before", "contained_by", "containing", "not_contained_by", "not_containing", "not_overlapping", "overlapping", "script")
    AFTER_FIELD_NUMBER: _ClassVar[int]
    BEFORE_FIELD_NUMBER: _ClassVar[int]
    CONTAINED_BY_FIELD_NUMBER: _ClassVar[int]
    CONTAINING_FIELD_NUMBER: _ClassVar[int]
    NOT_CONTAINED_BY_FIELD_NUMBER: _ClassVar[int]
    NOT_CONTAINING_FIELD_NUMBER: _ClassVar[int]
    NOT_OVERLAPPING_FIELD_NUMBER: _ClassVar[int]
    OVERLAPPING_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    after: IntervalsContainer
    before: IntervalsContainer
    contained_by: IntervalsContainer
    containing: IntervalsContainer
    not_contained_by: IntervalsContainer
    not_containing: IntervalsContainer
    not_overlapping: IntervalsContainer
    overlapping: IntervalsContainer
    script: Script
    def __init__(self, after: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., before: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., contained_by: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., containing: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., not_contained_by: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., not_containing: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., not_overlapping: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., overlapping: _Optional[_Union[IntervalsContainer, _Mapping]] = ..., script: _Optional[_Union[Script, _Mapping]] = ...) -> None: ...

class IntervalsContainer(_message.Message):
    __slots__ = ("all_of", "any_of", "fuzzy", "match", "prefix", "wildcard")
    ALL_OF_FIELD_NUMBER: _ClassVar[int]
    ANY_OF_FIELD_NUMBER: _ClassVar[int]
    FUZZY_FIELD_NUMBER: _ClassVar[int]
    MATCH_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    all_of: IntervalsAllOf
    any_of: IntervalsAnyOf
    fuzzy: IntervalsFuzzy
    match: IntervalsMatch
    prefix: IntervalsPrefix
    wildcard: IntervalsWildcard
    def __init__(self, all_of: _Optional[_Union[IntervalsAllOf, _Mapping]] = ..., any_of: _Optional[_Union[IntervalsAnyOf, _Mapping]] = ..., fuzzy: _Optional[_Union[IntervalsFuzzy, _Mapping]] = ..., match: _Optional[_Union[IntervalsMatch, _Mapping]] = ..., prefix: _Optional[_Union[IntervalsPrefix, _Mapping]] = ..., wildcard: _Optional[_Union[IntervalsWildcard, _Mapping]] = ...) -> None: ...

class PrefixQuery(_message.Message):
    __slots__ = ("field", "value", "boost", "x_name", "rewrite", "case_insensitive")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    REWRITE_FIELD_NUMBER: _ClassVar[int]
    CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
    field: str
    value: str
    boost: float
    x_name: str
    rewrite: MultiTermQueryRewrite
    case_insensitive: bool
    def __init__(self, field: _Optional[str] = ..., value: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., case_insensitive: bool = ...) -> None: ...

class TermsLookupFieldStringArrayMap(_message.Message):
    __slots__ = ("terms_lookup_field", "string_array")
    TERMS_LOOKUP_FIELD_FIELD_NUMBER: _ClassVar[int]
    STRING_ARRAY_FIELD_NUMBER: _ClassVar[int]
    terms_lookup_field: TermsLookupField
    string_array: StringArray
    def __init__(self, terms_lookup_field: _Optional[_Union[TermsLookupField, _Mapping]] = ..., string_array: _Optional[_Union[StringArray, _Mapping]] = ...) -> None: ...

class TermsQueryField(_message.Message):
    __slots__ = ("field_value_array", "lookup")
    FIELD_VALUE_ARRAY_FIELD_NUMBER: _ClassVar[int]
    LOOKUP_FIELD_NUMBER: _ClassVar[int]
    field_value_array: FieldValueArray
    lookup: TermsLookup
    def __init__(self, field_value_array: _Optional[_Union[FieldValueArray, _Mapping]] = ..., lookup: _Optional[_Union[TermsLookup, _Mapping]] = ...) -> None: ...

class TermsLookup(_message.Message):
    __slots__ = ("index", "id", "path", "routing", "store")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    index: str
    id: str
    path: str
    routing: str
    store: bool
    def __init__(self, index: _Optional[str] = ..., id: _Optional[str] = ..., path: _Optional[str] = ..., routing: _Optional[str] = ..., store: bool = ...) -> None: ...

class FieldValueArray(_message.Message):
    __slots__ = ("field_value_array",)
    FIELD_VALUE_ARRAY_FIELD_NUMBER: _ClassVar[int]
    field_value_array: _containers.RepeatedCompositeFieldContainer[FieldValue]
    def __init__(self, field_value_array: _Optional[_Iterable[_Union[FieldValue, _Mapping]]] = ...) -> None: ...

class TermsLookupField(_message.Message):
    __slots__ = ("index", "id", "path", "routing", "store")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ROUTING_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    index: str
    id: str
    path: str
    routing: str
    store: bool
    def __init__(self, index: _Optional[str] = ..., id: _Optional[str] = ..., path: _Optional[str] = ..., routing: _Optional[str] = ..., store: bool = ...) -> None: ...

class TermsSetQuery(_message.Message):
    __slots__ = ("field", "terms", "boost", "x_name", "minimum_should_match_field", "minimum_should_match_script")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    TERMS_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    field: str
    terms: _containers.RepeatedScalarFieldContainer[str]
    boost: float
    x_name: str
    minimum_should_match_field: str
    minimum_should_match_script: Script
    def __init__(self, field: _Optional[str] = ..., terms: _Optional[_Iterable[str]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., minimum_should_match_field: _Optional[str] = ..., minimum_should_match_script: _Optional[_Union[Script, _Mapping]] = ...) -> None: ...

class TermQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name", "value", "case_insensitive")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    value: FieldValue
    case_insensitive: bool
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., value: _Optional[_Union[FieldValue, _Mapping]] = ..., case_insensitive: bool = ...) -> None: ...

class QueryStringQuery(_message.Message):
    __slots__ = ("boost", "x_name", "allow_leading_wildcard", "analyzer", "analyze_wildcard", "auto_generate_synonyms_phrase_query", "default_field", "default_operator", "enable_position_increments", "escape", "fields", "fuzziness", "fuzzy_max_expansions", "fuzzy_prefix_length", "fuzzy_rewrite", "fuzzy_transpositions", "lenient", "max_determinized_states", "minimum_should_match", "phrase_slop", "query", "quote_analyzer", "quote_field_suffix", "rewrite", "tie_breaker", "time_zone", "type")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ALLOW_LEADING_WILDCARD_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_WILDCARD_FIELD_NUMBER: _ClassVar[int]
    AUTO_GENERATE_SYNONYMS_PHRASE_QUERY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_OPERATOR_FIELD_NUMBER: _ClassVar[int]
    ENABLE_POSITION_INCREMENTS_FIELD_NUMBER: _ClassVar[int]
    ESCAPE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    FUZZY_REWRITE_FIELD_NUMBER: _ClassVar[int]
    FUZZY_TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    LENIENT_FIELD_NUMBER: _ClassVar[int]
    MAX_DETERMINIZED_STATES_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    PHRASE_SLOP_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    QUOTE_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    QUOTE_FIELD_SUFFIX_FIELD_NUMBER: _ClassVar[int]
    REWRITE_FIELD_NUMBER: _ClassVar[int]
    TIE_BREAKER_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    allow_leading_wildcard: bool
    analyzer: str
    analyze_wildcard: bool
    auto_generate_synonyms_phrase_query: bool
    default_field: str
    default_operator: Operator
    enable_position_increments: bool
    escape: bool
    fields: _containers.RepeatedScalarFieldContainer[str]
    fuzziness: Fuzziness
    fuzzy_max_expansions: int
    fuzzy_prefix_length: int
    fuzzy_rewrite: MultiTermQueryRewrite
    fuzzy_transpositions: bool
    lenient: bool
    max_determinized_states: int
    minimum_should_match: MinimumShouldMatch
    phrase_slop: int
    query: str
    quote_analyzer: str
    quote_field_suffix: str
    rewrite: MultiTermQueryRewrite
    tie_breaker: float
    time_zone: str
    type: TextQueryType
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., allow_leading_wildcard: bool = ..., analyzer: _Optional[str] = ..., analyze_wildcard: bool = ..., auto_generate_synonyms_phrase_query: bool = ..., default_field: _Optional[str] = ..., default_operator: _Optional[_Union[Operator, str]] = ..., enable_position_increments: bool = ..., escape: bool = ..., fields: _Optional[_Iterable[str]] = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ..., fuzzy_max_expansions: _Optional[int] = ..., fuzzy_prefix_length: _Optional[int] = ..., fuzzy_rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., fuzzy_transpositions: bool = ..., lenient: bool = ..., max_determinized_states: _Optional[int] = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., phrase_slop: _Optional[int] = ..., query: _Optional[str] = ..., quote_analyzer: _Optional[str] = ..., quote_field_suffix: _Optional[str] = ..., rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., tie_breaker: _Optional[float] = ..., time_zone: _Optional[str] = ..., type: _Optional[_Union[TextQueryType, str]] = ...) -> None: ...

class RandomScoreFunction(_message.Message):
    __slots__ = ("field", "seed")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    field: str
    seed: RandomScoreFunctionSeed
    def __init__(self, field: _Optional[str] = ..., seed: _Optional[_Union[RandomScoreFunctionSeed, _Mapping]] = ...) -> None: ...

class RandomScoreFunctionSeed(_message.Message):
    __slots__ = ("int32", "int64", "string")
    INT32_FIELD_NUMBER: _ClassVar[int]
    INT64_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    int32: int
    int64: int
    string: str
    def __init__(self, int32: _Optional[int] = ..., int64: _Optional[int] = ..., string: _Optional[str] = ...) -> None: ...

class RangeQuery(_message.Message):
    __slots__ = ("number_range_query", "date_range_query")
    NUMBER_RANGE_QUERY_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_QUERY_FIELD_NUMBER: _ClassVar[int]
    number_range_query: NumberRangeQuery
    date_range_query: DateRangeQuery
    def __init__(self, number_range_query: _Optional[_Union[NumberRangeQuery, _Mapping]] = ..., date_range_query: _Optional[_Union[DateRangeQuery, _Mapping]] = ...) -> None: ...

class NumberRangeQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name", "relation", "gt", "gte", "lt", "lte", "to", "include_lower", "include_upper")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    GT_FIELD_NUMBER: _ClassVar[int]
    GTE_FIELD_NUMBER: _ClassVar[int]
    LT_FIELD_NUMBER: _ClassVar[int]
    LTE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_LOWER_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_UPPER_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    relation: RangeRelation
    gt: float
    gte: float
    lt: float
    lte: float
    to: NumberRangeQueryAllOfTo
    include_lower: bool
    include_upper: bool
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., relation: _Optional[_Union[RangeRelation, str]] = ..., gt: _Optional[float] = ..., gte: _Optional[float] = ..., lt: _Optional[float] = ..., lte: _Optional[float] = ..., to: _Optional[_Union[NumberRangeQueryAllOfTo, _Mapping]] = ..., include_lower: bool = ..., include_upper: bool = ..., **kwargs) -> None: ...

class NumberRangeQueryAllOfFrom(_message.Message):
    __slots__ = ("double", "string", "null_value")
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    double: float
    string: str
    null_value: NullValue
    def __init__(self, double: _Optional[float] = ..., string: _Optional[str] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class NumberRangeQueryAllOfTo(_message.Message):
    __slots__ = ("double", "string", "null_value")
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    double: float
    string: str
    null_value: NullValue
    def __init__(self, double: _Optional[float] = ..., string: _Optional[str] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class DateRangeQuery(_message.Message):
    __slots__ = ("field", "boost", "x_name", "relation", "gt", "gte", "lt", "lte", "to", "format", "time_zone", "include_lower", "include_upper")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    GT_FIELD_NUMBER: _ClassVar[int]
    GTE_FIELD_NUMBER: _ClassVar[int]
    LT_FIELD_NUMBER: _ClassVar[int]
    LTE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_LOWER_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_UPPER_FIELD_NUMBER: _ClassVar[int]
    field: str
    boost: float
    x_name: str
    relation: RangeRelation
    gt: str
    gte: str
    lt: str
    lte: str
    to: DateRangeQueryAllOfTo
    format: str
    time_zone: str
    include_lower: bool
    include_upper: bool
    def __init__(self, field: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., relation: _Optional[_Union[RangeRelation, str]] = ..., gt: _Optional[str] = ..., gte: _Optional[str] = ..., lt: _Optional[str] = ..., lte: _Optional[str] = ..., to: _Optional[_Union[DateRangeQueryAllOfTo, _Mapping]] = ..., format: _Optional[str] = ..., time_zone: _Optional[str] = ..., include_lower: bool = ..., include_upper: bool = ..., **kwargs) -> None: ...

class DateRangeQueryAllOfFrom(_message.Message):
    __slots__ = ("string", "null_value")
    STRING_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    string: str
    null_value: NullValue
    def __init__(self, string: _Optional[str] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class DateRangeQueryAllOfTo(_message.Message):
    __slots__ = ("string", "null_value")
    STRING_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    string: str
    null_value: NullValue
    def __init__(self, string: _Optional[str] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class RegexpQuery(_message.Message):
    __slots__ = ("field", "value", "boost", "x_name", "case_insensitive", "flags", "max_determinized_states", "rewrite")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    CASE_INSENSITIVE_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    MAX_DETERMINIZED_STATES_FIELD_NUMBER: _ClassVar[int]
    REWRITE_FIELD_NUMBER: _ClassVar[int]
    field: str
    value: str
    boost: float
    x_name: str
    case_insensitive: bool
    flags: str
    max_determinized_states: int
    rewrite: MultiTermQueryRewrite
    def __init__(self, field: _Optional[str] = ..., value: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., case_insensitive: bool = ..., flags: _Optional[str] = ..., max_determinized_states: _Optional[int] = ..., rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ...) -> None: ...

class FuzzyQuery(_message.Message):
    __slots__ = ("field", "value", "boost", "x_name", "max_expansions", "prefix_length", "rewrite", "transpositions", "fuzziness")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    REWRITE_FIELD_NUMBER: _ClassVar[int]
    TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    field: str
    value: FieldValue
    boost: float
    x_name: str
    max_expansions: int
    prefix_length: int
    rewrite: MultiTermQueryRewrite
    transpositions: bool
    fuzziness: Fuzziness
    def __init__(self, field: _Optional[str] = ..., value: _Optional[_Union[FieldValue, _Mapping]] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., max_expansions: _Optional[int] = ..., prefix_length: _Optional[int] = ..., rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., transpositions: bool = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ...) -> None: ...

class Fuzziness(_message.Message):
    __slots__ = ("string", "int32")
    STRING_FIELD_NUMBER: _ClassVar[int]
    INT32_FIELD_NUMBER: _ClassVar[int]
    string: str
    int32: int
    def __init__(self, string: _Optional[str] = ..., int32: _Optional[int] = ...) -> None: ...

class FieldValue(_message.Message):
    __slots__ = ("bool", "general_number", "string", "null_value")
    BOOL_FIELD_NUMBER: _ClassVar[int]
    GENERAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    bool: bool
    general_number: GeneralNumber
    string: str
    null_value: NullValue
    def __init__(self, bool: bool = ..., general_number: _Optional[_Union[GeneralNumber, _Mapping]] = ..., string: _Optional[str] = ..., null_value: _Optional[_Union[NullValue, str]] = ...) -> None: ...

class IdsQuery(_message.Message):
    __slots__ = ("boost", "x_name", "values")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class IntervalsFuzzy(_message.Message):
    __slots__ = ("analyzer", "fuzziness", "prefix_length", "term", "transpositions", "use_field")
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_FIELD_NUMBER: _ClassVar[int]
    analyzer: str
    fuzziness: Fuzziness
    prefix_length: int
    term: str
    transpositions: bool
    use_field: str
    def __init__(self, analyzer: _Optional[str] = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ..., prefix_length: _Optional[int] = ..., term: _Optional[str] = ..., transpositions: bool = ..., use_field: _Optional[str] = ...) -> None: ...

class IntervalsPrefix(_message.Message):
    __slots__ = ("analyzer", "prefix", "use_field")
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_FIELD_NUMBER: _ClassVar[int]
    analyzer: str
    prefix: str
    use_field: str
    def __init__(self, analyzer: _Optional[str] = ..., prefix: _Optional[str] = ..., use_field: _Optional[str] = ...) -> None: ...

class IntervalsWildcard(_message.Message):
    __slots__ = ("analyzer", "pattern", "use_field")
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_FIELD_NUMBER: _ClassVar[int]
    analyzer: str
    pattern: str
    use_field: str
    def __init__(self, analyzer: _Optional[str] = ..., pattern: _Optional[str] = ..., use_field: _Optional[str] = ...) -> None: ...

class MatchAllQuery(_message.Message):
    __slots__ = ("boost", "x_name")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ...) -> None: ...

class MatchBoolPrefixQuery(_message.Message):
    __slots__ = ("field", "query", "boost", "x_name", "analyzer", "fuzziness", "fuzzy_rewrite", "fuzzy_transpositions", "max_expansions", "minimum_should_match", "operator", "prefix_length")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_REWRITE_FIELD_NUMBER: _ClassVar[int]
    FUZZY_TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    field: str
    query: str
    boost: float
    x_name: str
    analyzer: str
    fuzziness: Fuzziness
    fuzzy_rewrite: MultiTermQueryRewrite
    fuzzy_transpositions: bool
    max_expansions: int
    minimum_should_match: MinimumShouldMatch
    operator: Operator
    prefix_length: int
    def __init__(self, field: _Optional[str] = ..., query: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ..., fuzzy_rewrite: _Optional[_Union[MultiTermQueryRewrite, str]] = ..., fuzzy_transpositions: bool = ..., max_expansions: _Optional[int] = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., operator: _Optional[_Union[Operator, str]] = ..., prefix_length: _Optional[int] = ...) -> None: ...

class MatchNoneQuery(_message.Message):
    __slots__ = ("boost", "x_name")
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    boost: float
    x_name: str
    def __init__(self, boost: _Optional[float] = ..., x_name: _Optional[str] = ...) -> None: ...

class MatchPhrasePrefixQuery(_message.Message):
    __slots__ = ("field", "query", "boost", "x_name", "analyzer", "max_expansions", "slop", "zero_terms_query")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    SLOP_FIELD_NUMBER: _ClassVar[int]
    ZERO_TERMS_QUERY_FIELD_NUMBER: _ClassVar[int]
    field: str
    query: str
    boost: float
    x_name: str
    analyzer: str
    max_expansions: int
    slop: int
    zero_terms_query: ZeroTermsQuery
    def __init__(self, field: _Optional[str] = ..., query: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., max_expansions: _Optional[int] = ..., slop: _Optional[int] = ..., zero_terms_query: _Optional[_Union[ZeroTermsQuery, str]] = ...) -> None: ...

class MatchPhraseQuery(_message.Message):
    __slots__ = ("field", "query", "boost", "x_name", "analyzer", "slop", "zero_terms_query")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    SLOP_FIELD_NUMBER: _ClassVar[int]
    ZERO_TERMS_QUERY_FIELD_NUMBER: _ClassVar[int]
    field: str
    query: str
    boost: float
    x_name: str
    analyzer: str
    slop: int
    zero_terms_query: ZeroTermsQuery
    def __init__(self, field: _Optional[str] = ..., query: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., slop: _Optional[int] = ..., zero_terms_query: _Optional[_Union[ZeroTermsQuery, str]] = ...) -> None: ...

class MultiMatchQuery(_message.Message):
    __slots__ = ("query", "boost", "x_name", "analyzer", "auto_generate_synonyms_phrase_query", "fields", "fuzzy_rewrite", "fuzziness", "fuzzy_transpositions", "lenient", "max_expansions", "minimum_should_match", "operator", "prefix_length", "slop", "tie_breaker", "type", "zero_terms_query")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    BOOST_FIELD_NUMBER: _ClassVar[int]
    X_NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_FIELD_NUMBER: _ClassVar[int]
    AUTO_GENERATE_SYNONYMS_PHRASE_QUERY_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_REWRITE_FIELD_NUMBER: _ClassVar[int]
    FUZZINESS_FIELD_NUMBER: _ClassVar[int]
    FUZZY_TRANSPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    LENIENT_FIELD_NUMBER: _ClassVar[int]
    MAX_EXPANSIONS_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SHOULD_MATCH_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SLOP_FIELD_NUMBER: _ClassVar[int]
    TIE_BREAKER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ZERO_TERMS_QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    boost: float
    x_name: str
    analyzer: str
    auto_generate_synonyms_phrase_query: bool
    fields: _containers.RepeatedScalarFieldContainer[str]
    fuzzy_rewrite: str
    fuzziness: Fuzziness
    fuzzy_transpositions: bool
    lenient: bool
    max_expansions: int
    minimum_should_match: MinimumShouldMatch
    operator: Operator
    prefix_length: int
    slop: int
    tie_breaker: float
    type: TextQueryType
    zero_terms_query: ZeroTermsQuery
    def __init__(self, query: _Optional[str] = ..., boost: _Optional[float] = ..., x_name: _Optional[str] = ..., analyzer: _Optional[str] = ..., auto_generate_synonyms_phrase_query: bool = ..., fields: _Optional[_Iterable[str]] = ..., fuzzy_rewrite: _Optional[str] = ..., fuzziness: _Optional[_Union[Fuzziness, _Mapping]] = ..., fuzzy_transpositions: bool = ..., lenient: bool = ..., max_expansions: _Optional[int] = ..., minimum_should_match: _Optional[_Union[MinimumShouldMatch, _Mapping]] = ..., operator: _Optional[_Union[Operator, str]] = ..., prefix_length: _Optional[int] = ..., slop: _Optional[int] = ..., tie_breaker: _Optional[float] = ..., type: _Optional[_Union[TextQueryType, str]] = ..., zero_terms_query: _Optional[_Union[ZeroTermsQuery, str]] = ...) -> None: ...

class FieldValueFactorScoreFunction(_message.Message):
    __slots__ = ("field", "factor", "missing", "modifier")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    MISSING_FIELD_NUMBER: _ClassVar[int]
    MODIFIER_FIELD_NUMBER: _ClassVar[int]
    field: str
    factor: float
    missing: float
    modifier: FieldValueFactorModifier
    def __init__(self, field: _Optional[str] = ..., factor: _Optional[float] = ..., missing: _Optional[float] = ..., modifier: _Optional[_Union[FieldValueFactorModifier, str]] = ...) -> None: ...

class DutchAnalyzer(_message.Message):
    __slots__ = ("type", "stopwords")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    type: DutchAnalyzerType
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[DutchAnalyzerType, str]] = ..., stopwords: _Optional[_Iterable[str]] = ...) -> None: ...

class FingerprintAnalyzer(_message.Message):
    __slots__ = ("type", "version", "max_output_size", "preserve_original", "separator", "stopwords", "stopwords_path")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MAX_OUTPUT_SIZE_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    SEPARATOR_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_PATH_FIELD_NUMBER: _ClassVar[int]
    type: FingerprintAnalyzerType
    version: str
    max_output_size: int
    preserve_original: bool
    separator: str
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    stopwords_path: str
    def __init__(self, type: _Optional[_Union[FingerprintAnalyzerType, str]] = ..., version: _Optional[str] = ..., max_output_size: _Optional[int] = ..., preserve_original: bool = ..., separator: _Optional[str] = ..., stopwords: _Optional[_Iterable[str]] = ..., stopwords_path: _Optional[str] = ...) -> None: ...

class IcuAnalyzer(_message.Message):
    __slots__ = ("type", "method", "mode")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    type: IcuAnalyzerType
    method: IcuNormalizationType
    mode: IcuNormalizationMode
    def __init__(self, type: _Optional[_Union[IcuAnalyzerType, str]] = ..., method: _Optional[_Union[IcuNormalizationType, str]] = ..., mode: _Optional[_Union[IcuNormalizationMode, str]] = ...) -> None: ...

class KeywordAnalyzer(_message.Message):
    __slots__ = ("type", "version")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    type: KeywordAnalyzerType
    version: str
    def __init__(self, type: _Optional[_Union[KeywordAnalyzerType, str]] = ..., version: _Optional[str] = ...) -> None: ...

class LanguageAnalyzer(_message.Message):
    __slots__ = ("type", "version", "language", "stem_exclusion", "stopwords", "stopwords_path")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    STEM_EXCLUSION_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_PATH_FIELD_NUMBER: _ClassVar[int]
    type: LanguageAnalyzerType
    version: str
    language: Language
    stem_exclusion: _containers.RepeatedScalarFieldContainer[str]
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    stopwords_path: str
    def __init__(self, type: _Optional[_Union[LanguageAnalyzerType, str]] = ..., version: _Optional[str] = ..., language: _Optional[_Union[Language, str]] = ..., stem_exclusion: _Optional[_Iterable[str]] = ..., stopwords: _Optional[_Iterable[str]] = ..., stopwords_path: _Optional[str] = ...) -> None: ...

class NoriAnalyzer(_message.Message):
    __slots__ = ("type", "version", "decompound_mode", "stoptags", "user_dictionary")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DECOMPOUND_MODE_FIELD_NUMBER: _ClassVar[int]
    STOPTAGS_FIELD_NUMBER: _ClassVar[int]
    USER_DICTIONARY_FIELD_NUMBER: _ClassVar[int]
    type: NoriAnalyzerType
    version: str
    decompound_mode: NoriDecompoundMode
    stoptags: _containers.RepeatedScalarFieldContainer[str]
    user_dictionary: str
    def __init__(self, type: _Optional[_Union[NoriAnalyzerType, str]] = ..., version: _Optional[str] = ..., decompound_mode: _Optional[_Union[NoriDecompoundMode, str]] = ..., stoptags: _Optional[_Iterable[str]] = ..., user_dictionary: _Optional[str] = ...) -> None: ...

class PatternAnalyzer(_message.Message):
    __slots__ = ("type", "version", "flags", "lowercase", "pattern", "stopwords")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    LOWERCASE_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    type: PatternAnalyzerType
    version: str
    flags: str
    lowercase: bool
    pattern: str
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[PatternAnalyzerType, str]] = ..., version: _Optional[str] = ..., flags: _Optional[str] = ..., lowercase: bool = ..., pattern: _Optional[str] = ..., stopwords: _Optional[_Iterable[str]] = ...) -> None: ...

class SimpleAnalyzer(_message.Message):
    __slots__ = ("type", "version")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNSPECIFIED: _ClassVar[SimpleAnalyzer.Type]
        TYPE_SIMPLE: _ClassVar[SimpleAnalyzer.Type]
    TYPE_UNSPECIFIED: SimpleAnalyzer.Type
    TYPE_SIMPLE: SimpleAnalyzer.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    type: SimpleAnalyzer.Type
    version: str
    def __init__(self, type: _Optional[_Union[SimpleAnalyzer.Type, str]] = ..., version: _Optional[str] = ...) -> None: ...

class StandardAnalyzer(_message.Message):
    __slots__ = ("type", "max_token_length", "stopwords")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKEN_LENGTH_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    type: StandardAnalyzerType
    max_token_length: int
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[StandardAnalyzerType, str]] = ..., max_token_length: _Optional[int] = ..., stopwords: _Optional[_Iterable[str]] = ...) -> None: ...

class StopAnalyzer(_message.Message):
    __slots__ = ("type", "version", "stopwords", "stopwords_path")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_PATH_FIELD_NUMBER: _ClassVar[int]
    type: StopAnalyzerType
    version: str
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    stopwords_path: str
    def __init__(self, type: _Optional[_Union[StopAnalyzerType, str]] = ..., version: _Optional[str] = ..., stopwords: _Optional[_Iterable[str]] = ..., stopwords_path: _Optional[str] = ...) -> None: ...

class WhitespaceAnalyzer(_message.Message):
    __slots__ = ("type", "version")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    type: WhitespaceAnalyzerType
    version: str
    def __init__(self, type: _Optional[_Union[WhitespaceAnalyzerType, str]] = ..., version: _Optional[str] = ...) -> None: ...

class CustomAnalyzer(_message.Message):
    __slots__ = ("type", "char_filter", "filter", "position_increment_gap", "position_offset_gap", "tokenizer")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CHAR_FILTER_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    POSITION_INCREMENT_GAP_FIELD_NUMBER: _ClassVar[int]
    POSITION_OFFSET_GAP_FIELD_NUMBER: _ClassVar[int]
    TOKENIZER_FIELD_NUMBER: _ClassVar[int]
    type: CustomAnalyzerType
    char_filter: _containers.RepeatedScalarFieldContainer[str]
    filter: _containers.RepeatedScalarFieldContainer[str]
    position_increment_gap: int
    position_offset_gap: int
    tokenizer: str
    def __init__(self, type: _Optional[_Union[CustomAnalyzerType, str]] = ..., char_filter: _Optional[_Iterable[str]] = ..., filter: _Optional[_Iterable[str]] = ..., position_increment_gap: _Optional[int] = ..., position_offset_gap: _Optional[int] = ..., tokenizer: _Optional[str] = ...) -> None: ...

class Analyzer(_message.Message):
    __slots__ = ("custom_analyzer", "fingerprint_analyzer", "keyword_analyzer", "language_analyzer", "nori_analyzer", "pattern_analyzer", "simple_analyzer", "standard_analyzer", "stop_analyzer", "whitespace_analyzer", "icu_analyzer", "kuromoji_analyzer", "snowball_analyzer", "dutch_analyzer")
    CUSTOM_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    FINGERPRINT_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    NORI_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    SIMPLE_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    STANDARD_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    STOP_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    WHITESPACE_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    ICU_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    KUROMOJI_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    SNOWBALL_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    DUTCH_ANALYZER_FIELD_NUMBER: _ClassVar[int]
    custom_analyzer: CustomAnalyzer
    fingerprint_analyzer: FingerprintAnalyzer
    keyword_analyzer: KeywordAnalyzer
    language_analyzer: LanguageAnalyzer
    nori_analyzer: NoriAnalyzer
    pattern_analyzer: PatternAnalyzer
    simple_analyzer: SimpleAnalyzer
    standard_analyzer: StandardAnalyzer
    stop_analyzer: StopAnalyzer
    whitespace_analyzer: WhitespaceAnalyzer
    icu_analyzer: IcuAnalyzer
    kuromoji_analyzer: KuromojiAnalyzer
    snowball_analyzer: SnowballAnalyzer
    dutch_analyzer: DutchAnalyzer
    def __init__(self, custom_analyzer: _Optional[_Union[CustomAnalyzer, _Mapping]] = ..., fingerprint_analyzer: _Optional[_Union[FingerprintAnalyzer, _Mapping]] = ..., keyword_analyzer: _Optional[_Union[KeywordAnalyzer, _Mapping]] = ..., language_analyzer: _Optional[_Union[LanguageAnalyzer, _Mapping]] = ..., nori_analyzer: _Optional[_Union[NoriAnalyzer, _Mapping]] = ..., pattern_analyzer: _Optional[_Union[PatternAnalyzer, _Mapping]] = ..., simple_analyzer: _Optional[_Union[SimpleAnalyzer, _Mapping]] = ..., standard_analyzer: _Optional[_Union[StandardAnalyzer, _Mapping]] = ..., stop_analyzer: _Optional[_Union[StopAnalyzer, _Mapping]] = ..., whitespace_analyzer: _Optional[_Union[WhitespaceAnalyzer, _Mapping]] = ..., icu_analyzer: _Optional[_Union[IcuAnalyzer, _Mapping]] = ..., kuromoji_analyzer: _Optional[_Union[KuromojiAnalyzer, _Mapping]] = ..., snowball_analyzer: _Optional[_Union[SnowballAnalyzer, _Mapping]] = ..., dutch_analyzer: _Optional[_Union[DutchAnalyzer, _Mapping]] = ...) -> None: ...

class KuromojiAnalyzer(_message.Message):
    __slots__ = ("type", "mode", "user_dictionary")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    USER_DICTIONARY_FIELD_NUMBER: _ClassVar[int]
    type: KuromojiAnalyzerType
    mode: KuromojiTokenizationMode
    user_dictionary: str
    def __init__(self, type: _Optional[_Union[KuromojiAnalyzerType, str]] = ..., mode: _Optional[_Union[KuromojiTokenizationMode, str]] = ..., user_dictionary: _Optional[str] = ...) -> None: ...

class SnowballAnalyzer(_message.Message):
    __slots__ = ("type", "version", "language", "stopwords")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    STOPWORDS_FIELD_NUMBER: _ClassVar[int]
    type: SnowballAnalyzerType
    version: str
    language: SnowballLanguage
    stopwords: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[SnowballAnalyzerType, str]] = ..., version: _Optional[str] = ..., language: _Optional[_Union[SnowballLanguage, str]] = ..., stopwords: _Optional[_Iterable[str]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("v1",)
    V1_FIELD_NUMBER: _ClassVar[int]
    v1: OpenSearchExceptionV1
    def __init__(self, v1: _Optional[_Union[OpenSearchExceptionV1, _Mapping]] = ...) -> None: ...

class OpenSearchExceptionV1(_message.Message):
    __slots__ = ("type", "reason", "root_cause", "caused_by", "stack_trace", "suppressed", "additional_details")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ROOT_CAUSE_FIELD_NUMBER: _ClassVar[int]
    CAUSED_BY_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    SUPPRESSED_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_DETAILS_FIELD_NUMBER: _ClassVar[int]
    type: str
    reason: str
    root_cause: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    caused_by: _struct_pb2.Struct
    stack_trace: str
    suppressed: _struct_pb2.Struct
    additional_details: _struct_pb2.Struct
    def __init__(self, type: _Optional[str] = ..., reason: _Optional[str] = ..., root_cause: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ..., caused_by: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., stack_trace: _Optional[str] = ..., suppressed: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., additional_details: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class InlineGet(_message.Message):
    __slots__ = ("fields", "found", "x_seq_no", "x_primary_term", "x_routing", "struct_source", "x_source")
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    X_SEQ_NO_FIELD_NUMBER: _ClassVar[int]
    X_PRIMARY_TERM_FIELD_NUMBER: _ClassVar[int]
    X_ROUTING_FIELD_NUMBER: _ClassVar[int]
    STRUCT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    X_SOURCE_FIELD_NUMBER: _ClassVar[int]
    fields: _struct_pb2.Struct
    found: bool
    x_seq_no: int
    x_primary_term: int
    x_routing: _containers.RepeatedScalarFieldContainer[str]
    struct_source: _struct_pb2.Struct
    x_source: bytes
    def __init__(self, fields: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., found: bool = ..., x_seq_no: _Optional[int] = ..., x_primary_term: _Optional[int] = ..., x_routing: _Optional[_Iterable[str]] = ..., struct_source: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., x_source: _Optional[bytes] = ...) -> None: ...
