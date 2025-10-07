from typing import Literal

from ordeq import Node
from ordeq.framework.hook import OutputHook
from ordeq.framework.io import Output
from pyspark.sql import DataFrame


class SparkExplainHook(OutputHook[DataFrame]):
    """Hook to print the Spark execution plan before saving a DataFrame."""

    def __init__(
        self,
        mode: Literal[
            "simple", "extended", "codegen", "cost", "formatted"
        ] = "formatted",
    ):
        self.mode = mode

    def before_output_save(
        self, io: Output[DataFrame], data: DataFrame, node: Node | None = None
    ) -> None:
        data.explain(mode=self.mode)
