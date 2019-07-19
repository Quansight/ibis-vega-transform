"""
Evaluate vega expressions using ibis
"""
import datetime as dt
import math
import random
import sys
from typing import *
import functools
import operator

import ibis
import ibis.expr.types as it
import pytz
from mypy_extensions import TypedDict
from typing_extensions import Literal

from altair_transform.utils import evaljs


def eval_vegajs(expression: str, datum: ibis.Expr = None) -> ibis.Expr:
    """Evaluate a vega expression"""
    namespace = {"datum": datum} if datum is not None else {}
    namespace.update(VEGAJS_NAMESPACE)
    return evaljs(expression, namespace)


# Type Coercion Functions
def isArray(value: Any) -> bool:
    """Returns true if value is an array, false otherwise."""
    return False


def isBoolean(value: Any) -> bool:
    """Returns true if value is a boolean (true or false), false otherwise."""
    return isinstance(value, it.BooleanValue)


def isDate(value: Any) -> bool:
    """Returns true if value is a Date object, false otherwise.
    """
    return isinstance(value, it.TemporalValue)


def isNumber(value: Any) -> bool:
    """Returns true if value is a number, false otherwise.

    NaN and Infinity are considered numbers.
    """
    return isinstance(value, it.NumericValue)


def isObject(value: Any) -> bool:
    """Returns true if value is an object, false otherwise.

    Following JavaScript typeof convention, null values are considered objects.
    """
    return value is None or isinstance(value, it.MapValue)


def isRegExp(value: Any) -> bool:
    """
    Returns true if value is a RegExp (regular expression)
    object, false otherwise.
    """
    return False


def isString(value: Any) -> bool:
    """Returns true if value is a string, false otherwise."""
    return isinstance(value, it.StringValue)


# Type Coercion Functions
def toBoolean(value: Any) -> bool:
    """
    Coerces the input value to a boolean.
    Null values and empty strings are mapped to null.
    """
    return value.cast("boolean")


def toDate(value: Any) -> Optional[dt.datetime]:
    """
    Coerces the input value to a Date instance.
    Null values and empty strings are mapped to null.
    If an optional parser function is provided, it is used to
    perform date parsing, otherwise Date.parse is used.
    """
    return value.cast("timestamp")


def toNumber(value: Any) -> Optional[float]:
    """
    Coerces the input value to a number.
    Null values and empty strings are mapped to null.
    """
    return value.cast("double")


def toString(value: Any) -> Optional[str]:
    """
    Coerces the input value to a string.
    Null values and empty strings are mapped to null.
    """
    return value.cast("string")


# Date/Time Functions
def now() -> float:
    """Returns the timestamp for the current time."""
    return ibis.now()


def datetime(
    year: int,
    month: int,
    day: int = 0,
    hour: int = 0,
    min: int = 0,
    sec: int = 0,
    millisec: int = 0,
) -> dt.datetime:
    """Returns a new Date instance.
    The month is 0-based, such that 1 represents February.
    """
    # TODO: do we need a local timezone?
    return dt.datetime(
        int(year),
        int(month) + 1,
        int(day),
        int(hour),
        int(min),
        int(sec),
        int(millisec * 1000),
    )


def date(datetime: dt.datetime) -> int:
    """
    Returns the day of the month for the given datetime value, in local time.
    """
    return datetime.day


def day(datetime: dt.datetime) -> int:
    """
    Returns the day of the week for the given datetime value, in local time.
    """
    return (datetime.weekday() + 1) % 7


def year(datetime: dt.datetime) -> int:
    """Returns the year for the given datetime value, in local time."""
    return datetime.year


def quarter(datetime: dt.datetime) -> int:
    """
    Returns the quarter of the year (0-3) for the given datetime value,
    in local time.
    """
    return (datetime.month - 1) // 3


def month(datetime: dt.datetime) -> int:
    """
    Returns the (zero-based) month for the given datetime value, in local time.
    """
    return datetime.month - 1


def hours(datetime: dt.datetime) -> int:
    """
    Returns the hours component for the given datetime value, in local time.
    """
    return datetime.hour


def minutes(datetime: dt.datetime) -> int:
    """
    Returns the minutes component for the given datetime value, in local time.
    """
    return datetime.minute


def seconds(datetime: dt.datetime) -> int:
    """
    Returns the seconds component for the given datetime value, in local time.
    """
    return datetime.second


def milliseconds(datetime: dt.datetime) -> float:
    """
    Returns the milliseconds component for the given datetime value,
    in local time.
    """
    return datetime.microsecond / 1000


def time(datetime: dt.datetime) -> float:
    """Returns the epoch-based timestamp for the given datetime value."""
    return datetime.timestamp() * 1000


def timezoneoffset(datetime):
    # TODO: use tzlocal?
    raise NotImplementedError("timezoneoffset()")


def utc(
    year: int,
    month: int,
    day: int = 0,
    hour: int = 0,
    min: int = 0,
    sec: int = 0,
    millisec: int = 0,
) -> dt.datetime:
    """
    Returns a timestamp for the given UTC date.
    The month is 0-based, such that 1 represents February.
    """
    return dt.datetime(
        int(year),
        int(month) + 1,
        int(day),
        int(hour),
        int(min),
        int(sec),
        int(millisec * 1000),
        tzinfo=pytz.UTC,
    )


FieldDict = TypedDict(
    "FieldDict",
    {
        "field": str,
        # identifies whether tuples in the dataset enumerate values for the
        # field, or specify a continuous range.
        "type": Literal["E", "R", "R-E", "R-LE", "R-RE"],
    },
)

SelectionDict = TypedDict("SelectionDict", {"fields": List[FieldDict], "values": List})


def _test_single_point(expr: ibis.Expr, field: FieldDict, value: Any) -> ibis.Expr:
    column = expr[field["field"]]
    tp = field["type"]
    if tp == "E":
        if isinstance(value, list):
            return column.isin(value)
        return column == value
    lower, upper = value
    if tp == "R":
        return (lower <= column) & (column <= upper)
    if tp == "R-RE":
        return (lower <= column) & (column < upper)
    if tp == "R-LE":
        return (lower < column) & (column <= upper)
    raise NotImplementedError(f"dont recoognize {tp}")


def _test_point(expr: ibis.Expr, entry: SelectionDict) -> ibis.Expr:
    """
    Translated from
    https://github.com/vega/vega/blob/353a4097a5c726ec6b5b1df71722976d246c6cd7/packages/vega-selections/src/selectionTest.js#L12-L48
    and
    https://github.com/vega/vega/blob/master/packages/vega-util/src/inrange.js
    """
    return functools.reduce(
        operator.and_,
        (
            _test_single_point(expr, field, value)
            for field, value in zip(entry["fields"], entry["values"])
        ),
    )


def vlSelectionTest(
    filters: List[SelectionDict],
    expr: ibis.Expr,
    op: Literal["union", "intersect"] = "union",
) -> ibis.Expr:
    """
    Instead of passing in the data name as the first arg, we pass in the actual data, like:

    >>>  [{'fields': [{'type': 'E', 'field': 'c'}], 'values': ['second']}]

    Translated from:

    https://github.com/vega/vega/blob/353a4097a5c726ec6b5b1df71722976d246c6cd7/packages/vega-selections/src/selectionTest.js#L50-L63
    """
    if not filters:
        return expr
    return functools.reduce(
        {"union": operator.or_, "intersect": operator.and_}[op],
        (_test_point(expr, f) for f in filters),
    )


# From https://vega.github.io/vega/docs/expressions/
VEGAJS_NAMESPACE: Dict[str, Any] = {
    # Constants
    "null": ibis.null(),
    "NaN": ibis.NA,
    "E": math.e,
    "LN2": math.log(2),
    "LN10": math.log(10),
    "LOG2E": math.log2(math.e),
    "LOG10E": math.log10(math.e),
    "MAX_VALUE": sys.float_info.max,
    "MIN_VALUE": sys.float_info.min,
    "PI": math.pi,
    "SQRT1_2": math.sqrt(0.5),
    "SQRT2": math.sqrt(2),
    # Type Checking
    "isArray": isArray,
    "isBoolean": isBoolean,
    "isDate": isDate,
    "isNumber": isNumber,
    "isObject": isObject,
    "isRegExp": isRegExp,
    "isString": isString,
    # Type Coercion
    "toBoolean": toBoolean,
    "toDate": toDate,
    "toNumber": toNumber,
    "toString": toString,
    # Control Flow Functions
    "if": lambda test, true_expr, false_expr: ibis.ifelse(test, true_expr, false_expr),
    # Math Functions
    "isNan": lambda x: x.isnull(),
    "abs": ibis.expr.api.abs,
    "acos": ibis.expr.api.acos,
    "asin": ibis.expr.api.asin,
    "atan": ibis.expr.api.atan,
    "atan2": ibis.expr.api.atan2,
    "ceil": ibis.expr.api.ceil,
    "cos": ibis.expr.api.cos,
    "exp": ibis.expr.api.exp,
    "floor": ibis.expr.api.floor,
    "log": ibis.expr.api.ln,
    "max": ibis.expr.api.max,
    "min": ibis.expr.api.min,
    "pow": ibis.expr.api.pow,
    "random": random.random,
    "round": ibis.expr.api.round,
    "sin": ibis.expr.api.sin,
    "sqrt": ibis.expr.api.sqrt,
    "tan": ibis.expr.api.tan,
    # Date/Time Functions
    "now": now,
    "datetime": datetime,
    "date": date,
    "day": day,
    "year": year,
    "quarter": quarter,
    "month": month,
    "hours": hours,
    "minutes": minutes,
    "seconds": seconds,
    "milliseconds": milliseconds,
    "time": time,
    "timezoneoffset": timezoneoffset,
    "utc": utc,
    "length": len,
    "vlSelectionTest": vlSelectionTest
    # TODOs:
    # Remaining Date/Time Functions
    # Array Functions
    # String Functions
    # Object Functions
    # Formatting Functions
    # RegExp Functions
}
