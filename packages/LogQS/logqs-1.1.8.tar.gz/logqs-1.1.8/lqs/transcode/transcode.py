import io
from typing import Union

import orjson as json

from lqs.transcode.utils import get_logger
from lqs.transcode.cdr import CDRWrapper
from lqs.transcode.ark.ark_json_parser import RbufMessageDeserializer
from lqs.transcode.config import TranscodeConfig
from lqs.transcode.cutter import CutterDecoder
from lqs.transcode.ros1.ros_message_deserializer import RosMessageDeserializer


class Transcode:
    def __init__(self, config: Union[TranscodeConfig, dict] = TranscodeConfig()):
        self.config = (
            config if isinstance(config, TranscodeConfig) else TranscodeConfig(**config)
        )
        self.ros_deserializer = RosMessageDeserializer(
            trim_size=self.config.trim_cutoff
        )
        self.rbuf_deserializer = RbufMessageDeserializer(
            trim_size=self.config.trim_cutoff
        )
        self.cdr_wrapper = CDRWrapper()

        self.cutter_decoder = CutterDecoder()
        self.logger = get_logger(
            self.__class__.__name__,
            level=self.config.log_level,
            json_logging=self.config.log_as_json,
        )

    @classmethod
    def supported_encoding(cls):
        return ["ros1", "rbuf", "json", "cdr"]

    def deserialize(
        self,
        type_encoding,
        type_name,
        type_data,
        message_bytes,
        replacements=((b"\\u0000", b"NULL"),),
        add_constants=True,
    ):
        if type_encoding == "ros1":
            message_bytes = io.BytesIO(message_bytes)
            res = self.ros_deserializer.deserialize(
                message_type=type_name,
                message_bytes=message_bytes,
                message_type_data=type_data,
            )
            res_dump = json.dumps(res, default=lambda x: x.to_dict())
            for replacement in replacements:
                res_dump = res_dump.replace(*replacement)
            json_results = json.loads(res_dump)
            if add_constants:
                try:
                    # try to add constants to the json output if available
                    primative_types = [
                        "uint8",
                        "int8",
                        "uint16",
                        "int16",
                        "uint32",
                        "int32",
                        "uint64",
                        "int64",
                        "float32",
                        "float64",
                        "string",
                        "bool",
                    ]
                    for line in type_data.split("\n"):
                        line = line.strip()
                        if line.startswith("#") or line == "":
                            continue
                        if " " not in line:
                            continue
                        if "=" not in line:
                            continue
                        if line.split(" ", 1)[0] not in primative_types:
                            continue
                        const_name = line.split("=", 1)[0].strip().split(" ")[-1]
                        const_value = line.split("=", 1)[1].strip()
                        try:
                            const_value = int(const_value)
                        except ValueError:
                            try:
                                const_value = float(const_value)
                            except ValueError:
                                const_value = const_value.strip('"')
                        if isinstance(json_results, dict):
                            json_results[const_name] = const_value
                except Exception:
                    pass
            return json_results

        if type_encoding == "rbuf":
            message_bytes = io.BytesIO(message_bytes)
            res = self.rbuf_deserializer.deserialize(
                message_bytes=message_bytes,
                message_type=type_name,
                message_type_data=json.loads(type_data),
            )
            res_dump = json.dumps(res, default=lambda x: x.to_dict())
            for replacement in replacements:
                res_dump = res_dump.replace(*replacement)
            return json.loads(res_dump)

        if type_encoding == "json":
            return json.loads(message_bytes)

        if type_encoding == "cdr":
            return self.cdr_wrapper.deserialize(
                type_name=type_name,
                type_data=type_data,
                message_bytes=message_bytes,
            )

        if not type_encoding and type_name and type_name.startswith("lqs_cutter"):
            return self.cutter_decoder.deserialize(
                type_name=type_name, payload=message_bytes
            )

        if not type_encoding and type_name == "logqs.csv":
            column_names = json.loads(type_data)
            column_values = message_bytes.decode("utf-8").split(",")
            message_dict = {}
            for key, value in zip(column_names, column_values):
                if value.isdigit():
                    message_dict[key] = int(value)
                else:
                    try:
                        message_dict[key] = float(value)
                    except ValueError:
                        message_dict[key] = value
            return message_dict

        if type_encoding is None:
            return message_bytes

        raise NotImplementedError(f"Unknown type encoding: {type_encoding}")

    def serialize(self, type_encoding, type_name, type_data, message_dict):
        pass

    def get_schema(self, type_encoding, type_name, type_data) -> dict:
        if type_encoding == "ros1":
            res = self.ros_deserializer.get_json_schema(
                message_type=type_name, message_type_data=type_data
            )
        elif type_encoding == "cdr":
            raise NotImplementedError("CDR schema generation is not implemented")
        elif type_encoding == "rbuf":
            res = self.rbuf_deserializer.get_json_schema(
                message_type=type_name, message_type_data=type_data
            )
        else:
            raise NotImplementedError(f"Unknown type encoding: {type_encoding}")

        return res
