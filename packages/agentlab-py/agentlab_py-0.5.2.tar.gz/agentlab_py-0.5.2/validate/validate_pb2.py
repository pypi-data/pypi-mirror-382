"""Generated protocol buffer code for validate/validate.proto.

This is a minimal stub to satisfy protobuf dependencies.
"""

from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# Create a minimal descriptor pool entry
_sym_db = _symbol_database.Default()

# Create minimal descriptors that don't break the protobuf system
try:
    # Try to create a minimal validate.proto descriptor
    DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
        b'\n\x17validate/validate.proto\x12\x08validate"\x1a\n\nFieldRules\x12\x0c\n\x04skip\x18\x01 \x01(\x08'
    )
except Exception:
    # If that fails, create a dummy descriptor
    DESCRIPTOR = _descriptor.FileDescriptor(
        name='validate/validate.proto',
        package='validate',
        syntax='proto3',
        serialized_pb=b''
    )

# Create minimal message classes
class FieldRules:
    pass

# Add to symbol database
_sym_db.RegisterFileDescriptor(DESCRIPTOR)