# © Copyright Databand.ai, an IBM Company 2022

from pathlib import Path

from dbnd_examples_orchestration.data import data_repo
from pandas import DataFrame
from sklearn.linear_model import ElasticNet

from dbnd import parameter, task
from targets.target_config import FileFormat


class TestDocInputsOutputs:
    def test_train_model(self):
        #### DOC START
        @task
        def train_model(
            training_set: DataFrame, alpha: float = 0.5, l1_ratio: float = 0.5
        ) -> ElasticNet:
            lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
            lr.fit(training_set.drop(["quality"], 1), training_set[["quality"]])
            return lr

        train_model.task(training_set=data_repo.wines).dbnd_run()
        #### DOC END

    def test_read_data(self):
        #### DOC START
        @task
        def read_data(path: Path) -> int:
            num_of_lines = len(open(path, "r").readlines())
            return num_of_lines

        #### DOC END
        read_data.task(path=data_repo.wines).dbnd_run()

    def test_prepare_data(self):
        #### DOC START
        @task
        def prepare_data(data: str) -> str:
            return data

        #### DOC END
        prepare_data.task(data="testing prepare dat").dbnd_run()

    def test_prepare_data_load_options(self):
        #### DOC START
        @task(data=parameter[DataFrame].csv.load_options(FileFormat.csv, sep="\t"))
        def prepare_data(data: DataFrame) -> DataFrame:
            data["new_column"] = 5
            return data

        #### DOC END
        prepare_data.dbnd_run(data_repo.wines)
