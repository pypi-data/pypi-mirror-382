from typing import List, Union

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


def build_features(df: pd.DataFrame, boolean_columns: list[str]) -> pd.DataFrame:
    df["patient_bmi"] = df["patient_weight_kg"] / ((df["patient_height_cm"] / 100) ** 2)

    today = pd.to_datetime("today")  # Current date for age calculation
    missing_age_mask = (
        df["patient_age"].isnull() & df["patient_date_of_birth"].notnull()
    )  # Calculate age only where it's missing and dob is available

    df.loc[missing_age_mask, "patient_age"] = (
        today - df.loc[missing_age_mask, "patient_date_of_birth"]
    ).dt.days // 365

    df["patient_age"] = df["patient_age"].fillna(
        df["patient_age"].median()
    )  # Now fill any remaining missing ages (where dob was also missing) with median

    # Define drug prefixes for iteration
    drug_names = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]

    # Compute date differences in days for each drug
    for drug in drug_names:
        start_col = f"{drug}_start_to_onset_days"
        stop_col = f"{drug}_stop_to_onset_days"
        start_stop_col = f"{drug}_start_stop_difference"

        df[start_col] = (
            df["date_of_onset_of_reaction"] - df[f"{drug}_start_date"]
        ).dt.days
        df[stop_col] = (
            df["date_of_onset_of_reaction"] - df[f"{drug}_stop_date"]
        ).dt.days
        df[start_stop_col] = (
            df[f"{drug}_stop_date"] - df[f"{drug}_start_date"]
        ).dt.days

    df["num_suspected_drugs"] = df[boolean_columns].sum(axis=1)

    return df


def drop_unnecessary_columns(
    df: pd.DataFrame, columns_to_drop: list[str]
) -> pd.DataFrame:
    df.drop(columns=columns_to_drop)

    return df


class PatientAgeImputer(BaseEstimator, TransformerMixin):
    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        df = X.copy()

        # Current date for age calculation
        today = pd.to_datetime("today")

        # Calculate age only where it's missing and dob is available
        missing_age_mask = (
            df["patient_age"].isnull() & df["patient_date_of_birth"].notnull()
        )

        df.loc[missing_age_mask, "patient_age"] = (
            today - df.loc[missing_age_mask, "patient_date_of_birth"]
        ).dt.days // 365

        # Convert age column to numeric before calculating median
        df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")

        # Now fill any remaining missing ages (where dob was also missing) with median
        df["patient_age"] = df["patient_age"].fillna(df["patient_age"].median())

        # Explicitly convert the age column to integer type
        df["patient_age"] = df["patient_age"].astype(int)
        return df


class DrugDateDifferenceTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, drug_names: list[str], date_columns: list[str]):
        self.drug_names = drug_names
        self.date_columns = date_columns

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None):
        df = X.copy()

        # Compute date differences in days for each drug
        for drug in self.drug_names:
            start_col = f"{drug}_start_to_onset_days"
            stop_col = f"{drug}_stop_to_onset_days"
            start_stop_col = f"{drug}_start_stop_difference"

            df[start_col] = (
                df["date_of_onset_of_reaction"] - df[f"{drug}_start_date"]
            ).dt.days
            df[stop_col] = (
                df["date_of_onset_of_reaction"] - df[f"{drug}_stop_date"]
            ).dt.days
            df[start_stop_col] = (
                df[f"{drug}_stop_date"] - df[f"{drug}_start_date"]
            ).dt.days

        df = df.drop(columns=self.date_columns)

        return df


class NumberOfSuspectedDrugsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, drug_names: list[str]):
        self.drug_names = drug_names
        self.suspected_drugs_columns = [f"{drug}_suspected" for drug in drug_names]

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        df = X.copy()

        # Make sure only existing columns are used
        cols = [col for col in self.suspected_drugs_columns if col in df.columns]

        if not cols:
            raise ValueError("No *_suspected columns found in DataFrame.")

        df["num_suspected_drugs"] = df[cols].sum(axis=1)

        return df


class DropColumnsTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer to drop specified columns from a DataFrame.
    Works cleanly inside scikit-learn Pipelines.

    Parameters
    ----------
    columns : List[str] or str
        Columns to drop. If a single string is provided, it will be converted to a list.
    """

    def __init__(self, columns: list[str]):
        self.columns = columns

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()

        existing_cols = [col for col in self.columns if col in df.columns]

        return df.drop(columns=existing_cols, errors="ignore")


class NumericalImputer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_columns: list[str]):
        self.numerical_columns = numerical_columns

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()

        df[self.numerical_columns] = (
            df[self.numerical_columns].fillna(-1).infer_objects(copy=False)
        )

        return df


class PatientBMITransformer(BaseEstimator, TransformerMixin):
    """
    Compute Body Mass Index (BMI) from patient weight (kg) and height (cm).

    Adds a new column 'patient_bmi' = weight_kg / (height_m ** 2)
    """

    def __init__(
        self,
        weight_col: str = "patient_weight_kg",
        height_col: str = "patient_height_cm",
        bmi_col: str = "patient_bmi",
    ):
        self.weight_col = weight_col
        self.height_col = height_col
        self.bmi_col = bmi_col

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        if self.weight_col not in X.columns or self.height_col not in X.columns:
            raise KeyError(
                f"Missing required columns: {self.weight_col}, {self.height_col}"
            )

        # Convert height from cm → meters before BMI computation
        height_m = X[self.height_col] / 100

        X[self.bmi_col] = X[self.weight_col] / (height_m**2)

        return X


class FinalColumnSelectorTransformer(BaseEstimator, TransformerMixin):
    """
    Select only the specified columns from the DataFrame.

    Useful as the final step before model prediction or export.

    Parameters
    ----------
    columns : list or str
        The column(s) to retain in the DataFrame.
    """

    def __init__(self, columns: Union[str, List[str]]):
        if isinstance(columns, str):
            columns = [columns]
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        existing_cols = [col for col in self.columns if col in X.columns]
        missing_cols = [col for col in self.columns if col not in X.columns]

        if missing_cols:
            print(f"⚠️ Warning: Missing columns not found in DataFrame: {missing_cols}")

        return X[existing_cols]


class OneHotEncodingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, categorical_columns: list[str]):
        self.categorical_columns = categorical_columns
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.feature_names_out = None

    def fit(self, X: pd.DataFrame, y=None):
        # Fit encoder on categorical columns
        self.encoder.fit(X[self.categorical_columns])
        # Save output feature names
        self.feature_names_out = self.encoder.get_feature_names_out(
            self.categorical_columns
        )
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        X_copy = X.copy()

        # Encode the categorical columns
        encoded = self.encoder.transform(X_copy[self.categorical_columns])
        encoded_df = pd.DataFrame(
            encoded, columns=self.feature_names_out, index=X_copy.index
        )

        # Drop original categorical columns and join encoded ones
        X_copy = X_copy.drop(columns=self.categorical_columns)
        X_transformed = pd.concat([X_copy, encoded_df], axis=1)

        return X_transformed


class MinMaxScalingTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, numerical_columns: list[str]):
        self.numerical_columns = numerical_columns
        self.scaler = MinMaxScaler()
        self.feature_names_out = numerical_columns  # keep same names

    def fit(self, X: pd.DataFrame, y=None):
        # Fit only on numerical columns
        self.scaler.fit(X[self.numerical_columns])
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        X_copy = X.copy()

        # Apply scaling only to specified columns
        scaled_values = self.scaler.transform(X_copy[self.numerical_columns])
        scaled_df = pd.DataFrame(
            scaled_values, columns=self.feature_names_out, index=X_copy.index
        )

        # Replace numerical columns with scaled versions
        X_copy[self.numerical_columns] = scaled_df
        return X_copy
