"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import FrsTabInfo_pb2 as FrsTabInfo__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bSearchPostForumResIdl.proto\x1a\x0b\x45rror.proto\x1a\x10\x46rsTabInfo.proto"\xfd\x01\n\x15SearchPostForumResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12,\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x1e.SearchPostForumResIdl.DataRes\x1a\x9e\x01\n\x07\x44\x61taRes\x12?\n\x0b\x65xact_match\x18\x01 \x01(\x0b\x32*.SearchPostForumResIdl.DataRes.SearchForum\x1aR\n\x0bSearchForum\x12\x10\n\x08\x66orum_id\x18\x01 \x01(\x03\x12\x12\n\nforum_name\x18\x02 \x01(\t\x12\x1d\n\x08tab_info\x18\t \x03(\x0b\x32\x0b.FrsTabInfob\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "SearchPostForumResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_SEARCHPOSTFORUMRESIDL"]._serialized_start = 63
    _globals["_SEARCHPOSTFORUMRESIDL"]._serialized_end = 316
    _globals["_SEARCHPOSTFORUMRESIDL_DATARES"]._serialized_start = 158
    _globals["_SEARCHPOSTFORUMRESIDL_DATARES"]._serialized_end = 316
    _globals["_SEARCHPOSTFORUMRESIDL_DATARES_SEARCHFORUM"]._serialized_start = 234
    _globals["_SEARCHPOSTFORUMRESIDL_DATARES_SEARCHFORUM"]._serialized_end = 316
