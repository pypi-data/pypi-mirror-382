import pandas as pd


def clean_columns(df: pd.DataFrame, rename_map: dict = None) -> pd.DataFrame:
    """Rename or clean up column names."""
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def drop_missing(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Drop rows with missing values in selected columns."""
    return df.dropna(subset=cols)


def fill_null_numerical_columns(
    df: pd.DataFrame, numerical_columns: list[str]
) -> pd.DataFrame:
    df[numerical_columns] = df[numerical_columns].fillna(-1)
    return df
