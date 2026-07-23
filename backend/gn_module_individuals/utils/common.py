from sqlalchemy.sql import Executable
from sqlalchemy.dialects import postgresql


def sql_log(query: Executable) -> None:
    """Give a SQLAlchemy query, log the SQL statement with parameters replaced by their values. Useful for debugging."""
    sql = query.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True},
    )
    print(f"-- DEBUG ------- {sql}")
