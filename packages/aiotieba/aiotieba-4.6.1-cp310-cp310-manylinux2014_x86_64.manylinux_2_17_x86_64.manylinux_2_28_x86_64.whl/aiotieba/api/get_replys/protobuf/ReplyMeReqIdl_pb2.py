"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13ReplyMeReqIdl.proto\x1a\x0f\x43ommonReq.proto"h\n\rReplyMeReqIdl\x12$\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x16.ReplyMeReqIdl.DataReq\x1a\x31\n\x07\x44\x61taReq\x12\n\n\x02pn\x18\x01 \x01(\t\x12\x1a\n\x06\x63ommon\x18\x03 \x01(\x0b\x32\n.CommonReqb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "ReplyMeReqIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_REPLYMEREQIDL"]._serialized_start = 40
    _globals["_REPLYMEREQIDL"]._serialized_end = 144
    _globals["_REPLYMEREQIDL_DATAREQ"]._serialized_start = 95
    _globals["_REPLYMEREQIDL_DATAREQ"]._serialized_end = 144
