"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1aGetForumSquareReqIdl.proto\x1a\x0f\x43ommonReq.proto"\xa7\x01\n\x14GetForumSquareReqIdl\x12+\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x1d.GetForumSquareReqIdl.DataReq\x1a\x62\n\x07\x44\x61taReq\x12\x1a\n\x06\x63ommon\x18\x01 \x01(\x0b\x32\n.CommonReq\x12\x12\n\nclass_name\x18\x02 \x01(\t\x12\n\n\x02pn\x18\x03 \x01(\x05\x12\n\n\x02rn\x18\x04 \x01(\x05\x12\x0f\n\x07user_id\x18\x05 \x01(\x03\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "GetForumSquareReqIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_GETFORUMSQUAREREQIDL"]._serialized_start = 48
    _globals["_GETFORUMSQUAREREQIDL"]._serialized_end = 215
    _globals["_GETFORUMSQUAREREQIDL_DATAREQ"]._serialized_start = 117
    _globals["_GETFORUMSQUAREREQIDL_DATAREQ"]._serialized_end = 215
