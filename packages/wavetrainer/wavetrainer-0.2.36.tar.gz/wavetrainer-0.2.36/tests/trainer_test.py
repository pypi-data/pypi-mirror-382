"""Tests for the trainer class."""
import datetime
import random
import tempfile
import unittest

import pandas as pd

from wavetrainer.trainer import Trainer


class TestTrainer(unittest.TestCase):

    def test_trainer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = Trainer(tmpdir, walkforward_timedelta=datetime.timedelta(days=7), trials=5, allowed_models={"catboost"})
            x_data = [i for i in range(101)]
            x_index = [datetime.datetime(2022, 1, 1) + datetime.timedelta(days=i) for i in range(len(x_data))]
            df = pd.DataFrame(
                data={
                    "column1": x_data,
                    "column2": [(x * random.random()) + random.random() for x in x_data],
                    "column3": [int(((x / random.random()) - random.random()) * 1000.0) for x in x_data],
                },
                index=x_index,
            )
            df["column3"] = df["column3"].astype('category')
            y = pd.DataFrame(
                data={
                    "y": [x % 2 == 0 for x in x_data],
                    "y2": [(x + 2) % 3 == 0 for x in x_data],
                    "y3": [float(x) + 2.0 for x in x_data],
                },
                index=df.index,
            )
            trainer.fit(df, y=y)
            df = trainer.transform(df)
            print("df:")
            print(df)

    def test_trainer_dt_column(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = Trainer(tmpdir, walkforward_timedelta=datetime.timedelta(days=7), trials=5, dt_column="dt_column", allowed_models={"catboost"})
            x_data = [i for i in range(100)]
            x_index = [datetime.datetime(2022, 1, 1) + datetime.timedelta(days=i) for i in range(len(x_data))]
            df = pd.DataFrame(
                data={
                    "column1": x_data,
                    "dt_column": x_index,
                },
            )
            y = pd.DataFrame(
                data={
                    "y": [x % 2 == 0 for x in x_data],
                },
                index=df.index,
            )
            y["y"] = y["y"].astype(bool)
            trainer.fit(df, y=y)
            df = trainer.transform(df)
            print("df:")
            print(df)
