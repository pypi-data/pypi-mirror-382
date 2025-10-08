import orjson
import json
from dataclasses import asdict, is_dataclass
from rosbags.typesys import (
    Stores,
    get_types_from_msg,
    get_typestore,
)
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif is_dataclass(obj):
            return asdict(obj)
        return json.JSONEncoder.default(self, obj)


class CDRWrapper:
    def __init__(self):
        self.type_store = get_typestore(Stores.LATEST)

    def deserialize(self, type_name, type_data, message_bytes):
        if type_name not in self.type_store.fielddefs:
            types_dict = get_types_from_msg(text=type_data, name=type_name)
            self.type_store.register(typs=types_dict)

        try:
            res = self.type_store.deserialize_cdr(
                rawdata=message_bytes,
                typename=type_name,
            )
        except KeyError as e:
            # it's possible that the type name isn't formatted as expected
            # count how many '/' is in the type name
            if type_name.count("/") == 1:
                corrected_type_name = type_name.replace("/", "/msg/", 1)
                res = self.type_store.deserialize_cdr(
                    rawdata=message_bytes,
                    typename=corrected_type_name,
                )
            else:
                raise e
        return orjson.loads(orjson.dumps(res, default=NumpyEncoder().default))
