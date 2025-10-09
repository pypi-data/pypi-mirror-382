# Medilinda-ML 💊

[![PyPI version](https://badge.fury.io/py/medilinda-ml.svg)](https://badge.fury.io/py/medilinda-ml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/medilinda-ml)](https://pypi.org/project/medilinda-ml/)

A complete machine learning pipeline to predict the causality of Adverse Drug Reactions (ADRs) from patient and medication data. This package provides tools for data preprocessing, feature engineering, model training, and evaluation, with seamless MLflow integration for experiment tracking.

## Overview

The goal of Medilinda-ML is to provide a reproducible and easy-to-use system for assessing the likelihood that a suspected drug is the cause of an adverse reaction. The pipeline is built with `scikit-learn` and handles common challenges in clinical data, such as missing values and class imbalance (using SMOTE).

## Features

-   **End-to-End Pipeline**: From raw data to a trained model.
-   **Feature Engineering**: Automatically calculates features like patient BMI, drug administration duration, and more.
-   **Class Imbalance Handling**: Uses SMOTE to create a balanced dataset for training.
-   **Hyperparameter Tuning**: Leverages `RandomizedSearchCV` to find the best model configuration.
-   **Experiment Tracking**: Integrated with MLflow to log parameters, metrics, and models.

## Installation

Install Medilinda-ML directly from PyPI:

```bash
pip install medilinda-ml
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
