import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def set_datatypes(
    df: pd.DataFrame, categorical_columns: list[str], date_columns: list[str]
) -> pd.DataFrame:
    for column in categorical_columns:
        df[column] = df[column].astype("category")

    for column in date_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    return df


class DatatypeSetter(BaseEstimator, TransformerMixin):
    def __init__(
        self, categorical_columns: list[str] = None, date_columns: list[str] = None
    ):
        self.categorical_columns = categorical_columns
        self.date_columns = date_columns

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        df = X.copy()

        for column in self.categorical_columns:
            df[column] = df[column].astype("category")

        for column in self.date_columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

        return df
