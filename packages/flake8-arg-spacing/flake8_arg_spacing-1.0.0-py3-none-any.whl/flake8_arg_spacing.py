
import ast
import importlib.metadata
from itertools import chain


class ArgSpacingChecker:
    name = __name__
    version = importlib.metadata.version(__name__)

    def __init__(self, tree):
        self.tree = tree

    def _should_report(self, arg_node, value_node):
        # Don't report if there's a space after `=`.
        if arg_node.col_offset + len(arg_node.arg) + 1 < value_node.col_offset:
            return False

        # Report only if the given expression contains spaces.
        if isinstance(value_node, ast.UnaryOp):
            return value_node.col_offset + 2 <= value_node.operand.col_offset
        elif isinstance(value_node, ast.BinOp):
            return value_node.left.end_col_offset + 3 <= value_node.right.col_offset
        else:
            # Assume these are always written with spaces.
            return isinstance(value_node, (ast.BoolOp, ast.Compare, ast.IfExp))

    def _get_info(self, node, error_code, label):
        return (
            node.lineno,
            node.col_offset,
            f"ARG{error_code} confusing spacing around {label}",
            type(self),
        )

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.keyword):
                if node.arg is not None and self._should_report(node, node.value):
                    yield self._get_info(node.value, 101, "keyword argument")

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                pos_args = node.args.posonlyargs + node.args.args
                pos_defaults = node.args.defaults
                pos_defaults_index = len(pos_args) - len(pos_defaults)
                kw_args = node.args.kwonlyargs
                kw_defaults = node.args.kw_defaults

                for arg, default in chain(zip(pos_args[pos_defaults_index:], pos_defaults), zip(kw_args, kw_defaults)):
                    if default is not None and self._should_report(arg, default):
                        yield self._get_info(default, 102, "parameter default")
