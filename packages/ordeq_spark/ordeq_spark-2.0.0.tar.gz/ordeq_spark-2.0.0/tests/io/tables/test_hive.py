import pytest
from ordeq_spark import SparkHiveTable
from pyspark.sql import SparkSession


# noinspection SqlNoDataSourceInspection
def test_it_saves(spark: SparkSession):
    table = "TestHiveTable_test_it_saves"
    hive_table = SparkHiveTable(table=table)
    cols = ["id", "colour"]
    df = spark.createDataFrame([(1, "yellow"), (2, "orange")], schema=cols)

    hive_table.save(df)

    actual = spark.sql(f"SELECT {','.join(cols)} FROM {table}")
    assert set(actual.collect()) == set(df.collect())


def test_it_saves_by_appending(spark: SparkSession):
    table = "TestHiveTable_test_it_saves_by_appending"
    hive_table = SparkHiveTable(table=table)
    cols = ["id", "colour"]
    df = spark.createDataFrame([(1, "yellow")], schema=cols)

    # Save twice - the 2nd save should be appended
    hive_table.save(df, mode="append")
    hive_table.save(df, mode="append")

    expected = spark.createDataFrame(
        [(1, "yellow"), (1, "yellow")], schema=cols
    )
    actual = spark.sql(f"SELECT {','.join(cols)} FROM {table}")
    assert set(actual.collect()) == set(expected.collect())


@pytest.mark.parametrize(
    ("partition_by", "expected_data"),
    [
        (("id",), (("id=1",), ("id=2",))),
        (("id", "colour"), (("id=1/colour=yellow",), ("id=2/colour=green",))),
    ],
)
def test_it_saves_partitioned_by(
    spark: SparkSession, partition_by, expected_data
):
    table = "TestHiveTable_test_it_saves_partitioned_by"
    hive_table = SparkHiveTable(table=table).with_save_options(
        partition_by=partition_by
    )
    hive_table.save(
        spark.createDataFrame(
            [(1, "yellow", "y"), (2, "green", "g")],
            schema=["id", "colour", "abbr"],
        )
    )
    actual = spark.sql(f"SHOW PARTITIONS {table}")
    expected = spark.createDataFrame(expected_data, schema=["partition"])
    assert set(actual.collect()) == set(expected.collect())
