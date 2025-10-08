# read functions for primitive types
import struct
from typing import Dict

from lqs.transcode.errors import DeserializationError

numerical_types = {
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "float",
    "double",
}
fixed_length_type = {
    *numerical_types,
    "bool",
    "guid",
    "duration",
    "steady_time_point",
    "system_time_point",
    "enum",
}

# The magic bits to indicate the byte is a header.
BITSTREAM_HEADER_MAGIC = 0xD0

# THe magic bits to indicate the byte is a group.
BITSTREAM_GROUP_MAGIC = 0xE0

# Indicates that this header/group has at least one following section
# that needs to be read.
BITSTREAM_HAS_FOLLOWING_SECTION = 0x04


def read_int8(stream, TRIM_SIZE):
    return struct.unpack("<b", stream.read(1))[0]


def read_uint8(stream, TRIM_SIZE):
    return struct.unpack("<B", stream.read(1))[0]


def read_int16(stream, TRIM_SIZE):
    return struct.unpack("<h", stream.read(2))[0]


def read_uint16(stream, TRIM_SIZE):
    return struct.unpack("<H", stream.read(2))[0]


def read_int32(stream, TRIM_SIZE):
    return struct.unpack("<i", stream.read(4))[0]


def read_uint32(stream, TRIM_SIZE):
    return struct.unpack("<I", stream.read(4))[0]


def read_int64(stream, TRIM_SIZE):
    return struct.unpack("<q", stream.read(8))[0]


def read_uint64(stream, TRIM_SIZE):
    return struct.unpack("<Q", stream.read(8))[0]


def read_float(stream, TRIM_SIZE):
    return struct.unpack("<f", stream.read(4))[0]


def read_double(stream, TRIM_SIZE):
    return struct.unpack("<d", stream.read(8))[0]


def read_string(stream, TRIM_SIZE):
    length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)
    if TRIM_SIZE is not None and length > TRIM_SIZE:
        stream.read(length)
        return None

    return stream.read(length).decode("utf-8")


def read_time(stream, TRIM_SIZE):
    return read_uint64(stream, TRIM_SIZE=TRIM_SIZE)


def read_steady_time_point(stream, TRIM_SIZE):
    return read_time(stream, TRIM_SIZE=TRIM_SIZE)


def read_system_time_point(stream, TRIM_SIZE):
    return read_time(stream, TRIM_SIZE=TRIM_SIZE)


def read_duration(stream, TRIM_SIZE):
    return read_uint64(stream, TRIM_SIZE=TRIM_SIZE)


def read_bool(stream, TRIM_SIZE):
    return read_uint8(stream, TRIM_SIZE=TRIM_SIZE) != 0


def read_guid(stream, TRIM_SIZE):
    # TODO revisit this later
    """
    Reads a GUID from the bitstream, which is essentially a 16-byte array that we
    return into a string for Python consumption.
    """

    # Read the raw 16 bytes in.
    raw_bytes = stream.read(16)

    # Convert the array into a hex guid, the hard way. Note that in Ark
    # the first 8 bytes are behind the second 8 bytes, and 'backwards', as
    # it tries to match little endian notation for two 8 byte integers for
    # some reason. We should move this into a class.
    output = ""

    index = 7
    while index >= 0:
        if index == 1 or index == 3:
            output += "-"

        output += "{:02x}".format(raw_bytes[index])
        index -= 1

    index = 15
    while index >= 8:
        if index == 15 or index == 13:
            output += "-"

        output += "{:02x}".format(raw_bytes[index])
        index -= 1

    return output


def read_byte_buffer(stream, TRIM_SIZE):
    length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)

    result = stream.read(length)
    if TRIM_SIZE is not None and length > TRIM_SIZE:
        return None
    # convert byte buffer to list to make it json compatible (for db insert)
    return list(result)


def read_array(type, stream, read_element, TRIM_SIZE, length=None):
    if length is None:
        length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)

    if type in fixed_length_type:
        # TODO can optimize this
        pass
    result = [read_element(stream, TRIM_SIZE=TRIM_SIZE) for _ in range(length)]
    if TRIM_SIZE is not None and length > TRIM_SIZE:
        return None
    return result


def read_dictionary(stream, read_key, read_value, TRIM_SIZE, length=None):
    if length is None:
        length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)
    return {
        str(read_key(stream, TRIM_SIZE=TRIM_SIZE)): read_value(stream, TRIM_SIZE=TRIM_SIZE)
        for _ in range(length)
    }


def consume(stream, length):
    # TODO maybe just seek instead depending on the stream
    stream.read(length)


def read_variant(stream, types: Dict, TRIM_SIZE):
    index = read_uint8(stream, TRIM_SIZE=TRIM_SIZE)
    length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)

    if index not in types:
        # consume the bytes
        consume(stream, length)
        return None

    return types[index]().deserialize(stream, TRIM_SIZE=TRIM_SIZE)


def read_bitstream_header(stream, TRIM_SIZE):
    """
    Reads the bitstream header from the stream. These headers
    denote the start of a new serialized structure, and help
    indicate version information or if different sections are
    present.
    """

    header = read_uint8(stream, TRIM_SIZE=TRIM_SIZE)

    # Ensure the header magic bits are set.
    if (header & 0xF0) != BITSTREAM_HEADER_MAGIC:
        raise DeserializationError(
            "Tried to read a bitstream header, but the header had the incorrect magic numbers. "
            "This indicates the stream is corrupt, or is not a rbuf stream."
        )

    # We can only decode version one with this code.
    if (header & 0x03) != 0x01:
        raise DeserializationError(
            "Tried to read a bitstream header, but it had an unexpected version number. This "
            "software only supports version 1."
        )

    # Store off if we have more sections...
    has_more_sections = (header & BITSTREAM_HAS_FOLLOWING_SECTION) > 0

    # If the last bit is set, then we have some kind of unexpected
    # bitstream error.
    if (header & 0x08) != 0x00:
        raise DeserializationError(
            "Tried to read a bitstream header, but this header indicates the stream has groups, "
            "which this software does not support."
        )
    return has_more_sections


def read_optional_group_header(stream, TRIM_SIZE):
    """
    Reads a group header from the bitstream, updating if we have additional sections or not,
    and returning a tuple containing the parsed identifier and group size. Throws if the next
    byte does not appear to be a group header.
    """

    header = struct.Struct("<BBL").unpack(stream.read(6))

    # Throw if this isn't a group
    if (header[0] & 0xF0) != BITSTREAM_GROUP_MAGIC:
        raise DeserializationError(
            "Tried to read a bitstream group header, but the header had an incorrect magic "
            "number. This indicates the stream is corrupt, or is not an rbuf stream."
        )

    # Record if we have additional sections
    has_more_sections = (header[0] & BITSTREAM_HAS_FOLLOWING_SECTION) > 0

    # Throw if we have any other fields set, something is wrong and we're an incorrect
    # version or were wrong that it was a group.
    if (header[0] & 0x0B) != 0x00:
        raise DeserializationError(
            "Tried to read a bitstream group header, but the header had additional flags specified that were unknown."
        )

    # Return the group identifier and size as a tuple
    return has_more_sections, header[1:]


def split_type_mapping_info_fn(stream, TRIM_SIZE):
    read_bitstream_header(stream, None)
    return {
        "object_identifier": read_guid(stream, None),
        "short_identifier": read_uint8(stream, None),
    }


def split_file_header_fn(stream):
    read_bitstream_header(stream, None)
    return {
        "format_version": read_uint16(stream, None),
        "split_identifier": read_guid(stream, None),
        "index_offset": read_uint32(stream, None),
        "indexed_item_count": read_uint32(stream, None),
        "maximum_item_count": read_uint32(stream, None),
        "type_mappings": read_array(
            type=None,
            stream=stream,
            read_element=lambda stream, TRIM_SIZE: split_type_mapping_info_fn(
                stream, None
            ),
            TRIM_SIZE=None,
        ),
    }
