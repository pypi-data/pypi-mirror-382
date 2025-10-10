import re
from dataclasses import dataclass
from enum import Enum, auto

from shiny import reactive


class Product(Enum):
    STATISTICS = auto()
    SYNTHETIC_DATA = auto()

    @classmethod
    def to_dict(cls) -> dict[str, str]:
        """
        >>> Product.to_dict()
        {'1': 'DP Statistics', '2': 'DP Synthetic Data'}
        """
        return {
            str(member.value): str(member) for (name, member) in cls.__members__.items()
        }

    def __str__(self) -> str:
        return "DP " + self.name.replace("_", " ").title()


class AnalysisName(str):
    """
    A name like "Histogram" or "Mean".
    """

    pass


class ColumnName(str):
    """
    The exact column header in the CSV.
    """

    pass


class ColumnLabel(str):
    """
    The column label displayed in the UI.
    """

    pass


class ColumnId(str):
    """
    The opaque string we pass as a module ID.

    If we just sanitize the user string, it might collide with another user string.
    Hashing is safer, although hash collisions are not impossible.

    >>> import re
    >>> assert re.match(r'^[_0-9]+$', ColumnId('xyz'))
    """

    def __new__(cls, content):
        id = str(hash(content)).replace("-", "_")
        return str.__new__(cls, id)


class ColumnIdentifier(str):
    """
    A human-readable form that is a valid Python identifier.

    >>> ColumnIdentifier("Does this work?!")
    'does_this_work_'
    """

    def __new__(cls, content):
        identifier = re.sub(r"\W+", "_", content).lower()
        return str.__new__(cls, identifier)


@dataclass(kw_only=True, frozen=True)
class AppState:
    # CLI options:
    is_sample_csv: bool
    in_cloud: bool
    qa_mode: bool

    # Top-level:
    is_tutorial_mode: reactive.Value[bool]

    # Dataset choices:
    initial_private_csv_path: str
    private_csv_path: reactive.Value[str]
    initial_public_csv_path: str
    public_csv_path: reactive.Value[str]
    contributions: reactive.Value[int]
    contributions_entity: reactive.Value[str]
    max_rows: reactive.Value[str]
    initial_product: Product
    product: reactive.Value[Product]

    # Analysis choices:
    column_names: reactive.Value[list[ColumnName]]
    groups: reactive.Value[list[ColumnName]]
    epsilon: reactive.Value[float]

    # Per-column choices:
    # (Note that these are all dicts, with the ColumnName as the key.)
    analysis_types: reactive.Value[dict[ColumnName, AnalysisName]]
    lower_bounds: reactive.Value[dict[ColumnName, float]]
    upper_bounds: reactive.Value[dict[ColumnName, float]]
    bin_counts: reactive.Value[dict[ColumnName, int]]
    weights: reactive.Value[dict[ColumnName, str]]
    analysis_errors: reactive.Value[dict[ColumnName, bool]]

    # Release state:
    released: reactive.Value[bool]
