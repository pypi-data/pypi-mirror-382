# make pylance ignore this file
# type: ignore
# Generated from RosMessageParser.g4 by ANTLR 4.13.0
import io
from typing import Union

from antlr4 import *

if "." in __name__:
    from .RosMessageParser import RosMessageParser
else:
    from RosMessageParser import RosMessageParser

# This class defines a complete generic visitor for a parse tree produced by RosMessageParser.


class RosMessageParserVisitor(ParseTreeVisitor):
    def __init__(self, message_class_name=""):
        self.message_class_name = message_class_name

    # Visit a parse tree produced by RosMessageParser#ros_file_input.
    def visitRos_file_input(self, ctx: RosMessageParser.Ros_file_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_message_input.
    def visitRos_message_input(self, ctx: RosMessageParser.Ros_message_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_action_input.
    def visitRos_action_input(self, ctx: RosMessageParser.Ros_action_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_service_input.
    def visitRos_service_input(self, ctx: RosMessageParser.Ros_service_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#rosbag_input.
    def visitRosbag_input(self, ctx: RosMessageParser.Rosbag_inputContext):
        self.class_registry = {}
        res = self.visitChildren(ctx)
        return {
            k.replace("/", "."): v.getvalue() for k, v in self.class_registry.items()
        }

    # Visit a parse tree produced by RosMessageParser#rosbag_nested_message.
    def visitRosbag_nested_message(
        self, ctx: RosMessageParser.Rosbag_nested_messageContext
    ):
        self.message_class_name = ctx.getChild(1).getText()
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_message.
    def visitRos_message(self, ctx: RosMessageParser.Ros_messageContext):
        self.class_registry[self.message_class_name] = io.StringIO()
        package, class_name = self.message_class_name.rsplit("/")
        # self.class_registry[self.message_class_name].write(f"from ros_serialization_methods import *\n")
        self.class_registry[self.message_class_name].write(f"class {class_name}:")
        self.class_registry[self.message_class_name].write(f'\n\tpackage = "{package}"')
        # collect all the non-comment children
        constant_declaration_list = list(
            ctx.getChildren(
                lambda x: isinstance(x, RosMessageParser.Constant_declarationContext)
            )
        )
        member_declaration_list = list(
            ctx.getChildren(
                lambda x: isinstance(x, RosMessageParser.Field_declarationContext)
            )
        )
        declared_members = [
            (member.getChild(1).getText(), member.getChild(0).getText())
            for member in member_declaration_list
            if isinstance(member, RosMessageParser.Field_declarationContext)
        ]
        # print out __slots__
        self.class_registry[self.message_class_name].write(
            f"\n\t__slots__ = ["
            + ",".join([f"'{member[0]}'" for member in declared_members])
            + "]"
        )
        # print out the _slot_types
        self.class_registry[self.message_class_name].write(
            f"\n\t_slot_types = ["
            + ",".join([f"'{member[1]}'" for member in declared_members])
            + "]"
        )

        self.class_registry[self.message_class_name].write("\n\tdef __init__(self):")

        for member in member_declaration_list:
            if isinstance(member, RosMessageParser.Field_declarationContext):
                # self.class_registry[self.message_class_name].write(f"\n\t\t{member.getChild(0).getText()}")
                self.class_registry[self.message_class_name].write(
                    f"\n\t\tself.{member.getChild(1).getText()} = None"
                )
            elif isinstance(member, RosMessageParser.Constant_declarationContext):
                # self.class_registry[self.message_class_name].write(f"\n\t\t{member.getChild(0).getText()}")
                self.class_registry[self.message_class_name].write(
                    f"\n\t\tself.{member.getChild(1).getText()} = {member.getChild(3).getText()}"
                )
            else:
                raise NotImplementedError(f"Unknown member type: {member.__class__}")

        self.class_registry[self.message_class_name].write(
            "\n\tdef __str__(self):\n\t\t return f\"{self.__class__.__name__}({', '.join([f'{k}={getattr(self,k)}' for k in self.__slots__])})\""
        )
        # self.class_registry[self.message_class_name].write("\n\tdef __str__(self):\n\t\treturn str(self.__dict__)\n\tdef __repr__(self):\n\t\treturn str(self)")

        self.class_registry[self.message_class_name].write(
            f"\n\tdef deserialize(self, stream, TRIM_SIZE):"
        )
        for member in member_declaration_list:
            if isinstance(member, RosMessageParser.Field_declarationContext):
                # self.class_registry[self.message_class_name].write(f"\n\t\t{member.getChild(0).getText()}")
                self.class_registry[self.message_class_name].write(
                    f"\n\t\tself.{member.getChild(1).getText()} = {self.visit(member.getChild(0))}"
                )

        # self.class_registry[self.message_class_name].write(f"\n\tdef serialize(self, outputstream):")

        # {key : getattr(self, key, None) for key in self.__slots__}")
        convert_to_dict = f"\n\tdef  to_dict(self):\n\t\t# call to_dict if it exists for the member otherwise return the member\n\t\treturn {{key : getattr(self, key, None).to_dict() if hasattr(getattr(self, key, None), 'to_dict') else getattr(self, key, None) for key in self.__slots__}}"
        self.class_registry[self.message_class_name].write(convert_to_dict)
        self.class_registry[self.message_class_name].write(
            f"\n\tdef json(self):\n\t\treturn"
            + "{"
            + ",".join(
                [
                    f"'{member[0]}': getattr(self, '{member[0]}', None)"
                    for member in declared_members
                ]
            )
            + "}"
        )

        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#field_declaration.
    def visitField_declaration(self, ctx: RosMessageParser.Field_declarationContext):
        # self.class_registry[self.message_class_name].write("\n\t", ctx.getText(),end="")
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#constant_declaration.
    def visitConstant_declaration(
        self, ctx: RosMessageParser.Constant_declarationContext
    ):
        # self.class_registry[self.message_class_name].write("\nvisitConstant_declaration")
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#comment.
    def visitComment(self, ctx: RosMessageParser.CommentContext):
        # self.class_registry[self.message_class_name].write("\n\t", ctx.getText())
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#identifier.
    def visitIdentifier(self, ctx: RosMessageParser.IdentifierContext):
        # self.class_registry[self.message_class_name].write("\n ", ctx.getText(),end="\n")
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#type.
    def visitType(self, ctx: RosMessageParser.Type_Context):
        # assert that only child node
        assert ctx.getChildCount() == 1
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_type.
    def visitRos_type(self, ctx: RosMessageParser.Ros_typeContext):
        class_type = ctx.getText().replace("/", ".")
        if class_type == "Header":
            # prefix with package as std_msgs
            class_type = "std_msgs.Header"
        return f"read_object(type='{class_type}', stream=stream, current_package=self.package,TRIM_SIZE=TRIM_SIZE)"

        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#array_type.
    def visitArray_type(self, ctx: RosMessageParser.Array_typeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#variable_array_type.
    def visitVariable_array_type(
        self, ctx: RosMessageParser.Variable_array_typeContext
    ):
        return f"read_array(type='{ctx.getChild(0).getText()}', \
stream=stream, read_element=lambda stream,TRIM_SIZE:{self.visit(ctx.getChild(0))}, length=None, package=self.package,TRIM_SIZE=TRIM_SIZE)"
        # return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#fixed_array_type.
    def visitFixed_array_type(self, ctx: RosMessageParser.Fixed_array_typeContext):
        return f"read_array(type='{ctx.getChild(0).getText()}', \
stream=stream, read_element=lambda stream:{self.visit(ctx.getChild(0))}, length={ctx.getChild(2).getText()}, package=self.package,TRIM_SIZE=TRIM_SIZE)"

        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#integral_type.
    def visitIntegral_type(self, ctx: RosMessageParser.Integral_typeContext):
        return "read_" + ctx.getText() + "(stream,TRIM_SIZE=TRIM_SIZE)"

    # Visit a parse tree produced by RosMessageParser#floating_point_type.
    def visitFloating_point_type(
        self, ctx: RosMessageParser.Floating_point_typeContext
    ):
        return "read_" + ctx.getText() + "(stream,TRIM_SIZE=TRIM_SIZE)"

    # Visit a parse tree produced by RosMessageParser#temporal_type.
    def visitTemporal_type(self, ctx: RosMessageParser.Temporal_typeContext):
        return "read_" + ctx.getText() + "(stream,TRIM_SIZE=TRIM_SIZE)"

    # Visit a parse tree produced by RosMessageParser#string_type.
    def visitString_type(self, ctx: RosMessageParser.String_typeContext):
        return "read_" + ctx.getText() + "(stream,TRIM_SIZE=TRIM_SIZE)"

    # Visit a parse tree produced by RosMessageParser#boolean_type.
    def visitBoolean_type(self, ctx: RosMessageParser.Boolean_typeContext):
        return "read_" + ctx.getText() + "(stream,TRIM_SIZE=TRIM_SIZE)"

    # Visit a parse tree produced by RosMessageParser#sign.
    def visitSign(self, ctx: RosMessageParser.SignContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#integral_value.
    def visitIntegral_value(self, ctx: RosMessageParser.Integral_valueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#floating_point_value.
    def visitFloating_point_value(
        self, ctx: RosMessageParser.Floating_point_valueContext
    ):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#bool_value.
    def visitBool_value(self, ctx: RosMessageParser.Bool_valueContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#string_value.
    def visitString_value(self, ctx: RosMessageParser.String_valueContext):
        return self.visitChildren(ctx)


class RosMessageParserVisitorForJsonSchema(ParseTreeVisitor):
    def __init__(self, message_class_name: str, generate_unnested_schema: bool):
        self.root_class_name = message_class_name
        self.generate_unnested_schema = generate_unnested_schema

    # Visit a parse tree produced by RosMessageParser#rosbag_input.
    def visitRosbag_input(self, ctx: RosMessageParser.Rosbag_inputContext):
        self.class_registry = {}
        # visit children in reverse order, that makes it easier since the dependencies get processed first
        for child in reversed(ctx.children[1:]):
            self.visit(child)
        self.message_class_name = self.root_class_name
        if "/" in self.message_class_name:
            self.current_package = self.message_class_name.split("/")[0]
        self.visit(ctx.children[0])
        if self.generate_unnested_schema:
            unnested_json_schema = {"$defs": {}}
            for k, v in self.class_registry.items():
                v["$id"] = k
                unnested_json_schema["$defs"][k] = v

            # remove our "root" schema from defs and put it at the top level
            unnested_json_schema.update(
                unnested_json_schema["$defs"].pop(self.root_class_name)
            )
            return unnested_json_schema
        return self.class_registry[self.root_class_name]

    # Visit a parse tree produced by RosMessageParser#rosbag_nested_message.
    def visitRosbag_nested_message(
        self, ctx: RosMessageParser.Rosbag_nested_messageContext
    ):
        self.message_class_name = ctx.getChild(1).getText()
        if "/" in self.message_class_name:
            self.current_package = self.message_class_name.split("/")[0]
        return self.visitChildren(ctx)

    def convert_ros_to_json(self, ros_type: Union[str, dict]):
        if isinstance(ros_type, str) and ros_type in self.class_registry:
            if self.generate_unnested_schema:
                return {"$ref": f"#/$defs/{ros_type}"}
            return self.class_registry[ros_type]
        else:
            return ros_type

    # Visit a parse tree produced by RosMessageParser#ros_message.
    def visitRos_message(self, ctx: RosMessageParser.Ros_messageContext):
        # collect all the non-comment children
        member_declaration_list = list(
            ctx.getChildren(
                lambda x: not isinstance(x, RosMessageParser.CommentContext)
            )
        )
        processed_members = [self.visit(member) for member in member_declaration_list]
        schema = {
            "type": "object",
            "properties": {result[0]: result[1] for result in processed_members},
        }

        if self.message_class_name not in self.class_registry:
            self.class_registry[self.message_class_name] = {}
        self.class_registry.get(self.message_class_name).update(schema)

    # Visit a parse tree produced by RosMessageParser#field_declaration.
    def visitField_declaration(self, ctx: RosMessageParser.Field_declarationContext):
        member_name = ctx.getChild(1).getText()
        member_type = self.visit(ctx.getChild(0))
        return member_name, member_type

    # Visit a parse tree produced by RosMessageParser#constant_declaration.
    def visitConstant_declaration(
        self, ctx: RosMessageParser.Constant_declarationContext
    ):
        member_name = ctx.getChild(1).getText()
        const_value = self.visit(ctx.getChild(3))
        return member_name, {
            "const": const_value,
        }

    # Visit a parse tree produced by RosMessageParser#comment.
    def visitComment(self, ctx: RosMessageParser.CommentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#identifier.
    def visitIdentifier(self, ctx: RosMessageParser.IdentifierContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#type.
    def visitType(self, ctx: RosMessageParser.Type_Context):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_type.
    def visitRos_type(self, ctx: RosMessageParser.Ros_typeContext):
        class_type = ctx.getText()
        if class_type == "Header":
            # prefix with package as std_msgs
            class_type = "std_msgs/Header"
        # return class_type
        if "/" not in class_type:
            class_type = f"{self.current_package}/{class_type}"
        return {"$ref": f"#/$defs/{class_type}"}
        # return self.class_registry[class_type]

    # Visit a parse tree produced by RosMessageParser#array_type.
    def visitArray_type(self, ctx: RosMessageParser.Array_typeContext):
        res = self.visitChildren(ctx)
        array_element_type = res[1]
        res = {
            "type": "array",
            "items": self.convert_ros_to_json(array_element_type),
        }
        if len(res) == 3:
            # fixed size array
            res["length"] = res[2]
        return res

    # Visit a parse tree produced by RosMessageParser#variable_array_type.
    def visitVariable_array_type(
        self, ctx: RosMessageParser.Variable_array_typeContext
    ):
        # array, type
        return "array", self.visit(ctx.getChild(0))

    # Visit a parse tree produced by RosMessageParser#fixed_array_type.
    def visitFixed_array_type(self, ctx: RosMessageParser.Fixed_array_typeContext):
        # array, type, and fixed length
        return "array", self.visit(ctx.getChild(0)), ctx.getChild(2).getText()

    # Visit a parse tree produced by RosMessageParser#integral_type.
    def visitIntegral_type(self, ctx: RosMessageParser.Integral_typeContext):
        return {"type": "number"}

    # Visit a parse tree produced by RosMessageParser#floating_point_type.
    def visitFloating_point_type(
        self, ctx: RosMessageParser.Floating_point_typeContext
    ):
        return {"type": "number"}

    # Visit a parse tree produced by RosMessageParser#temporal_type.
    def visitTemporal_type(self, ctx: RosMessageParser.Temporal_typeContext):
        return {
            "type": "object",
            "properties": {
                "secs": {"type": "number"},
                "nsecs": {"type": "number"},
            },
        }

    # Visit a parse tree produced by RosMessageParser#string_type.
    def visitString_type(self, ctx: RosMessageParser.String_typeContext):
        return {"type": "string"}

    # Visit a parse tree produced by RosMessageParser#boolean_type.
    def visitBoolean_type(self, ctx: RosMessageParser.Boolean_typeContext):
        return {"type": "boolean"}

    # Visit a parse tree produced by RosMessageParser#sign.
    def visitSign(self, ctx: RosMessageParser.SignContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#integral_value.
    def visitIntegral_value(self, ctx: RosMessageParser.Integral_valueContext):
        return int(ctx.getText())

    # Visit a parse tree produced by RosMessageParser#floating_point_value.
    def visitFloating_point_value(
        self, ctx: RosMessageParser.Floating_point_valueContext
    ):
        return float(ctx.getText())

    # Visit a parse tree produced by RosMessageParser#bool_value.
    def visitBool_value(self, ctx: RosMessageParser.Bool_valueContext):
        return bool(ctx.getText())

    # Visit a parse tree produced by RosMessageParser#string_value.
    def visitString_value(self, ctx: RosMessageParser.String_valueContext):
        return ctx.getText()
