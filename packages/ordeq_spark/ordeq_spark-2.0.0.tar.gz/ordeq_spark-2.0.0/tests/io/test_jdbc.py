from typing import Any

import pymssql
import pytest
from ordeq_spark import SparkJDBCQuery, SparkJDBCTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType
from testcontainers.mssql import SqlServerContainer


def execute_mssql_query(
    mssql: SqlServerContainer, query: str, return_result: bool = True
) -> list[tuple[Any, ...]] | None:
    """Utility method to execute queries on an MSSQL database. Assumes init
    of the `mssql` fixture in `conftest`. Typically used to test
    saving/loading of Spark to MSSQL.

    Args:
        mssql: Docker container running the SQL server
        query: the query to execute
        return_result: whether to fetch & return all records from cursor

    Returns:
        tuple of rows
    """

    result = None

    with (
        pymssql.connect(
            mssql.get_container_host_ip(),
            mssql.username,
            mssql.password,
            mssql.dbname,
            port=mssql.get_exposed_port(mssql.port),
            autocommit=True,
        ) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(query)
        if return_result:
            result = cursor.fetchall()

    return result


data = [(1, "apples"), (2, "pears")]


@pytest.fixture
def df(spark: SparkSession) -> DataFrame:
    return spark.createDataFrame(
        data,
        schema=StructType(
            fields=[
                StructField("id", IntegerType()),
                StructField("fruit", StringType()),
            ]
        ),
    )


# noinspection SqlNoDataSourceInspection
class TestSparkJDBCTable:
    def test_it_saves_to_mssql(
        self,
        spark: SparkSession,
        mssql_jdbc_url: str,
        mssql: SqlServerContainer,
        df: DataFrame,
    ):
        table = "TestSparkJDBCTable_test_it_saves_to_mssql"

        SparkJDBCTable(
            table=table,
            url=mssql_jdbc_url,
            driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
        ).save(df)

        query = (
            f"SELECT {','.join(df.columns)} FROM {table} "
            f"ORDER BY {','.join(df.columns)}"
        )
        actual = execute_mssql_query(mssql, query=query)
        assert actual == data

    @pytest.mark.parametrize(
        ("mode", "expected"),
        [("overwrite", data), ("append", data + data), ("ignore", data)],
    )
    def test_it_saves_to_mssql_twice(
        self,
        spark: SparkSession,
        mssql_jdbc_url: str,
        mssql: SqlServerContainer,
        df: DataFrame,
        mode: str,
        expected,
    ):
        table = f"TestSparkJDBCTable_test_it_saves_to_mssql_{mode}"

        table = SparkJDBCTable(
            table=table,
            url=mssql_jdbc_url,
            driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
        ).with_save_options(mode=mode)
        table.save(df)
        table.save(df)

        actual = execute_mssql_query(
            mssql, query=f"SELECT {','.join(df.columns)} FROM {table.table}"
        )
        assert sorted(actual) == sorted(expected)

    def test_it_loads_from_mssql(
        self,
        spark: SparkSession,
        mssql_jdbc_url: str,
        mssql: SqlServerContainer,
        df: DataFrame,
    ):
        table = "TestSparkJDBCTable_test_it_loads"

        execute_mssql_query(
            mssql,
            query=f"""
            CREATE TABLE {table} (
                id INTEGER,
                fruit VARCHAR(10)
            );
            INSERT INTO {table}
            VALUES (1, 'apples'),(2, 'pears');
            """,
            return_result=False,
        )

        actual = SparkJDBCTable(
            table=table,
            url=mssql_jdbc_url,
            driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
        ).load()

        assert set(actual.collect()) == set(df.collect())


# noinspection SqlNoDataSourceInspection
class TestSparkJDBCQuery:
    def test_it_loads_from_mssql(
        self,
        spark: SparkSession,
        mssql_jdbc_url: str,
        mssql: SqlServerContainer,
        df: DataFrame,
    ):
        table = "TestSparkJDBCQuery_test_it_loads_from_mssql"

        execute_mssql_query(
            mssql,
            query=f"""
            CREATE TABLE {table} (
                id INTEGER,
                fruit VARCHAR(10)
            );
            INSERT INTO {table}
            VALUES (1, 'apples'),(2, 'pears');
            """,
            return_result=False,
        )

        actual = SparkJDBCQuery(
            query=f"SELECT {','.join(df.columns)} FROM {table}",
            url=mssql_jdbc_url,
            driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
        ).load()

        assert set(actual.collect()) == set(df.collect())
