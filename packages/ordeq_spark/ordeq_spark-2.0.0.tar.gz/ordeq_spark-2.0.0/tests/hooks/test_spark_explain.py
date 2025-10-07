from unittest.mock import MagicMock

from _pytest.capture import CaptureFixture
from ordeq_spark import SparkExplainHook
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def test_before_dataset_save_prints_explain_output(
    spark: SparkSession, capsys: CaptureFixture
) -> None:
    """Test that SparkExplain prints the actual Spark execution plan."""
    df = (
        spark.createDataFrame([(1, "a"), (2, "b")], ["id", "val"])
        .where(F.col("id") < 3)
        .filter(F.col("val") != "c")
    )
    hook = SparkExplainHook()
    node = MagicMock()
    dataset = MagicMock()

    hook.before_output_save(dataset, df, node)
    captured = capsys.readouterr()
    assert "== Physical Plan ==" in captured.out
