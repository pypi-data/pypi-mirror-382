"""Weights based on exponential bias towards the current time."""

from typing import Self

import numpy as np
import optuna
import pandas as pd

from .weights import WEIGHTS_COLUMN, Weights


class ExponentialWeights(Weights):
    """Exponential weight class."""

    # pylint: disable=too-many-positional-arguments,too-many-arguments

    @classmethod
    def name(cls) -> str:
        """The name of the weight class."""
        return "exponential"

    def set_options(
        self, trial: optuna.Trial | optuna.trial.FrozenTrial, df: pd.DataFrame
    ) -> None:
        pass

    def load(self, folder: str) -> None:
        pass

    def save(self, folder: str, trial: optuna.Trial | optuna.trial.FrozenTrial) -> None:
        pass

    def fit(
        self,
        df: pd.DataFrame,
        y: pd.Series | pd.DataFrame | None = None,
        w: pd.Series | None = None,
        eval_x: pd.DataFrame | None = None,
        eval_y: pd.Series | pd.DataFrame | None = None,
    ) -> Self:
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            data=np.linspace(0, 1.0, len(df)) ** 2.0,
            columns=[WEIGHTS_COLUMN],
            index=df.index,
        )
