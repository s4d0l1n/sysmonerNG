# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: logservice.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'logservice.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10logservice.proto\x12\x07logbook\"K\n\x13LogDateRangeRequest\x12\x10\n\x08log_name\x18\x01 \x01(\t\x12\x11\n\tfrom_date\x18\x02 \x01(\t\x12\x0f\n\x07to_date\x18\x03 \x01(\t\"%\n\x0eLogListRequest\x12\x13\n\x0blogged_host\x18\x01 \x01(\t\"\x14\n\x12LogHostListRequest\"\x83\x01\n\x08LogEntry\x12\x12\n\nlog_source\x18\x01 \x01(\t\x12\x10\n\x08\x65vent_id\x18\x02 \x01(\x05\x12\x14\n\x0ctime_created\x18\x03 \x01(\t\x12\x11\n\trecord_id\x18\x04 \x01(\x05\x12\x14\n\x0cmachine_name\x18\x05 \x01(\t\x12\x12\n\nevent_data\x18\x06 \x01(\t\"8\n\x12LogEntriesResponse\x12\"\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x11.logbook.LogEntry\"\"\n\x0fLogListResponse\x12\x0f\n\x07\x65ntries\x18\x01 \x03(\t\"&\n\x13LogHostListResponse\x12\x0f\n\x07\x65ntries\x18\x01 \x03(\t2c\n\x0eLogbookService\x12Q\n\x12GetLogsByDateRange\x12\x1c.logbook.LogDateRangeRequest\x1a\x1b.logbook.LogEntriesResponse0\x01\x32\xa4\x01\n\x0eLogListService\x12\x45\n\x10GetLogListByHost\x12\x17.logbook.LogListRequest\x1a\x18.logbook.LogListResponse\x12K\n\x0eGetLogHostList\x12\x1b.logbook.LogHostListRequest\x1a\x1c.logbook.LogHostListResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'logservice_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_LOGDATERANGEREQUEST']._serialized_start=29
  _globals['_LOGDATERANGEREQUEST']._serialized_end=104
  _globals['_LOGLISTREQUEST']._serialized_start=106
  _globals['_LOGLISTREQUEST']._serialized_end=143
  _globals['_LOGHOSTLISTREQUEST']._serialized_start=145
  _globals['_LOGHOSTLISTREQUEST']._serialized_end=165
  _globals['_LOGENTRY']._serialized_start=168
  _globals['_LOGENTRY']._serialized_end=299
  _globals['_LOGENTRIESRESPONSE']._serialized_start=301
  _globals['_LOGENTRIESRESPONSE']._serialized_end=357
  _globals['_LOGLISTRESPONSE']._serialized_start=359
  _globals['_LOGLISTRESPONSE']._serialized_end=393
  _globals['_LOGHOSTLISTRESPONSE']._serialized_start=395
  _globals['_LOGHOSTLISTRESPONSE']._serialized_end=433
  _globals['_LOGBOOKSERVICE']._serialized_start=435
  _globals['_LOGBOOKSERVICE']._serialized_end=534
  _globals['_LOGLISTSERVICE']._serialized_start=537
  _globals['_LOGLISTSERVICE']._serialized_end=701
# @@protoc_insertion_point(module_scope)
