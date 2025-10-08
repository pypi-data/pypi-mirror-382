import struct


SIMPLE_TYPES_DICT = {  # see python module struct
    "int8": "b",
    "uint8": "B",
    # Python 2.6 adds in '?' for C99 _Bool, which appears equivalent to an uint8,
    # thus, we use uint8
    "bool": "B",
    "int16": "h",
    "uint16": "H",
    "int32": "i",
    "uint32": "I",
    "int64": "q",
    "uint64": "Q",
    "float32": "f",
    "float64": "d",
    # deprecated
    "char": "B",  # unsigned
    "byte": "b",  # signed
}


def read_uint8(stream, TRIM_SIZE):
    return struct.unpack("<B", stream.read(1))[0]


def read_uint16(stream, TRIM_SIZE):
    return struct.unpack("<H", stream.read(2))[0]


def read_uint32(stream, TRIM_SIZE):
    return struct.unpack("<I", stream.read(4))[0]


def read_uint64(stream, TRIM_SIZE):
    return struct.unpack("<Q", stream.read(8))[0]


def read_int8(stream, TRIM_SIZE):
    return struct.unpack("<b", stream.read(1))[0]


def read_int16(stream, TRIM_SIZE):
    return struct.unpack("<h", stream.read(2))[0]


def read_int32(stream, TRIM_SIZE):
    return struct.unpack("<i", stream.read(4))[0]


def read_int64(stream, TRIM_SIZE):
    return struct.unpack("<q", stream.read(8))[0]


def read_float32(stream, TRIM_SIZE):
    return struct.unpack("<f", stream.read(4))[0]


def read_float64(stream, TRIM_SIZE):
    return struct.unpack("<d", stream.read(8))[0]


def read_byte(stream, TRIM_SIZE):
    return read_int8(stream, TRIM_SIZE=TRIM_SIZE)


def read_string(stream, TRIM_SIZE):
    length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)
    if TRIM_SIZE is not None and length > TRIM_SIZE:
        stream.read(length)
        return None
    return stream.read(length).decode("utf-8")


def read_time(stream, TRIM_SIZE):
    return {
        "secs": read_uint32(stream, TRIM_SIZE=TRIM_SIZE),
        "nsecs": read_uint32(stream, TRIM_SIZE=TRIM_SIZE),
    }


def read_duration(stream, TRIM_SIZE):
    return read_time(stream, TRIM_SIZE=TRIM_SIZE)


def read_bool(stream, TRIM_SIZE):
    return read_uint8(stream, TRIM_SIZE=TRIM_SIZE) != 0


def read_char(stream, TRIM_SIZE):
    return read_uint8(stream, TRIM_SIZE=TRIM_SIZE)


def read_array(type, stream, read_element, length, package, TRIM_SIZE):
    if length is None:
        length = read_uint32(stream, TRIM_SIZE=TRIM_SIZE)

    if type in SIMPLE_TYPES_DICT:
        element_size = struct.calcsize(SIMPLE_TYPES_DICT[type])
        array_total_size = element_size * length
        array_bytes = stream.read(array_total_size)
        if TRIM_SIZE is not None and length > TRIM_SIZE:
            return None
        return list(
            struct.unpack(
                f"<{length}{SIMPLE_TYPES_DICT[type]}",
                array_bytes,
            )
        )
    if TRIM_SIZE is not None and length > TRIM_SIZE:
        for i in range(length, TRIM_SIZE):
            read_element(stream, TRIM_SIZE=TRIM_SIZE)
        return None
    return [read_element(stream, TRIM_SIZE=TRIM_SIZE) for i in range(length)]


def read_object(type, stream, current_package, TRIM_SIZE):
    # try to import the type and if that fails try to modify the package and try again
    if "." in type:
        package, class_name = type.rsplit(".")
    else:
        class_name = type
        package = current_package
    module = __import__(package)

    cls = getattr(module, class_name)()
    cls.deserialize(stream, TRIM_SIZE=TRIM_SIZE)
    return cls
