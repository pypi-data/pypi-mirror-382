"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import CommonReq_pb2 as CommonReq__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14UserPostReqIdl.proto\x1a\x0f\x43ommonReq.proto"\xc7\x01\n\x0eUserPostReqIdl\x12%\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x17.UserPostReqIdl.DataReq\x1a\x8d\x01\n\x07\x44\x61taReq\x12\x0f\n\x07user_id\x18\x01 \x01(\x03\x12\n\n\x02rn\x18\x02 \x01(\r\x12\x11\n\tis_thread\x18\x04 \x01(\r\x12\x14\n\x0cneed_content\x18\x05 \x01(\r\x12\n\n\x02pn\x18\x1a \x01(\r\x12\x14\n\x0cis_view_card\x18! \x01(\x05\x12\x1a\n\x06\x63ommon\x18\x1b \x01(\x0b\x32\n.CommonReqb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "UserPostReqIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_USERPOSTREQIDL"]._serialized_start = 42
    _globals["_USERPOSTREQIDL"]._serialized_end = 241
    _globals["_USERPOSTREQIDL_DATAREQ"]._serialized_start = 100
    _globals["_USERPOSTREQIDL_DATAREQ"]._serialized_end = 241
