import matplotlib

matplotlib.use("agg")

import os
from pprint import pprint

import joblib
import mlflow
import numpy as np
import pandas as pd
import shap
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from medilinda_ml.columns import (
    COLUMNS_FOR_ONE_HOT,
    COLUMNS_TO_DROP,
    DATE_COLUMNS,
    DRUG_NAMES,
    FINAL_COLUMNS,
    INITIAL_CATEGORICAL_COLUMNS,
    NUMERICAL_COLUMNS,
    TARGET_COLUMN,
)
from medilinda_ml.data.set_datatypes import DatatypeSetter
from medilinda_ml.features.build_features import (
    DropColumnsTransformer,
    DrugDateDifferenceTransformer,
    FinalColumnSelectorTransformer,
    MinMaxScalingTransformer,
    NumberOfSuspectedDrugsTransformer,
    NumericalImputer,
    OneHotEncodingTransformer,
    PatientAgeImputer,
    PatientBMITransformer,
)
from medilinda_ml.paths import DATA_DIR
from medilinda_ml.settings import settings
from medilinda_ml.utils import ShapModelWrapper
from mlflow.models import infer_signature
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import (
    RandomizedSearchCV,
    RepeatedStratifiedKFold,
    train_test_split,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

os.environ["DATABRICKS_HOST"] = settings.databricks_host
os.environ["DATABRICKS_TOKEN"] = settings.databricks_token
os.environ["MLFLOW_RECORD_ENV_VARS_IN_MODEL_LOGGING"] = "false"

# # To allow uv to be used
# os.environ["MLFLOW_LOCK_MODEL_DEPENDENCIES"] = "true"

# Set MLFlow Tracking URI
mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

# Create MLFlow Experiment if not created
if mlflow.get_experiment_by_name(settings.mlflow_experiment_path) is None:
    mlflow.create_experiment(
        name=settings.mlflow_experiment_path,
        artifact_location=settings.mlflow_artifact_path,
    )

# Set MLFlow Experiment if not created
mlflow.set_experiment(settings.mlflow_experiment_path)



def train_model(df_path: str) -> None:
    mlflow.autolog()
    df = pd.read_csv(df_path)

    X = df.drop(columns=[TARGET_COLUMN], axis=1)
    y = df[TARGET_COLUMN]

    X_train_and_val, X_test, y_train_and_val, y_test = train_test_split(
        X, y, stratify=y, test_size=0.25
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_and_val,
        y_train_and_val,
        stratify=y_train_and_val,
        test_size=0.2,
        random_state=42,
    )

    ordinal_encoder = OrdinalEncoder(
        categories=[["certain", "likely", "possible", "unlikely"]]
    )

    y_train_enc = ordinal_encoder.fit_transform(y_train.to_frame()).ravel()
    y_val_enc = ordinal_encoder.transform(y_val.to_frame()).ravel()
    y_test_enc = ordinal_encoder.transform(y_test.to_frame()).ravel()

    print("✅ Train shape:", X_train.shape)
    print("✅ Validation shape:", X_val.shape)
    print("✅ Test shape:", X_test.shape)

    estimators_and_param_grids = {
        "decision_tree": (
            DecisionTreeClassifier(random_state=42),
            {"max_depth": [25, 50, 100]},
        ),
        "ada_boost": (
            AdaBoostClassifier(random_state=42),
            {"n_estimators": [10, 50], "learning_rate": [0.1, 1.0]},
        ),
        "logistic_regression": (
            LogisticRegression(random_state=42, max_iter=1000, solver="saga"),
            {"C": [0.01, 0.1, 1, 10], "penalty": ["l2"]},
        ),
        # "random_forest": (
        #     RandomForestClassifier(random_state=42),
        #     {
        #         "n_estimators": [50, 100, 200],
        #         "max_depth": [None, 10, 30, 50],
        #         "max_features": ["sqrt", "log2"],
        #     },
        # ),
        # "gradient_boosting": (
        #     GradientBoostingClassifier(random_state=42),
        #     {
        #         "n_estimators": [50, 100],
        #         "learning_rate": [0.01, 0.1],
        #         "max_depth": [3, 5],
        #         "subsample": [0.8, 1.0],
        #     },
        # ),
        "svm": (
            SVC(probability=True, random_state=42),
            {
                "kernel": ["rbf"],
                "C": [0.1, 1, 3],
                "gamma": ["scale", "auto"],
            },
        ),
        "knn": (
            KNeighborsClassifier(),
            {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"], "p": [1, 2]},
        ),
        "naive_bayes": (GaussianNB(), {}),
    }
    # --- Cross-validation setup ---
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)

    best_estimators_and_best_param_grids = {}

    for name, (estimator, param_grid) in estimators_and_param_grids.items():
        print(f"\n🧠 Training model: {name}")
        print("—" * 80)

        # --- Build full pipeline for this estimator ---
        pipeline = Pipeline(
            [
                (
                    "set_datatypes",
                    DatatypeSetter(
                        categorical_columns=INITIAL_CATEGORICAL_COLUMNS,
                        date_columns=DATE_COLUMNS,
                    ),
                ),
                ("patient_age_imputer", PatientAgeImputer()),
                ("patient_bmi", PatientBMITransformer()),
                (
                    "drug_date_difference",
                    DrugDateDifferenceTransformer(
                        drug_names=DRUG_NAMES,
                        date_columns=DATE_COLUMNS,
                    ),
                ),
                (
                    "num_of_suspected_drugs",
                    NumberOfSuspectedDrugsTransformer(drug_names=DRUG_NAMES),
                ),
                (
                    "drop_irrelevant_columns",
                    DropColumnsTransformer(columns=COLUMNS_TO_DROP),
                ),
                (
                    "numerical_imputer",
                    NumericalImputer(numerical_columns=NUMERICAL_COLUMNS),
                ),
                (
                    "one_hot_encoding",
                    OneHotEncodingTransformer(categorical_columns=COLUMNS_FOR_ONE_HOT),
                ),
                (
                    "numerical_scaling",
                    MinMaxScalingTransformer(numerical_columns=["patient_bmi"]),
                ),
                (
                    "final_column",
                    FinalColumnSelectorTransformer(columns=FINAL_COLUMNS),
                ),
                ("smote", SMOTE(random_state=42)),
                ("classifier", estimator),
            ],
        )

        # # --- Run pipeline on training data ---
        # print("\n🚀 Running pipeline...")
        # X_train_resampled, y_train_resampled = pipeline.fit_resample(
        #     X_train, y_train_enc
        # )

        # # --- Display results ---
        # print("\n✅ Pipeline output:")
        # print(pd.DataFrame(X_train_resampled).info())
        # print("\nOutput shape:", X_train_resampled.shape)

        # # --- Check class balance ---
        # print("Before SMOTE:")
        # print(pd.Series(y_train_enc).value_counts(normalize=True))
        # print("\nAfter SMOTE:")
        # print(pd.Series(y_train_resampled).value_counts(normalize=True))

        # Prefix param grid keys with "classifier__"
        tuned_params = {f"classifier__{k}": v for k, v in param_grid.items()}

        # --- RandomizedSearchCV ---
        search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=tuned_params,
            cv=cv,
            n_iter=int(min(20, np.prod([len(v) for v in tuned_params.values()]))),
            scoring="f1_weighted",
            verbose=2,
            n_jobs=-1,
        )

        with mlflow.start_run():
            search.fit(X_train, y_train_enc)

            # --- Results ---
            best_estimator = search.best_estimator_
            best_params = search.best_params_

            best_estimators_and_best_param_grids[name] = (best_estimator, best_params)

            print("\n✅ Best params:")
            pprint(best_params)

            # --- Evaluate on validation data ---
            y_pred = best_estimator.predict(X_val)

            decoded_y_val = ordinal_encoder.inverse_transform(
                y_val_enc.reshape(-1, 1)
            ).ravel()
            decoded_y_pred = ordinal_encoder.inverse_transform(
                y_pred.reshape(-1, 1)
            ).ravel()

            print("\n📊 Validation Results:")
            print(classification_report(decoded_y_val, decoded_y_pred))

            print("═" * 80)

            # --- Log model ---
            signature = infer_signature(X_test, y_pred)

            input_example = X_test.iloc[:1]

            model_name = f"rf_smote_pipeline_{name}"

            registered_model_name = f"workspace.default.{model_name}"

            mlflow.sklearn.log_model(
                sk_model=best_estimator,
                name=model_name,
                input_example=input_example,
                registered_model_name=registered_model_name,
                signature=signature,
            )
            print("📦 Model logged to MLflow successfully.")

            encoder_path = "ordinal_encoder.pkl"

            try:
                joblib.dump(ordinal_encoder, encoder_path)
                mlflow.log_artifact(encoder_path, artifact_path="encoders")
                print("📦 Ordinal encoder logged to MLflow successfully.")
            finally:
                if os.path.exists(encoder_path):
                    os.remove(encoder_path)

            print("📦 Creating and logging SHAP explainer...")

            # Temporarily disable autologging to prevent conflicts
            mlflow.autolog(disable=True)

            explainer_path = "shap_explainer.pkl"

            try:
                # preprocessed_X_train, _ = best_estimator[:-1].fit_resample(
                #     X_train, y_train_enc
                # )
                background_data = X_train.sample(100, random_state=42)

                predict_fn = ShapModelWrapper(best_estimator, X_train.columns)

                explainer = shap.KernelExplainer(predict_fn, background_data)

                joblib.dump(explainer, explainer_path)
                mlflow.log_artifact(explainer_path, artifact_path="explainers")
                print("📦 SHAP explainer logged to MLflow successfully.")
            finally:
                if os.path.exists(explainer_path):
                    os.remove(explainer_path)
                    print("🧹 Cleaned up local explainer file.")

        print("DONE")


if __name__ == "__main__":
    train_model(f"{DATA_DIR}/data.csv")
