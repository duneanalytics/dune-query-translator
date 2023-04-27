# Harmonizer

Harmonizer is a library we have developed at Dune to translate Dune queries from PostgreSQL and Spark SQL to DuneSQL.
We currently use this library in our migration service in the app.

A query is translated through three steps:

1. We use [SQLGlot](https://github.com/tobymao/sqlglot) to transpile the query. 
This is an excellent tool for working with SQL queries. We use it to parse the query into an Abstract Syntax Tree (AST),
manipulating that tree, and then generating the SQL for that query in a different dialect.
We translate from Spark SQL to DuneSQL, and from PostgreSQL to DuneSQL.
2. We create a DuneSQL SQLGlot dialect, allowing us to do stuff like
   - translating string literals '0x...' to 0x... in DuneSQL, since we [support native hex literals](https://dune.com/docs/query/DuneSQL-reference/datatypes/#varbinary).
3. We pass the query through custom rules to make additional changes to the query. Examples of such rules are
   - mapping known changes in table names from the legacy Postgres datasets to corresponding table names in DuneSQL

## Getting started

Install with

```
pip install dune-harmonizer
```

Now import the `translate_` functions in your code:

```python
from dune.harmonizer import translate_spark, translate_postgres
```

with function signatures

```python
def translate_spark(query: str) -> str:
    ...

def translate_postgres(query: str, dataset: str) -> str:
    ...
```

## Contributing

Contributions are very welcome!

Please open an issue or PR, and we will get back to you as soon as we can.

**If you've found a table that doesn't get mapped to one that exists on Dune SQL**, then you can open an issue or just add the table mapping [to this line](https://github.com/duneanalytics/harmonizer/blob/main/dune/harmonizer/table_replacements.py#L18) here in a PR.

**If there is a function that doesn't get mapped correctly**, then you can open an issue or try and [add one here using sqlglot](https://github.com/duneanalytics/harmonizer/blob/main/dune/harmonizer/custom_transforms.py) and open a PR.

## Development

Install with

```
poetry install
```

If the Ruff linter complains, running the following and committing the changes should suffice

```
poetry run ruff . --fix
poetry run black .
```

Run tests with

```
poetry run pytest
```

We test on examples in the `test_cases` directory.
To force an update of the expected outputs, run the `update_expected_outputs` script like below

```
poetry run python tests/update_expected_outputs.py
```
