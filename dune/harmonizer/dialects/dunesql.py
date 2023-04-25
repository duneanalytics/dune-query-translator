from sqlglot import TokenType, exp, transforms
from sqlglot.dialects.trino import Trino


def explode_to_unnest(expression: exp.Expression):
    """Convert explode to cross join unnest"""
    if isinstance(expression, exp.Select):
        for e in expression.args.get("expressions", []):
            # Handle either an aliased explode select, or a plain explode select
            explode_alias = None
            explode = None
            posexplode = None
            if isinstance(e, exp.Alias):
                if isinstance(e.args["this"], exp.Explode):
                    explode_alias = e.alias
                    explode = e.args["this"]
                    to_remove = e
                    explode_expression = explode.args["this"]
                else:
                    continue
            elif isinstance(e, exp.Explode):
                explode = e
                to_remove = e
                explode_expression = explode.args["this"]
            elif isinstance(e, exp.Posexplode):
                posexplode = e
                to_remove = e
                posexplode_expression = posexplode.args["this"]

            if explode is not None:
                array_column_name = "array_column"
                unnested_column_name = explode_alias or "col"
                unnest = exp.Unnest(
                    expressions=[explode_expression], alias=f"{array_column_name}({unnested_column_name})"
                )
                # Remove the `explode()` expression from the select
                expression.args["expressions"].remove(to_remove)

                # If the SELECT has a FROM, do a CROSS JOIN with the UNNEST,
                # otherwise, just do SELECT ... FROM UNNEST
                if expression.args.get("from") is not None:
                    join = exp.Join(this=unnest, kind="CROSS")
                    expression = expression.select(unnested_column_name).join(join)
                else:
                    expression = expression.select(unnested_column_name).from_(unnest)
            elif posexplode is not None:
                array_column_name = "array_column"
                unnested_column_name = "col"
                position_column_name = "pos"
                unnest = exp.Unnest(
                    expressions=[posexplode_expression],
                    alias=f"{array_column_name}({unnested_column_name}, {position_column_name})",
                    ordinality=True,
                )
                # Remove the `explode()` expression from the select
                expression.args["expressions"].remove(to_remove)

                # If the SELECT has a FROM, do a CROSS JOIN with the UNNEST,
                # otherwise, just do SELECT ... FROM UNNEST
                if expression.args.get("from") is not None:
                    join = exp.Join(this=unnest, kind="CROSS")
                    expression = expression.select(position_column_name, unnested_column_name).join(join)
                else:
                    expression = expression.select(position_column_name, unnested_column_name).from_(unnest)
    return expression


class DuneSQL(Trino):
    """The DuneSQL dialect is the dialect used to execute SQL queries on Dune's crypto data sets

    DuneSQL is the Trino dialect with slight modifications."""

    class Tokenizer(Trino.Tokenizer):
        """Text -> Tokens"""

        HEX_STRINGS = ["0x", ("X'", "'")]
        KEYWORDS = Trino.Tokenizer.KEYWORDS | {
            "UINT256": TokenType.UBIGINT,
            "INT256": TokenType.BIGINT,
        }

    class Parser(Trino.Parser):
        """Tokens -> AST"""

        TYPE_TOKENS = Trino.Parser.TYPE_TOKENS | {TokenType.UBIGINT, TokenType.BIGINT}

    class Generator(Trino.Generator):
        """AST -> SQL"""

        TRANSFORMS = Trino.Generator.TRANSFORMS | {
            # Output hex strings as 0xdeadbeef
            exp.HexString: lambda self, e: hex(int(e.name)),
            exp.Select: transforms.preprocess([explode_to_unnest]),
        }

        TYPE_MAPPING = Trino.Generator.TYPE_MAPPING | {
            exp.DataType.Type.UBIGINT: "UINT256",
            exp.DataType.Type.BIGINT: "INT256",
        }
