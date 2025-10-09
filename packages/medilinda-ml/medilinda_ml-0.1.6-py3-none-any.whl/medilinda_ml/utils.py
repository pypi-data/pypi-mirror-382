import pandas as pd


class ShapModelWrapper:
    """
    A wrapper class for the scikit-learn pipeline to make it compatible
    with SHAP's KernelExplainer, ensuring it's pickleable.
    """

    def __init__(self, model, column_names):
        self.model = model
        self.column_names = column_names

    def __call__(self, x):
        """
        The call method that SHAP will use for predictions.
        Converts the NumPy array from SHAP back to a DataFrame before predicting.
        """
        x_df = pd.DataFrame(x, columns=self.column_names)
        return self.model.predict_proba(x_df)
