"""
Evaluate vega expressions using ibis
"""
import datetime as dt
import functools
import math
import operator
import random
import sys
from typing import *

import altair_transform.utils._evaljs
import ibis
import ibis.expr.types as it
from altair_transform.utils import evaljs
from mypy_extensions import TypedDict
from typing_extensions import Literal

# Monkey patch altair_transform so that boolean operators  work on ibis expression


def not_operator(value):
    if isinstance(value, ibis.expr.types.ValueExpr):
        return ~value
    return not value


def and_operator(l, r):
    if isinstance(l, ibis.expr.types.ValueExpr):
        if isinstance(r, ibis.expr.types.ValueExpr):
            return l & r
        return r and l
    return l and r


def or_operator(l, r):
    if isinstance(l, ibis.expr.types.ValueExpr):
        if isinstance(r, ibis.expr.types.ValueExpr):
            return l & r
        return r or l
    return l or r


# We also want to monkey patch `x == null` so that it resolves to `(x IS NULL)`, because
# the null literal is not available for omnisci.


def equal_operator(l, r):
    if ibis.null().equals(l):
        return r.isnull()
    if ibis.null().equals(r):
        return l.isnull()
    return l == r


# and the same for not equal
def not_equal_operator(l, r):
    return not_operator(equal_operator(l, r))


def unary_add_operator(v):
    """
    The unary plus operator precedes its operand and evaluates to its operand but attempts to convert it into a number, if it isn't already.
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Arithmetic_Operators#Unary_plus_2
    """
    if isinstance(v, (int, float, it.NumericValue)):
        return v
    if isinstance(v, ibis.expr.types.ValueExpr):
        return v.cast("double")
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return


altair_transform.utils._evaljs.UNARY_OPERATORS["+"] = unary_add_operator
altair_transform.utils._evaljs.UNARY_OPERATORS["!"] = not_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["&&"] = and_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["||"] = or_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["=="] = equal_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["==="] = equal_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["!="] = not_equal_operator
altair_transform.utils._evaljs.BINARY_OPERATORS["!=="] = not_equal_operator


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
    """Returns true if value is a Date object, false otherwise."""
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


def z(v) -> bool:
    """
    Returns whether the value is equal to a literal 0
    """
    return not isinstance(v, ibis.expr.types.Expr) and v == 0


def datetime(y, m, d, h, mi, s, ms):
    """
    This should use https://github.com/ibis-project/ibis/issues/386 if it gets implemented

    Currently we only support use cases that can be turned into a truncate, which is:

        datetime(year(col), 0, 0, 0, 0, 0)
        or
        datetime(year(col), month(col), 0, 0, 0, 0)
        etc.
    """
    if not hasattr(y, "_arg"):
        raise NotImplementedError()
    if not isinstance(y._arg, ibis.expr.operations.ExtractYear):
        raise NotImplementedError()
    date_column = y._arg.arg

    if z(m):
        if not z(d) or not z(h) or not z(mi) or not z(s) or not z(ms):
            raise NotImplementedError()
        return date_column.truncate("year")
    if not m.equals(month(date_column)):
        raise NotImplementedError()

    if z(d):
        if not z(h) or not z(mi) or not z(s) or not z(ms):
            raise NotImplementedError()
        return date_column.truncate("month")
    if not d.equals(date(date_column)):
        raise NotImplementedError(f"{d}, {day(date_column)}")

    if z(h):
        if not z(mi) or not z(s) or not z(ms):
            raise NotImplementedError()
        return date_column.truncate("day")
    if not h.equals(hours(date_column)):
        raise NotImplementedError()

    if z(mi):
        if not z(s) or not z(ms):
            raise NotImplementedError()
        return date_column.truncate("hour")
    if not mi.equals(minutes(date_column)):
        raise NotImplementedError()

    if z(s):
        if not z(ms):
            raise NotImplementedError()
        return date_column.truncate("minute")
    if not s.equals(seconds(date_column)):
        raise NotImplementedError()

    if z(ms):
        return date_column.truncate("second")
    if not ms.equals(milliseconds(date_column)):
        raise NotImplementedError()
    return date_column


def date(datetime):
    """
    Returns the day of the month for the given datetime value, in local time.
    """
    return datetime.day()


def day(datetime):
    """
    Returns the day of the week for the given datetime value, in local time.
    """
    return datetime.day_of_week.index()


def year(datetime):
    """Returns the year for the given datetime value, in local time."""
    return datetime.year()


def quarter(datetime):
    """
    Returns the quarter of the year (0-3) for the given datetime value,
    in local time.
    """
    return (datetime.month() - 1) // 3


def month(datetime):
    """
    Returns the (zero-based) month for the given datetime value, in local time.
    """
    return datetime.month() - 1


def hours(datetime):
    """
    Returns the hours component for the given datetime value, in local time.
    """
    return datetime.hour()


def minutes(datetime):
    """
    Returns the minutes component for the given datetime value, in local time.
    """
    return datetime.minute()


def seconds(datetime):
    """
    Returns the seconds component for the given datetime value, in local time.
    """
    return datetime.second()


def milliseconds(datetime) -> float:
    """
    Returns the milliseconds component for the given datetime value,
    in local time.
    """
    return datetime.millisecond()


def time(datetime) -> float:
    """Returns the epoch-based timestamp for the given datetime value."""
    raise NotImplementedError("time()")


def timezoneoffset(datetime):
    # TODO: use tzlocal?
    raise NotImplementedError("timezoneoffset()")


def utc(year, month, day=0, hour=0, min=0, sec=0, millisec=0):
    """
    Returns a timestamp for the given UTC date.
    The month is 0-based, such that 1 represents February.
    """
    raise NotImplementedError("utc()")
    # return dt.datetime(
    #     int(year),
    #     int(month) + 1,
    #     int(day),
    #     int(hour),
    #     int(min),
    #     int(sec),
    #     int(millisec * 1000),
    #     tzinfo=pytz.UTC,
    # )


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


JS_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _test_single_point(expr: ibis.Expr, field: FieldDict, value: Any) -> ibis.Expr:
    column = expr[field["field"]]
    tp = field["type"]

    # SPECIAL CASE
    # Workaround for case where we are selecting a range of dates
    # for some reason this appears as type E even though it should be type R
    if isinstance(column, ibis.expr.types.TemporalValue) and tp == "E":
        tp = "R"
        value = [dt.datetime.strptime(v, JS_DATETIME_FORMAT) for v in value]

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
    raise NotImplementedError(f"don't recoognize {tp}")


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


def isValid(value):
    """
    Returns true if value is not null, undefined, or NaN, false otherwise.

    https://vega.github.io/vega/docs/expressions/#isValid
    """

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return False
    if isinstance(value, ibis.expr.types.ValueExpr):
        return ~value.isnull()
    return True


def isFinite(value):
    """
    Returns true if value is a finite number. Same as JavaScript’s Number.isFinite.

    https://vega.github.io/vega/docs/expressions/#isFinite
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isFinite
    """

    if isinstance(value, float) and math.isnan(value):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, ibis.expr.types.NumericValue):
        return ~value.isnull()
    return False


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
    "isNaN": lambda x: x.isnull(),
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
    "vlSelectionTest": vlSelectionTest,
    "isValid": isValid,
    "isFinite": isFinite
    # TODOs:
    # Remaining Date/Time Functions
    # Array Functions
    # String Functions
    # Object Functions
    # Formatting Functions
    # RegExp Functions
}
