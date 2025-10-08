import sys
import types
from typing import Any, List, Tuple

from lqs.transcode.ark.ark_deserialization_methods import *  # noqa  # used by the generated code we execute dynamically
from collections import defaultdict

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
    "duration",
    "steady_time_point",
    "system_time_point",
}
primitive_types = {
    *numerical_types,
    "bool",
    "guid",
    "string",
}


def handle_initialization(
    ark_json_schema, field, current_package
) -> Tuple[List[str], Any]:
    if "attributes" in field:
        if (
            "constant" in field["attributes"]
            and field["attributes"]["constant"] is True
        ):
            return [], field["constant_value"]
        if "removed" in field["attributes"] and field["attributes"]["removed"] is True:
            return [], None
        if (
            "optional" in field["attributes"]
            and field["attributes"]["optional"] is True
        ):
            return [], "None"
    if field["type"] in primitive_types:
        if field["type"] in numerical_types:
            return [], "0"
        elif field["type"] == "bool":
            return [], "False"
        elif field["type"] == "guid":
            return [], '"00000000-0000-0000-0000-000000000000"'
        elif field["type"] == "string":
            return [], '""'
    if (
        field["type"] == "byte_buffer"
        or field["type"] == "arraylist"
        or field["type"] == "fixed_size_array"
    ):
        return [], "[]"
    if field["type"] == "dictionary":
        return [], "{}"
    if field["type"] == "enum":
        object_namespace: str
        name: str
        object_namespace, name = field["object_type"].rsplit("::", 1)
        enum = next(
            enum
            for enum in ark_json_schema["enums"]
            if enum["name"] == name and enum["object_namespace"] == object_namespace
        )
        # if its a bitmask enum just return 0
        if enum["enum_type"] == "bitmask":
            value = 0
        # check if 0 or -1 value exists, otherwise just return the first value
        elif 0 in enum["values"].values():
            value = 0
        elif -1 in enum["values"].values():
            value = -1
        else:
            value = next(value for value in enum["values"].values())

        if current_package == object_namespace:
            return [], f"{name}({value})"
        else:
            return [object_namespace], f"{object_namespace}.{name}({value})"

    if field["type"] == "object":
        object_namespace: str
        name: str
        object_namespace, name = field["object_type"].rsplit("::", 1)
        if object_namespace == current_package:
            return [], f"{name}()"
        else:
            return [object_namespace], f'{object_namespace.replace("::",".")}.{name}()'
    if field["type"] == "variant":
        imports = []
        init = None
        for index, variant_type in field["variant_types"]:
            object_namespace, name = variant_type.rsplit("::", 1)

            if object_namespace == current_package and init is None:
                init = f"{name}()"
            else:
                imports.append(object_namespace)
                if init is None:
                    init = f'{object_namespace.replace("::",".")}.{name}()'
        return imports, init

    return [], str(field["type"])


def generate_read_enum(ark_json_schema, enum, current_package):
    object_namespace, name = enum["object_type"].rsplit("::", 1)
    enum = next(
        enum
        for enum in ark_json_schema["enums"]
        if enum["name"] == name and enum["object_namespace"] == object_namespace
    )
    enum_class = enum["enum_class"]
    if object_namespace == current_package:
        return f"lambda *args, **kwargs: {name}(value=read_{enum_class}(kwargs['stream'], TRIM_SIZE=kwargs['TRIM_SIZE']))"
    else:
        # TODO add an import for this object_namespace here
        object_namespace = object_namespace.replace("::", ".")
        return f"lambda *args, **kwargs: {object_namespace}.{name}(value=read_{enum_class}(kwargs['stream'], TRIM_SIZE=kwargs['TRIM_SIZE']))"


def get_read_statement(ark_json_schema, field, current_package):
    read_fn = get_read_fn(ark_json_schema, field, current_package)
    return f"({read_fn})(stream=stream, TRIM_SIZE=TRIM_SIZE)"


def get_read_fn(ark_json_schema, field, current_package):
    if field["type"] in primitive_types:
        if field["type"] in numerical_types:
            return f"read_{field['type']}"
        elif field["type"] == "bool":
            return "read_bool"
        elif field["type"] == "guid":
            return "read_guid"
        elif field["type"] == "string":
            return "read_string"
    if field["type"] == "byte_buffer":
        return "read_byte_buffer"
    if field["type"] == "arraylist":
        # TODO optimize for primitive types
        read_element_fn = get_read_fn(
            ark_json_schema=ark_json_schema,
            field=field["ctr_value_type"],
            current_package=current_package,
        )
        return f"lambda *args, **kwargs: read_array(type='{field['ctr_value_type']['type']}', read_element={read_element_fn}, stream=kwargs['stream'], TRIM_SIZE=kwargs['TRIM_SIZE'])"
    if field["type"] == "array":
        read_element_fn = get_read_fn(
            ark_json_schema=ark_json_schema,
            field=field["ctr_value_type"],
            current_package=current_package,
        )
        return f"lambda *args, **kwargs: read_array(type='{field['ctr_value_type']['type']}', read_element={read_element_fn}, length={field['array_size']}, stream=kwargs['stream'], TRIM_SIZE=kwargs['TRIM_SIZE'])"
    if field["type"] == "dictionary":
        read_key_fn = get_read_fn(
            ark_json_schema=ark_json_schema,
            field=field["ctr_key_type"],
            current_package=current_package,
        )
        read_value_fn = get_read_fn(
            ark_json_schema=ark_json_schema,
            field=field["ctr_value_type"],
            current_package=current_package,
        )
        assert read_key_fn
        assert read_value_fn
        return f"lambda *args, **kwargs: read_dictionary(read_key={read_key_fn}, read_value={read_value_fn}, stream=kwargs['stream'], TRIM_SIZE=kwargs['TRIM_SIZE'])"
    if field["type"] == "enum":
        return generate_read_enum(
            ark_json_schema=ark_json_schema, enum=field, current_package=current_package
        )
    if field["type"] == "object":
        object_namespace, name = field["object_type"].rsplit("::", 1)
        if object_namespace == current_package:
            return f"{name}().deserialize"
        else:
            object_namespace = object_namespace.replace("::", ".")
            return f"{object_namespace}.{name}().deserialize"
    if field["type"] in {"steady_time_point", "duration", "system_time_point"}:
        return f"read_{field['type']}"

    if field["type"] == "variant":
        index: int
        variant_type: str
        types_dict = {}
        types_dict_str = "{"
        for index, variant_type in field["variant_types"]:
            object_namespace, name = variant_type.rsplit("::", 1)
            if object_namespace == current_package:
                object_name = f"{name}"
            else:
                object_namespace = object_namespace.replace("::", ".")
                object_name = f"{object_namespace}.{name}"
            types_dict[index] = object_name
            types_dict_str += f"{index}: {object_name}, "
        types_dict_str += "}"
        read_fn = f"lambda *args, **kwargs: read_variant(stream=kwargs['stream'], types={types_dict_str}, TRIM_SIZE=kwargs['TRIM_SIZE'])"
        return read_fn
    raise Exception("Not implemented yet", field)


import keyword


def handle_arbitrary_name(value):
    """
    If the passed string is a python  keyword, "escape"  it by adding  `_lqs_` prefix
    """
    if keyword.iskeyword(value):
        return "_lqs_" + value
    return value


def convert_enum(enum_schema):
    enum_class = enum_schema["enum_class"]
    assert enum_class in {
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
    }, f"enum_class has to be one of 'int8' / 'int16' / 'int32' / 'int64' / 'uint8' / 'uint16' / 'uint32' / 'uint64' but was {enum_class}"
    name, object_namespace = (
        handle_arbitrary_name(enum_schema["name"]),
        enum_schema["object_namespace"],
    )
    enum_type = enum_schema["enum_type"]
    if enum_type == "bitmask":
        enum_class_def = (
            f"""from enum import IntFlag\nclass {enum_schema['name']}(IntFlag):"""
        )
        for enum_value_name, enum_value in enum_schema["values"].items():
            enum_class_def += (
                f"""\n\t{handle_arbitrary_name(enum_value_name)} = {enum_value}"""
            )
    elif enum_type == "value":
        enum_class_def = (
            f"""from enum import IntEnum\nclass {enum_schema['name']}(IntEnum):"""
        )
        for enum_value_name, enum_value in enum_schema["values"].items():
            enum_class_def += (
                f"""\n\t{handle_arbitrary_name(enum_value_name)} = {enum_value}"""
            )
    else:
        raise Exception("Not implemented yet", enum_type)
    return object_namespace, name, enum_class_def


def converter(ark_json_schema, type_identifier, recursive_call=False):
    deserializer_registry = defaultdict(dict)
    imports = set()
    # we start with the schem in schemas where name, object_namespace matched the type_identifier
    object_namespace, name = type_identifier.rsplit("::", 1)
    schema = next(
        schema
        for schema in ark_json_schema["schemas"]
        if schema["name"] == name and schema["object_namespace"] == object_namespace
    )
    assert schema is not None, (
        "Schema not found for type identifier: " + type_identifier
    )
    is_final = (
        "attributes" in schema
        and "final" in schema["attributes"]
        and schema["attributes"]["final"] is True
    )
    name = schema["name"]
    assert not keyword.iskeyword(
        name
    ), f"Cannot have a reserved keyword as the schema name: {name}"
    class_def = f"""class {name}:\n\tdef __init__(self):\n"""
    for field in schema["fields"]:
        field["name"] = handle_arbitrary_name(field["name"])
        new_import, field_initialization = handle_initialization(
            ark_json_schema=ark_json_schema,
            field=field,
            current_package=object_namespace,
        )
        if new_import:
            imports.update(new_import)
        if field_initialization is not None:
            class_def += f"\t\tself.{field['name']} = {field_initialization}\n"
    if not schema["fields"]:
        class_def += f"\t\tpass\n"
    for group in schema["groups"]:
        for field in group["fields"]:
            field["name"] = handle_arbitrary_name(field["name"])
            new_import, field_initialization = handle_initialization(
                ark_json_schema=ark_json_schema,
                field=field,
                current_package=object_namespace,
            )
            if field_initialization is not None:
                class_def += f"\t\tself.{field['name']} = {field_initialization}\n"
            if new_import:
                imports.update(new_import)
    # deserialization method
    class_def += """\tdef deserialize(self, stream, TRIM_SIZE):\n"""

    if not is_final:
        class_def += "\t\thas_more_sections = read_bitstream_header(stream, TRIM_SIZE=TRIM_SIZE)\n"
    for field in schema["fields"]:
        # skip constant fields
        if (
            "attributes" in field
            and "constant" in field["attributes"]
            and field["attributes"]["constant"] is True
        ):
            continue
        # for removed fields we just read the value and discard it
        if (
            "attributes" in field
            and "removed" in field["attributes"]
            and field["attributes"]["removed"] is True
        ):
            read_statement = get_read_statement(
                ark_json_schema=ark_json_schema,
                field=field,
                current_package=object_namespace,
            )
            class_def += f"\t\t{read_statement}\n"
            continue
        # for optional fields we read a bool and if its true we read the value
        if (
            "attributes" in field
            and "optional" in field["attributes"]
            and field["attributes"]["optional"] is True
        ):
            class_def += f"\t\tif read_bool(stream, TRIM_SIZE=TRIM_SIZE):\n"
            field_type = field["type"]
            if field_type == "object":
                read_statement = get_read_statement(
                    ark_json_schema=ark_json_schema,
                    field=field,
                    current_package=object_namespace,
                )
                class_def += f"\t\t\tself.{field['name']} = {read_statement}\n"
            else:
                class_def += f"\t\t\tself.{field['name']} = read_{field_type}(stream, TRIM_SIZE=TRIM_SIZE)\n"
            continue

        read_statement = get_read_statement(
            ark_json_schema=ark_json_schema,
            field=field,
            current_package=object_namespace,
        )
        class_def += f"\t\tself.{field['name']} = {read_statement}\n"
    if not is_final:
        class_def += "\t\twhile has_more_sections:\n"
        class_def += "\t\t\thas_more_sections, (group_number, group_data_length) = read_optional_group_header(stream, TRIM_SIZE=TRIM_SIZE)\n"
        for group in schema["groups"]:
            class_def += f"\t\t\tif group_number == {group['identifier']}:\n"
            for field in group["fields"]:
                # skip constant fields
                if (
                    "attributes" in field
                    and "constant" in field["attributes"]
                    and field["attributes"]["constant"] is True
                ):
                    continue
                # for removed fields we just read the value and discard it
                read_statement = get_read_statement(
                    ark_json_schema=ark_json_schema,
                    field=field,
                    current_package=object_namespace,
                )
                if (
                    "attributes" in field
                    and "removed" in field["attributes"]
                    and field["attributes"]["removed"] is True
                ):
                    class_def += f"\t\t\t\t{read_statement}\n"
                    continue
                # for optional fields we read a bool and if its true we read the value
                if (
                    "attributes" in field
                    and "optional" in field["attributes"]
                    and field["attributes"]["optional"] is True
                ):
                    class_def += f"\t\t\t\tif read_bool(stream, TRIM_SIZE=TRIM_SIZE):\n\t\t\t\t\tself.{field['name']} = {read_statement}\n"
                    continue

                class_def += f"\t\t\t\tself.{field['name']} = {read_statement}\n"
            class_def += "\t\t\t\tcontinue\n"
        class_def += "\n\t\t\tconsume(stream, group_data_length)\n"
    class_def += "\t\treturn self\n"
    class_def += """\n\tdef __str__(self):\n\t\treturn str(self.__dict__)\n\tdef __repr__(self):\n\t\treturn str(self)"""
    class_def += "\n\tdef  to_dict(self):\n\t\t# call to_dict if it exists for the member otherwise return the member\n\t\treturn {key : getattr(self, key, None).to_dict() if hasattr(getattr(self, key, None), 'to_dict') else getattr(self, key, None) for key in self.__dict__}"
    # convert other classes
    if not recursive_call:
        for schema in ark_json_schema["schemas"]:
            if (
                schema["name"] == name
                and schema["object_namespace"] == object_namespace
            ):
                continue
            _package, _name, converted_class_def = converter(
                ark_json_schema=ark_json_schema,
                type_identifier=f"{schema['object_namespace']}::{schema['name']}",
                recursive_call=True,
            )
            deserializer_registry[_package.replace("::", ".")][
                _name
            ] = converted_class_def
        for enum_schema in ark_json_schema["enums"]:
            _package, _name, converted_enum_def = convert_enum(enum_schema=enum_schema)
            deserializer_registry[_package.replace("::", ".")][
                _name
            ] = converted_enum_def
        import_statements = ""
        for _import in imports:
            _import_modified = _import.replace("::", ".")
            import_statements += f"import {_import_modified}\n"

        deserializer_registry[object_namespace.replace("::", ".")][name] = (
            import_statements + class_def
        )
        return deserializer_registry

    else:
        import_statements = ""
        for _import in imports:
            _import_modified = _import.replace("::", ".")
            import_statements += f"import {_import_modified}\n"
        return object_namespace, name, import_statements + class_def


def sys_module_registration(package, class_name, class_obj):
    if package not in sys.modules:
        sub_module_obj = types.ModuleType(
            package, "This is a fake module for " + package
        )
        if "." in package:
            parent_package, sub_package = package.rsplit(".", 1)
            sub_module_obj.__package__ = parent_package
            sys_module_registration(parent_package, sub_package, sub_module_obj)
        sys.modules[package] = sub_module_obj

    else:
        sub_module_obj = sys.modules[package]

    sub_module_obj.__dict__.update(
        {
            class_name: class_obj,
        }
    )
    return sys.modules[package]


class RbufJsonSchemaGenerator:
    def __init__(self, rbuf_schema_registry, generate_unnested_schema):
        self.json_schema_registry = {}
        self.rbuf_schema_registry = rbuf_schema_registry
        self.generate_unnested_schema = generate_unnested_schema
        self.dependencies = set()

    def handle_enum_type(self, canonical_enum_name):
        enum_package, enum_name = canonical_enum_name.rsplit("::", 1)
        # get the enum schema from the registry
        enum_schema = next(
            enum_schema
            for enum_schema in self.rbuf_schema_registry["enums"]
            if enum_schema["name"] == enum_name
            and enum_schema["object_namespace"] == enum_package
        )
        return {
            "description": f"ark enum of type: {enum_schema['enum_type']}",
            "oneOf": [
                {"const": enum_value, "description": enum_name}
                for enum_name, enum_value in enum_schema["values"].items()
            ],
        }

    def parse_constant_value(self, constant_type, constant_value_string):
        if constant_type in numerical_types:
            if constant_type in {"float", "double"}:
                return float(constant_value_string)
            return int(constant_value_string)
        elif constant_type == "bool":
            return constant_value_string == "true"
        elif constant_type == "guid":
            return constant_value_string
        elif constant_type == "string":
            return constant_value_string[1:-1]  # this is to remove the escaped quotes
        elif constant_type == "enum":
            return constant_value_string
        elif constant_type in {"steady_time_point", "duration", "system_time_point"}:
            return int(constant_value_string)
        else:
            raise Exception("Not implemented yet", constant_type)

    def get_json_type(self, rbuf_type, field):
        # if the field is a constant just return the constant value
        if field.get("attributes", {}).get("constant", False):
            return {
                "const": self.parse_constant_value(
                    field["type"], field["constant_value"]
                )
            }
        elif rbuf_type in numerical_types:
            return {"type": "number"}
        elif rbuf_type == "bool":
            return {"type": "boolean"}
        elif rbuf_type == "guid":
            return {"type": "string"}
        elif rbuf_type == "string":
            return {"type": "string"}
        elif rbuf_type == "byte_buffer":
            return {"type": "array", "items": {"type": "number"}}
        elif rbuf_type == "arraylist" or rbuf_type == "array":
            res = {
                "type": "array",
                "items": self.get_json_type(
                    rbuf_type=field["ctr_value_type"]["type"],
                    field=field["ctr_value_type"],
                ),
            }
            if rbuf_type == "array":
                res["minItems"] = field["array_size"]
                res["maxItems"] = field["array_size"]
            return res
        elif rbuf_type == "dictionary":
            return {"type": "object"}
        elif rbuf_type == "enum":
            return self.handle_enum_type(field["object_type"])
        elif rbuf_type == "object":
            object_type = field["object_type"]
            if object_type not in self.json_schema_registry:
                self.get_json_schema_for_rbuf(object_type)
            # add this to dependencies
            self.dependencies.add(object_type)
            return {"$ref": f"#/$defs/{object_type}"}
            # return self.json_schema_registry[field["object_type"]]
        elif rbuf_type in {"steady_time_point", "duration", "system_time_point"}:
            return {"type": "number"}
        elif rbuf_type == "variant":
            return {
                "$comment": "ark variant type",
                "anyOf": [
                    {
                        "$comment": str(variant_type_id),
                        **self.get_json_type(
                            "object", {"object_type": variant_type_class}
                        ),
                    }
                    for variant_type_id, variant_type_class in field["variant_types"]
                ],
            }

        raise Exception("Not implemented yet", rbuf_type)

    def get_json_schema_for_rbuf(self, message_type, include_dependencies=False):
        if message_type in self.json_schema_registry:
            return self.json_schema_registry[message_type]
        # fetch the schema for the message_type
        object_namespace, name = message_type.rsplit("::", 1)
        schema = next(
            schema
            for schema in self.rbuf_schema_registry["schemas"]
            if schema["name"] == name and schema["object_namespace"] == object_namespace
        )
        json_schema = {
            "$id": message_type,
            "type": "object",
            "properties": {},
        }

        for field in schema["fields"]:
            json_schema["properties"][field["name"]] = self.get_json_type(
                field["type"], field
            )

        for group in schema["groups"]:
            for field in group["fields"]:
                json_schema["properties"][field["name"]] = self.get_json_type(
                    field["type"], field
                )

        self.json_schema_registry[message_type] = json_schema

        if self.generate_unnested_schema and include_dependencies:
            json_schema["$defs"] = {
                dependency: self.json_schema_registry[dependency]
                for dependency in self.dependencies
            }

        return json_schema


class RbufMessageDeserializer:
    def __init__(self, trim_size=None, generate_unnested_schema=True):
        self._class_registry = {}
        self._trim_size = trim_size
        self.generate_unnested_schema = generate_unnested_schema

    def _register(self, type_name, type_schema: dict):
        deserializer_registry = converter(
            ark_json_schema=type_schema, type_identifier=type_name
        )
        for package in deserializer_registry:
            for class_name, python_class_defintion in deserializer_registry[
                package
            ].items():
                try:
                    exec(
                        python_class_defintion + f"\n{class_name} = {class_name}",
                        globals(),
                        globals(),
                    )
                    sys_module_registration(package, class_name, globals()[class_name])
                except Exception as e:
                    raise Exception(
                        e,
                        f"package: {package}, name: {class_name}, def: {python_class_defintion}",
                    )

    def deserialize(self, message_bytes, message_type, message_type_data=None):
        main_package, main_class_name = message_type.rsplit("::", 1)
        if message_type not in self._class_registry:
            if message_type_data is None:
                raise Exception(
                    "message_type_data is required for the first time deserialization"
                )
            self._register(message_type, message_type_data)
        main_package, main_class_attr = message_type.split("::", 1)
        package = __import__(main_package)
        for attr in main_class_attr.split("::"):
            package = getattr(package, attr)
        main_cls = package
        res = main_cls()
        res.deserialize(message_bytes, TRIM_SIZE=self._trim_size)
        return res

    def get_json_schema(self, message_type, message_type_data) -> dict:
        rbuf_json_schema_generator = RbufJsonSchemaGenerator(
            rbuf_schema_registry=message_type_data,
            generate_unnested_schema=self.generate_unnested_schema,
        )
        return rbuf_json_schema_generator.get_json_schema_for_rbuf(
            message_type, include_dependencies=True
        )
