import pytest
import sqlglot
from sqlglot.optimizer.qualify_columns import validate_qualify_columns

from dune.harmonizer.dunesql.dunesql import DuneSQL
from dune.harmonizer.dunesql.optimize import optimize

testcases = [
    # x = y
    {
        "schema": {"tbl": {"col": "double"}},
        "in": "SELECT col = 1 FROM tbl",
        "out": "SELECT tbl.col = CAST(1 AS DOUBLE) AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "double"}},
        "in": "SELECT 1 = col FROM tbl",
        "out": "SELECT CAST(1 AS DOUBLE) = tbl.col AS _col_0 FROM tbl",
    },
    # x = y
    {
        "schema": {"tbl": {"col": "varchar"}},
        "in": "SELECT col = 0xdeadbeef FROM tbl",
        "out": "SELECT tbl.col = CAST(0xdeadbeef AS VARCHAR) AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "varchar"}},
        "in": "SELECT 0xdeadbeef = col FROM tbl",
        "out": "SELECT CAST(0xdeadbeef AS VARCHAR) = tbl.col AS _col_0 FROM tbl",
    },
    # x = y
    {
        "schema": {"tbl": {"col": "varchar"}},
        "in": "SELECT col = '0xdeadbeef' FROM tbl",
        "out": "SELECT tbl.col = '0xdeadbeef' AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "varchar"}},
        "in": "SELECT '0xdeadbeef' = col FROM tbl",
        "out": "SELECT '0xdeadbeef' = tbl.col AS _col_0 FROM tbl",
    },
    # x = y
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT col = '0xdeadbeef' FROM tbl",
        # should remove quotes instead of casting?
        "out": "SELECT tbl.col = CAST('0xdeadbeef' AS VARBINARY) AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT '0xdeadbeef' = col FROM tbl",
        # should remove quotes instead of casting?
        "out": "SELECT CAST('0xdeadbeef' AS VARBINARY) = tbl.col AS _col_0 FROM tbl",
    },
    # x = y
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT col = 'a string' FROM tbl",
        "out": "SELECT tbl.col = CAST('a string' AS VARBINARY) AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT 'a string' = col FROM tbl",
        "out": "SELECT CAST('a string' AS VARBINARY) = tbl.col AS _col_0 FROM tbl",
    },
    # x = y
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT col = 0xdeadbeef FROM tbl",
        "out": "SELECT tbl.col = 0xdeadbeef AS _col_0 FROM tbl",
    },
    # y = x
    {
        "schema": {"tbl": {"col": "varbinary"}},
        "in": "SELECT 0xdeadbeef = col FROM tbl",
        "out": "SELECT 0xdeadbeef = tbl.col AS _col_0 FROM tbl",
    },
]


@pytest.mark.parametrize("tc", testcases)
def test_optimize_cast(tc):
    dune_sql_expr = sqlglot.parse_one(tc["in"], read=DuneSQL)
    optimized = optimize(dune_sql_expr, schema=tc["schema"])
    validate_qualify_columns(optimized)
    assert tc["out"] == optimized.sql(DuneSQL)


# case 1
# varbinary lit = varchar col
# 0xdead = col -> '0xdead' = col -> 0xdead = col

# case 2
# varchar lit (hexstring) = varbinary col
# '0xdead' = col -> 0xdead = col

# case 3
# varchar lit (hexstring) = varchar col
# '0xdead' = col -> '0xdead' = col

# case 4
# varbinary lit = varbinary col
# 0xdead = col -> 0xdead = col
