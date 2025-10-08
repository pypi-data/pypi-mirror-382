from lqs.transcode.ros1.RosMessageParser import RosMessageParser


from antlr4 import ParseTreeVisitor
import hashlib


def compute_md5(msg_text: str):
    md5 = hashlib.md5()
    md5.update(msg_text.encode("utf-8"))
    return md5.hexdigest()


def compute_md5_from_dict(schema: dict):
    # it has constants and properties
    msg_text = "\n".join([*schema["constants"], *schema["properties"]]).strip()
    return compute_md5(msg_text)


class RosMessageParserVisitorForMD5(ParseTreeVisitor):
    def __init__(self, message_class_name: str):
        self.root_class_name = message_class_name
        self.md5_registry = {}

    # Visit a parse tree produced by RosMessageParser#rosbag_input.
    def visitRosbag_input(self, ctx: RosMessageParser.Rosbag_inputContext):
        # visit children in reverse order, that makes it easier since the dependencies get processed first
        for child in reversed(ctx.children[1:]):
            self.visit(tree=child)
        self.message_class_name = self.root_class_name
        if "/" in self.message_class_name:
            self.current_package = self.message_class_name.split("/")[0]
        self.visit(ctx.children[0])
        return self.md5_registry[self.root_class_name]

    # Visit a parse tree produced by RosMessageParser#rosbag_nested_message.
    def visitRosbag_nested_message(
        self, ctx: RosMessageParser.Rosbag_nested_messageContext
    ):
        self.message_class_name = ctx.getChild(1).getText()
        if "/" in self.message_class_name:
            self.current_package = self.message_class_name.split("/")[0]
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#ros_message.
    def visitRos_message(self, ctx: RosMessageParser.Ros_messageContext):
        # collect all the non-comment children
        member_declaration_list = list(
            ctx.getChildren(
                lambda x: not isinstance(x, RosMessageParser.CommentContext)
            )
        )
        # split into constants and members
        constant_declaration_list = [
            member
            for member in member_declaration_list
            if isinstance(member, RosMessageParser.Constant_declarationContext)
        ]
        member_declaration_list = [
            member
            for member in member_declaration_list
            if isinstance(member, RosMessageParser.Field_declarationContext)
        ]

        schema = {
            "type": "object",
            "constants": [self.visit(member) for member in constant_declaration_list],
            "properties": [self.visit(member) for member in member_declaration_list],
        }
        self.md5_registry[self.message_class_name] = compute_md5_from_dict(schema)

    # Visit a parse tree produced by RosMessageParser#field_declaration.
    def visitField_declaration(self, ctx: RosMessageParser.Field_declarationContext):
        member_name = ctx.getChild(1).getText()
        member_type = self.visit(ctx.getChild(0))
        return f"{member_type} {member_name}"

    # Visit a parse tree produced by RosMessageParser#constant_declaration.
    def visitConstant_declaration(
        self, ctx: RosMessageParser.Constant_declarationContext
    ):
        type = ctx.getChild(0).getText()
        member_name = ctx.getChild(1).getText()
        const_value = self.visit(ctx.getChild(3))
        return f"{type} {member_name}={const_value}"

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
        if "/" not in class_type:
            class_type = f"{self.current_package}/{class_type}"
        if class_type not in self.md5_registry:
            return ""
        return self.md5_registry[class_type]

    # Visit a parse tree produced by RosMessageParser#array_type.
    def visitArray_type(self, ctx: RosMessageParser.Array_typeContext):
        # TODO handle this with the broken logic that ROS uses for custom classes
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#variable_array_type.
    def visitVariable_array_type(
        self, ctx: RosMessageParser.Variable_array_typeContext
    ):
        base_type = ctx.getChild(0).getChild(0)
        if isinstance(base_type, RosMessageParser.Ros_typeContext):
            # the broken logic is only for Complex Types
            return self.visit(base_type)
        else:
            return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#fixed_array_type.
    def visitFixed_array_type(self, ctx: RosMessageParser.Fixed_array_typeContext):
        # array, type, and fixed length
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#integral_type.
    def visitIntegral_type(self, ctx: RosMessageParser.Integral_typeContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#floating_point_type.
    def visitFloating_point_type(
        self, ctx: RosMessageParser.Floating_point_typeContext
    ):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#temporal_type.
    def visitTemporal_type(self, ctx: RosMessageParser.Temporal_typeContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#string_type.
    def visitString_type(self, ctx: RosMessageParser.String_typeContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#boolean_type.
    def visitBoolean_type(self, ctx: RosMessageParser.Boolean_typeContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#sign.
    def visitSign(self, ctx: RosMessageParser.SignContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by RosMessageParser#integral_value.
    def visitIntegral_value(self, ctx: RosMessageParser.Integral_valueContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#floating_point_value.
    def visitFloating_point_value(
        self, ctx: RosMessageParser.Floating_point_valueContext
    ):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#bool_value.
    def visitBool_value(self, ctx: RosMessageParser.Bool_valueContext):
        return ctx.getText()

    # Visit a parse tree produced by RosMessageParser#string_value.
    def visitString_value(self, ctx: RosMessageParser.String_valueContext):
        return ctx.getText()
