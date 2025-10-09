"""
Parser module for the Norvelang language.

Provides parsing functionality using Lark parser with optional Cython support.
"""
from pathlib import Path
import lark_cython
from lark import Lark
from .transformer import ASTTransformer

GRAM_PATH = Path(__file__).parent / "grammar.lark"


def parse(text: str, use_cython: bool = False):
    """
    Parse text using the best available parser.

    Args:
        text: The text to parse
        use_cython: If True, force use of lark-cython. If False, use regular lark.
    """
    transformer = ASTTransformer()
    parser = Lark(
        GRAM_PATH.read_text(),
        start="start",
        parser="lalr",
        propagate_positions=True,
        _plugins=lark_cython.plugins if use_cython else {},
    )

    tree = parser.parse(text)
    return transformer.transform(tree)
