"""Interpreter package for executing Norvelang AST nodes."""
from .safe_funcs import SAFE_FUNCS
from .expr_eval import eval_expr_node, eval_expr_legacy
from .backend import ListBackend
from .pipeline import execute_pipeline
from .utils import extract_arg_value
