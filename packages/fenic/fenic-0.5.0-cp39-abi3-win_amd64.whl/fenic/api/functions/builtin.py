"""Built-in functions for Fenic DataFrames."""

import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, List, Optional, Tuple, Union

from pydantic import ConfigDict, validate_call

from fenic.api.column import Column, ColumnOrName
from fenic.api.functions.core import lit
from fenic.core._logical_plan.expressions import (
    ArrayContainsExpr,
    ArrayExpr,
    ArrayLengthExpr,
    AsyncUDFExpr,
    AvgExpr,
    CoalesceExpr,
    CountExpr,
    FirstExpr,
    GreatestExpr,
    LeastExpr,
    ListExpr,
    MaxExpr,
    MinExpr,
    StdDevExpr,
    StructExpr,
    SumExpr,
    UDFExpr,
    WhenExpr,
)
from fenic.core.error import ValidationError
from fenic.core.types import DataType
from fenic.core.types.datatypes import _is_logical_type

"""Built-in functions."""


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def sum(column: ColumnOrName) -> Column:
    """Aggregate function: returns the sum of all values in the specified column.

    Args:
        column: Column or column name to compute the sum of

    Returns:
        A Column expression representing the sum aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        SumExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def avg(column: ColumnOrName) -> Column:
    """Aggregate function: returns the average (mean) of all values in the specified column. Applies to numeric and embedding types.

    Args:
        column: Column or column name to compute the average of

    Returns:
        A Column expression representing the average aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        AvgExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def mean(column: ColumnOrName) -> Column:
    """Aggregate function: returns the mean (average) of all values in the specified column.

    Alias for avg().

    Args:
        column: Column or column name to compute the mean of

    Returns:
        A Column expression representing the mean aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        AvgExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def min(column: ColumnOrName) -> Column:
    """Aggregate function: returns the minimum value in the specified column.

    Args:
        column: Column or column name to compute the minimum of

    Returns:
        A Column expression representing the minimum aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        MinExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def max(column: ColumnOrName) -> Column:
    """Aggregate function: returns the maximum value in the specified column.

    Args:
        column: Column or column name to compute the maximum of

    Returns:
        A Column expression representing the maximum aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        MaxExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def count(column: ColumnOrName) -> Column:
    """Aggregate function: returns the count of non-null values in the specified column.

    Args:
        column: Column or column name to count values in

    Returns:
        A Column expression representing the count aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    if isinstance(column, str) and column == "*":
        return Column._from_logical_expr(CountExpr(lit("*")._logical_expr))
    return Column._from_logical_expr(
        CountExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def collect_list(column: ColumnOrName) -> Column:
    """Aggregate function: collects all values from the specified column into a list.

    Args:
        column: Column or column name to collect values from

    Returns:
        A Column expression representing the list aggregation

    Raises:
        TypeError: If column is not a Column or string
    """
    return Column._from_logical_expr(
        ListExpr(Column._from_col_or_name(column)._logical_expr)
    )

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def array_agg(column: ColumnOrName) -> Column:
    """Alias for collect_list()."""
    return collect_list(column)

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def first(column: ColumnOrName) -> Column:
    """Aggregate function: returns the first non-null value in the specified column.

    Typically used in aggregations to select the first observed value per group.

    Args:
        column: Column or column name.

    Returns:
        Column expression for the first value.
    """
    return Column._from_logical_expr(
        FirstExpr(Column._from_col_or_name(column)._logical_expr)
    )

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def stddev(column: ColumnOrName) -> Column:
    """Aggregate function: returns the sample standard deviation of the specified column.

    Args:
        column: Column or column name.

    Returns:
        Column expression for sample standard deviation.
    """
    return Column._from_logical_expr(
        StdDevExpr(Column._from_col_or_name(column)._logical_expr)
    )

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def struct(
    *args: Union[ColumnOrName, List[ColumnOrName], Tuple[ColumnOrName, ...]]
) -> Column:
    """Creates a new struct column from multiple input columns.

    Args:
        *args: Columns or column names to combine into a struct. Can be:

            - Individual arguments
            - Lists of columns/column names
            - Tuples of columns/column names

    Returns:
        A Column expression representing a struct containing the input columns

    Raises:
        TypeError: If any argument is not a Column, string, or collection of
            Columns/strings
    """
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    expr_columns = [Column._from_col_or_name(c)._logical_expr for c in flattened_args]

    return Column._from_logical_expr(StructExpr(expr_columns))


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def array(
    *args: Union[ColumnOrName, List[ColumnOrName], Tuple[ColumnOrName, ...]]
) -> Column:
    """Creates a new array column from multiple input columns.

    Args:
        *args: Columns or column names to combine into an array. Can be:

            - Individual arguments
            - Lists of columns/column names
            - Tuples of columns/column names

    Returns:
        A Column expression representing an array containing values from the input columns

    Raises:
        TypeError: If any argument is not a Column, string, or collection of
            Columns/strings
    """
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    expr_columns = [Column._from_col_or_name(c)._logical_expr for c in flattened_args]

    return Column._from_logical_expr(ArrayExpr(expr_columns))


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def udf(f: Optional[Callable] = None, *, return_type: DataType):
    """A decorator or function for creating user-defined functions (UDFs) that can be applied to DataFrame rows.

    Warning:
        UDFs cannot be serialized and are not supported in cloud execution.
        User-defined functions contain arbitrary Python code that cannot be transmitted
        to remote workers. For cloud compatibility, use built-in fenic functions instead.

    When applied, UDFs will:
    - Access `StructType` columns as Python dictionaries (`dict[str, Any]`).
    - Access `ArrayType` columns as Python lists (`list[Any]`).
    - Access primitive types (e.g., `int`, `float`, `str`) as their respective Python types.

    Args:
        f: Python function to convert to UDF

        return_type: Expected return type of the UDF. Required parameter.

    Example: UDF with primitive types
        ```python
        # UDF with primitive types
        @udf(return_type=IntegerType)
        def add_one(x: int):
            return x + 1

        # Or
        add_one = udf(lambda x: x + 1, return_type=IntegerType)
        ```

    Example: UDF with nested types
        ```python
        # UDF with nested types
        @udf(return_type=StructType([StructField("value1", IntegerType), StructField("value2", IntegerType)]))
        def example_udf(x: dict[str, int], y: list[int]):
            return {
                "value1": x["value1"] + x["value2"] + y[0],
                "value2": x["value1"] + x["value2"] + y[1],
            }
        ```
    """

    def _create_udf(func: Callable) -> Callable:
        @wraps(func)
        def _udf_wrapper(*cols: ColumnOrName) -> Column:
            col_exprs = [Column._from_col_or_name(c)._logical_expr for c in cols]
            return Column._from_logical_expr(UDFExpr(func, col_exprs, return_type))

        return _udf_wrapper

    if _is_logical_type(return_type):
        raise NotImplementedError(f"return_type {return_type} is not supported for UDFs")

    if f is not None:
        return _create_udf(f)
    return _create_udf

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def async_udf(
    f: Optional[Callable[..., Awaitable[Any]]] = None,
    *,
    return_type: DataType,
    max_concurrency: int = 10,
    timeout_seconds: float = 30,
    num_retries: int = 0,
):
    """A decorator for creating async user-defined functions (UDFs) with configurable concurrency and retries.

    Async UDFs allow IO-bound operations (API calls, database queries, MCP tool calls)
    to be executed concurrently while maintaining DataFrame semantics.

    Args:
        f: Async function to convert to UDF
        return_type: Expected return type of the UDF. Required parameter.
        max_concurrency: Maximum number of concurrent executions (default: 10)
        timeout_seconds: Per-item timeout in seconds (default: 30)
        num_retries: Number of retries for failed items (default: 0)

    Example: Basic async UDF
        ```python
        @async_udf(return_type=IntegerType)
        async def slow_add(x: int, y: int) -> int:
            await asyncio.sleep(1)
            return x + y

        df = df.select(slow_add(fc.col("x"), fc.col("y")).alias("slow_sum"))

        # Or
        async def slow_add_fn(x: int, y: int) -> int:
            await asyncio.sleep(1)
            return x + y

        slow_add = async_udf(
            slow_add_fn,
            return_type=IntegerType
        )
    ```

    Example: API call with custom concurrency and retries
        ```python
        @async_udf(
            return_type=StructType([
                StructField("status", IntegerType),
                StructField("data", StringType)
            ]),
            max_concurrency=20,
            timeout_seconds=5,
            num_retries=2
        )
        async def fetch_data(id: str) -> dict:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.example.com/{id}") as resp:
                    return {
                        "status": resp.status,
                        "data": await resp.text()
                    }
        ```

    Note:
        - Individual failures return None instead of raising exceptions
        - Async UDFs should not block or do CPU-intensive work, as they
          will block execution of other instances of the function call.
    """

    def _create_async_udf(func: Callable[..., Awaitable[Any]]) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise ValidationError(
                f"@async_udf requires an async function, but found a synchronous "
                f"function {func.__name__!r} of type {type(func)}"
            )

        @wraps(func)
        def _async_udf_wrapper(*cols: ColumnOrName) -> Column:
            col_exprs = [Column._from_col_or_name(c)._logical_expr for c in cols]
            return Column._from_logical_expr(
                AsyncUDFExpr(
                    func,
                    col_exprs,
                    return_type,
                    max_concurrency=max_concurrency,
                    timeout_seconds=timeout_seconds,
                    num_retries=num_retries
                )
            )
        return _async_udf_wrapper

    if _is_logical_type(return_type):
        raise NotImplementedError(f"return_type {return_type} is not supported for async UDFs")

    # Support both @async_udf and async_udf(...) syntax
    if f is None:
        return _create_async_udf
    else:
        return _create_async_udf(f)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def asc(column: ColumnOrName) -> Column:
    """Mark this column for ascending sort order with nulls first.

    Args:
        column: The column to apply the ascending ordering to.

    Returns:
        A sort expression with ascending order and nulls first.
    """
    return Column._from_col_or_name(column).asc()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def asc_nulls_first(column: ColumnOrName) -> Column:
    """Alias for asc().

    Args:
        column: The column to apply the ascending ordering to.

    Returns:
        A sort expression with ascending order and nulls first.
    """
    return Column._from_col_or_name(column).asc_nulls_first()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def asc_nulls_last(column: ColumnOrName) -> Column:
    """Mark this column for ascending sort order with nulls last.

    Args:
        column: The column to apply the ascending ordering to.

    Returns:
        A Column expression representing the column and the ascending sort order with nulls last.
    """
    return Column._from_col_or_name(column).asc_nulls_last()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def desc(column: ColumnOrName) -> Column:
    """Mark this column for descending sort order with nulls first.

    Args:
        column: The column to apply the descending ordering to.

    Returns:
        A sort expression with descending order and nulls first.
    """
    return Column._from_col_or_name(column).desc()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def desc_nulls_first(column: ColumnOrName) -> Column:
    """Alias for desc().

    Args:
        column: The column to apply the descending ordering to.

    Returns:
        A sort expression with descending order and nulls first.
    """
    return Column._from_col_or_name(column).desc_nulls_first()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def desc_nulls_last(column: ColumnOrName) -> Column:
    """Mark this column for descending sort order with nulls last.

    Args:
        column: The column to apply the descending ordering to.

    Returns:
        A sort expression with descending order and nulls last.
    """
    return Column._from_col_or_name(column).desc_nulls_last()


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def array_size(column: ColumnOrName) -> Column:
    """Returns the number of elements in an array column.

    This function computes the length of arrays stored in the specified column.
    Returns None for None arrays.

    Args:
        column: Column or column name containing arrays whose length to compute.

    Returns:
        A Column expression representing the array length.

    Raises:
        TypeError: If the column does not contain array data.

    Example: Get array sizes
        ```python
        # Get the size of arrays in 'tags' column
        df.select(array_size("tags"))

        # Use with column reference
        df.select(array_size(col("tags")))
        ```
    """
    return Column._from_logical_expr(
        ArrayLengthExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def array_contains(
    column: ColumnOrName, value: Union[str, int, float, bool, Column]
) -> Column:
    """Checks if array column contains a specific value.

    This function returns True if the array in the specified column contains the given value,
    and False otherwise. Returns False if the array is None.

    Args:
        column: Column or column name containing the arrays to check.

        value: Value to search for in the arrays. Can be:
            - A literal value (string, number, boolean)
            - A Column expression

    Returns:
        A boolean Column expression (True if value is found, False otherwise).

    Raises:
        TypeError: If value type is incompatible with the array element type.
        TypeError: If the column does not contain array data.

    Example: Check for values in arrays
        ```python
        # Check if 'python' exists in arrays in the 'tags' column
        df.select(array_contains("tags", "python"))

        # Check using a value from another column
        df.select(array_contains("tags", col("search_term")))
        ```
    """
    value_column = None
    if isinstance(value, Column):
        value_column = value
    else:
        value_column = lit(value)
    return Column._from_logical_expr(
        ArrayContainsExpr(
            Column._from_col_or_name(column)._logical_expr, value_column._logical_expr
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def when(condition: Column, value: Column) -> Column:
    """Evaluates a conditional expression (like if-then).

    Evaluates a condition for each row and returns a value when true.
    Can be chained with more .when() calls or finished with .otherwise().
    All branches must return the same type.

    Args:
        condition: Boolean expression to test
        value: Value to return when condition is True

    Returns:
        Column: A when expression that can be chained with more conditions

    Raises:
        TypeMismatchError: If the condition is not a boolean Column expression.

    Example:
        ```python
        # Simple if-then (returns null when false)
        df.select(fc.when(col("age") >= 18, fc.lit("adult")))

        # If-then-else
        df.select(
            fc.when(col("age") >= 18, fc.lit("adult")).otherwise(fc.lit("minor"))
        )

        # Multiple conditions (if-elif-else)
        df.select(
            when(col("score") >= 90, "A")
            .when(col("score") >= 80, "B")
            .when(col("score") >= 70, "C")
            .otherwise("F")
        )
        ```

    Note: Without .otherwise(), unmatched rows return null
    """
    return Column._from_logical_expr(
        WhenExpr(None, condition._logical_expr, value._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def coalesce(*cols: ColumnOrName) -> Column:
    """Returns the first non-null value from the given columns for each row.

    This function mimics the behavior of SQL's COALESCE function. It evaluates the input columns
    in order and returns the first non-null value encountered. If all values are null, returns null.

    Args:
        *cols: Column expressions or column names to evaluate. Each argument should be a single
            column expression or column name string.

    Returns:
        A Column expression containing the first non-null value from the input columns.

    Raises:
        ValidationError: If no columns are provided.

    Example: coalesce usage
        ```python
        df.select(coalesce("col1", "col2", "col3"))
        ```
    """
    if not cols:
        raise ValidationError("No columns were provided. Please specify at least one column to use with the coalesce method.")

    exprs = [
        Column._from_col_or_name(c)._logical_expr for c in cols
    ]
    return Column._from_logical_expr(CoalesceExpr(exprs))

@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def greatest(*cols: ColumnOrName) -> Column:
    """Returns the greatest value from the given columns for each row.

    This function mimics the behavior of SQL's GREATEST function. It evaluates the input columns
    in order and returns the greatest value encountered. If all values are null, returns null.

    All arguments must be of the same primitive type (e.g., StringType, BooleanType, FloatType, IntegerType, etc).

    Args:
        *cols: Column expressions or column names to evaluate. Each argument should be a single
            column expression or column name string.

    Returns:
        A Column expression containing the greatest value from the input columns.

    Raises:
        ValidationError: If fewer than two columns are provided.

    Example: greatest usage
        ```python
        df.select(fc.greatest("col1", "col2", "col3"))
        ```
    """
    if len(cols) < 2:
        raise ValidationError(f"greatest() requires at least 2 columns, got {len(cols)}")

    exprs = [
        Column._from_col_or_name(c)._logical_expr for c in cols
    ]
    return Column._from_logical_expr(GreatestExpr(exprs))


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def least(*cols: ColumnOrName) -> Column:
    """Returns the least value from the given columns for each row.

    This function mimics the behavior of SQL's LEAST function. It evaluates the input columns
    in order and returns the least value encountered. If all values are null, returns null.

    All arguments must be of the same primitive type (e.g., StringType, BooleanType, FloatType, IntegerType, etc).

    Args:
        *cols: Column expressions or column names to evaluate. Each argument should be a single
            column expression or column name string.

    Returns:
        A Column expression containing the least value from the input columns.

    Raises:
        ValidationError: If fewer than two columns are provided.

    Example: least usage
        ```python
        df.select(fc.least("col1", "col2", "col3"))
        ```
    """
    if len(cols) < 2:
        raise ValidationError(f"least() requires at least 2 columns, got {len(cols)}")

    exprs = [
        Column._from_col_or_name(c)._logical_expr for c in cols
    ]
    return Column._from_logical_expr(LeastExpr(exprs))
