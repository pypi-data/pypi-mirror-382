from collections.abc import Generator
from pathlib import Path
from re import match
from typing import Any

import pytest
from _pytest.tmpdir import TempPathFactory
from pyspark import version
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from testcontainers.mssql import SqlServerContainer


@pytest.fixture(scope="session")
def spark_version() -> str:
    return version.__version__


@pytest.fixture(scope="session")
def spark_warehouse_dir(tmp_path_factory: TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("spark-warehouse")


@pytest.fixture(scope="session")
def spark_conf(spark_version: str, spark_warehouse_dir: Path) -> SparkConf:
    # Iceberg JAR is determined based on Spark minor version:
    spark_minor = match(r"(\d+\.\d+)\.\d+", spark_version).group(1)

    # Creates a SparkConf object containing all configuration of the Session
    # used throughout tests. Note that this test configuration differs from the
    # configuration used in the DAG. E.g., some Airflow tasks might need
    # MSSQL or Iceberg dependencies, whereas others do not. As this
    # configuration grows larger it might make sense to split.
    packages = [
        "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11",
        "org.apache.hadoop:hadoop-aws:3.3.4",
        f"org.apache.iceberg:iceberg-spark-runtime-{spark_minor}_2.12:1.7.1",
    ]
    return SparkConf().setAll([
        ("spark.jars.packages", ",".join(packages)),
        (
            "spark.sql.catalog.spark_catalog",
            "org.apache.iceberg.spark.SparkSessionCatalog",
        ),
        ("spark.sql.catalog.spark_catalog.type", "hadoop"),
        (
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        ),
        (
            "spark.sql.catalog.spark_catalog.warehouse",
            str(spark_warehouse_dir),
        ),
        ("spark.sql.warehouse.dir", str(spark_warehouse_dir)),
        (
            "spark.driver.extraJavaOptions",
            f"-Dderby.system.home={spark_warehouse_dir}/derby",
        ),
    ])


@pytest.fixture(scope="session")
def spark(spark_conf: SparkConf) -> SparkSession:
    # Creates a SparkSession used throughout all tests. See the 'spark_conf'
    # fixture for configuration.
    return (
        SparkSession.builder.config(conf=spark_conf)
        .master("local[2]")
        .enableHiveSupport()
        .getOrCreate()
    )


@pytest.fixture(scope="session")
def mssql() -> Generator[SqlServerContainer, Any, None]:
    # Initializes an MSSQL Docker container that can be used throughout tests.
    db = SqlServerContainer(image="mcr.microsoft.com/mssql/server:2022-latest")
    db.start()
    yield db
    db.stop()


@pytest.fixture(scope="session")
def mssql_jdbc_url(mssql: SqlServerContainer) -> str:
    port = int(mssql.get_exposed_port(mssql.port))
    return (
        f"jdbc:sqlserver://localhost:{port};"
        f"databaseName={mssql.dbname};"
        f"user={mssql.username};"
        f"password={mssql.password};"
        "sslmode=false;"
        "trustServerCertificate=false;"
        "encrypt=false;"
    )
