"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fPbContent.proto"\xcf\x04\n\tPbContent\x12\x0c\n\x04type\x18\x01 \x01(\r\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x0c\n\x04link\x18\x03 \x01(\t\x12\x0b\n\x03src\x18\x04 \x01(\t\x12\r\n\x05\x62size\x18\x05 \x01(\t\x12\x0f\n\x07\x63\x64n_src\x18\x08 \x01(\t\x12\x13\n\x0b\x62ig_cdn_src\x18\t \x01(\t\x12\t\n\x01\x63\x18\x0b \x01(\t\x12\x11\n\tvoice_md5\x18\x0c \x01(\t\x12\x13\n\x0b\x64uring_time\x18\r \x01(\r\x12\x0b\n\x03uid\x18\x0f \x01(\x03\x12\r\n\x05width\x18\x12 \x01(\r\x12\x0e\n\x06height\x18\x13 \x01(\r\x12\x12\n\norigin_src\x18\x19 \x01(\t\x12\x13\n\x0borigin_size\x18\x1b \x01(\r\x12\r\n\x05\x63ount\x18\x1c \x01(\x05\x12\x30\n\x0etiebaplus_info\x18( \x01(\x0b\x32\x18.PbContent.TiebaPlusInfo\x12\x1d\n\x04item\x18) \x01(\x0b\x32\x0f.PbContent.Item\x1a\xd2\x01\n\rTiebaPlusInfo\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x65sc\x18\x02 \x01(\t\x12\x10\n\x08jump_url\x18\x03 \x01(\t\x12\x10\n\x08\x61pp_icon\x18\x06 \x01(\t\x12\x13\n\x0btarget_type\x18\x0c \x01(\x05\x12\x14\n\x0ch5_jump_type\x18\r \x01(\x05\x12\x16\n\x0eh5_jump_number\x18\x0e \x01(\t\x12\x15\n\rh5_jump_param\x18\x0f \x01(\t\x12\x11\n\tjump_type\x18\x10 \x01(\x05\x12\x13\n\x0b\x62utton_desc\x18\x17 \x01(\t\x1a\x19\n\x04Item\x12\x11\n\titem_name\x18\x02 \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "PbContent_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_PBCONTENT"]._serialized_start = 20
    _globals["_PBCONTENT"]._serialized_end = 611
    _globals["_PBCONTENT_TIEBAPLUSINFO"]._serialized_start = 374
    _globals["_PBCONTENT_TIEBAPLUSINFO"]._serialized_end = 584
    _globals["_PBCONTENT_ITEM"]._serialized_start = 586
    _globals["_PBCONTENT_ITEM"]._serialized_end = 611
