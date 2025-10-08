from typing import Iterable, List, Sequence, TypeVar, overload, Protocol, runtime_checkable
from markupsafe import Markup

__all__ = ["exc"]

T = TypeVar("T")

class _SupportsStr(Protocol):
    def __str__(self) -> str: ...

@runtime_checkable
class _HasOp(Protocol):
    op: str

class _ExcludeList(List[T]):
    op: str = "NOT IN"

@overload
def exc(iterable: Iterable[T], /) -> _ExcludeList[T]: ...
@overload
def exc(*values: T) -> _ExcludeList[T]: ...

def exc(*args):
    if len(args) == 1 and not isinstance(args[0], (str, bytes)) and isinstance(args[0], Iterable):
        return _ExcludeList(args[0])  # type: ignore[arg-type]
    return _ExcludeList(args)         # type: ignore[arg-type]

def _ensure_sequence(value) -> Sequence[_SupportsStr]:
    from collections.abc import Sequence as _Seq
    if isinstance(value, (str, bytes)) or not isinstance(value, _Seq):
        raise TypeError("inclause filters require an iterable (not str/bytes)")
    return value  # type: ignore[return-value]

def _join(vals: Sequence[_SupportsStr]) -> str:
    return ",".join(str(v) for v in vals)

def _sql_quote(v) -> str:
    s = str(v).replace("'", "''")  # SQL escape single quotes by doubling
    return "'" + s + "'"

def _inclause(value: Sequence[_SupportsStr], set_op: bool = False) -> str:
    vals = _ensure_sequence(value)
    clause = "(" + _join(vals) + ")"
    if set_op:
        op = vals.op if isinstance(vals, _HasOp) else "IN"
        return Markup(op + " " + clause)
    return Markup(clause)

def _inclause_str(value: Sequence[_SupportsStr], set_op: bool = False) -> str:
    vals = _ensure_sequence(value)
    clause = "(" + ",".join(_sql_quote(v) for v in vals) + ")"
    if set_op:
        op = vals.op if isinstance(vals, _HasOp) else "IN"
        return Markup(op + " " + clause)
    return Markup(clause)
