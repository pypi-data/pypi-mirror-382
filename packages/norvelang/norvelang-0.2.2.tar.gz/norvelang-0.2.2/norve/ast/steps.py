"""AST nodes for pipeline steps in Norvelang."""
from dataclasses import dataclass
from typing import List, Dict, Optional, TYPE_CHECKING
from .expr import Expr
from .agg import AggFunc

if TYPE_CHECKING:
    from .pipeline import Pipeline

__all__ = [
    "Step",
    "Order",
    "Limit",
    "Join",
    "Use",
    "From",
    "Where",
    "Map",
    "Group",
    "Save",
    "Let",
    "Name",
    "Having",
    "Title",
]


@dataclass
class Step:
    """Base class for all pipeline steps."""


@dataclass
class Title(Step):
    """Pipeline title step."""
    text: str


@dataclass
class Order(Step):
    """Sort rows by specified columns and directions."""
    orderings: list


@dataclass
class Limit(Step):
    """Limit result to n rows."""
    n: int


@dataclass
class Join(Step):
    """Join with another data source."""
    join_type: str
    source: str
    alias: Optional[str]
    left_key: str
    right_key: str
    extra: Optional[Dict[str, str]] = None


@dataclass
class Use(Step):
    """Display specified columns."""
    columns: Optional[List[tuple]] = None


@dataclass
class From(Step):
    """Specify data source with optional alias."""
    source: str
    alias: Optional[str] = None
    extra: Optional[Dict[str, str]] = None


@dataclass
class Where(Step):
    """Filter rows based on condition."""
    condition: Expr


@dataclass
class Map(Step):
    """Transform columns using expressions."""
    mappings: Dict[str, Expr]


@dataclass
class Group(Step):
    """Group rows by columns and apply aggregations."""
    by: List[str]
    aggs: Dict[str, AggFunc]


@dataclass
class Having(Step):
    """Filter grouped results based on condition."""
    condition: Expr


@dataclass
class Save(Step):
    """Save results to target location."""
    target: str


@dataclass
class Let(Step):
    """Assign pipeline result to variable."""
    name: str
    pipeline: "Pipeline"


@dataclass
class Name(Step):
    """Name/alias step for pipeline elements."""
    name: str
