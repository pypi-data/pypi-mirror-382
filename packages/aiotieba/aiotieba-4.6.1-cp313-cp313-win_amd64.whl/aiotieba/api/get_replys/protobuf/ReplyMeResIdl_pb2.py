"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()


from ..._protobuf import Error_pb2 as Error__pb2
from ..._protobuf import Page_pb2 as Page__pb2
from ..._protobuf import User_pb2 as User__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13ReplyMeResIdl.proto\x1a\x0b\x45rror.proto\x1a\nPage.proto\x1a\nUser.proto"\x95\x03\n\rReplyMeResIdl\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12$\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x16.ReplyMeResIdl.DataRes\x1a\xc6\x02\n\x07\x44\x61taRes\x12\x13\n\x04page\x18\x01 \x01(\x0b\x32\x05.Page\x12\x34\n\nreply_list\x18\x02 \x03(\x0b\x32 .ReplyMeResIdl.DataRes.ReplyList\x1a\xef\x01\n\tReplyList\x12\x11\n\tthread_id\x18\x01 \x01(\x04\x12\x0f\n\x07post_id\x18\x02 \x01(\x04\x12\x0c\n\x04time\x18\x03 \x01(\r\x12\r\n\x05\x66name\x18\x05 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x06 \x01(\t\x12\x10\n\x08is_floor\x18\x07 \x01(\r\x12\x15\n\rquote_content\x18\x08 \x01(\t\x12\x16\n\x07replyer\x18\t \x01(\x0b\x32\x05.User\x12\x11\n\tquote_pid\x18\x0e \x01(\x04\x12\x19\n\nquote_user\x18\x0f \x01(\x0b\x32\x05.User\x12!\n\x12thread_author_user\x18\x19 \x01(\x0b\x32\x05.Userb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "ReplyMeResIdl_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_REPLYMERESIDL"]._serialized_start = 61
    _globals["_REPLYMERESIDL"]._serialized_end = 466
    _globals["_REPLYMERESIDL_DATARES"]._serialized_start = 140
    _globals["_REPLYMERESIDL_DATARES"]._serialized_end = 466
    _globals["_REPLYMERESIDL_DATARES_REPLYLIST"]._serialized_start = 227
    _globals["_REPLYMERESIDL_DATARES_REPLYLIST"]._serialized_end = 466
