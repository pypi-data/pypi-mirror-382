# jan883-eda

A collection of utility functions for data analysis, preprocessing, model evaluation, and clustering in Python. Designed to streamline the workflow of data scientists and machine learning practitioners.

## Installation

Install the package via pip:

```bash
pip install jan883-eda
```

## Usage

Below are examples demonstrating how to use some of the key functions in the package. These examples assume you have a DataFrame (`your_dataframe`) or feature matrix (`X`) and target vector (`y`) ready.

### Exploratory Data Analysis (EDA)

- **Inspect DataFrame:**

```python
from jan883_eda import inspect_df

inspect_df(your_dataframe)
```

This displays the head, shape, description, NaN values, and duplicates of the DataFrame.

- **Column Summary:**

```python
from jan883_eda import column_summary

summary = column_summary(your_dataframe)
print(summary)
```

### Data Preprocessing

- **Update Column Names:**

```python
from jan883_eda import update_column_names

updated_df = update_column_names(your_dataframe)
```

- **Label Encoding:**

```python
from jan883_eda import label_encode_column

encoded_df = label_encode_column(your_dataframe, 'column_name')
```

### Model Evaluation

- **Evaluate Classification Model:**

```python
from jan883_eda import evaluate_classification_model
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier()
evaluate_classification_model(model, X, y)
```

- **Test Multiple Regression Models:**

```python
from jan883_eda import best_regression_models

results = best_regression_models(X, y)
print(results)
```

## Functions Overview

The package provides a variety of functions grouped by their purpose:

- **EDA Functions:** `inspect_df`, `column_summary`, `univariate_analysis`, and more.
- **Data Preprocessing:** `update_column_names`, `label_encode_column`, `one_hot_encode_column`, `scale_X_train_X_test`, and more.
- **Model Evaluation:** `evaluate_classification_model`, `evaluate_regression_model`, `best_classification_models`, `best_regression_models`, and more.
- **Clustering Analysis:** `plot_elbow_method`, `plot_intercluster_distance`, `plot_silhouette_visualizer`, and more.

For a complete list of functions and their detailed documentation, refer to the docstrings within the source code or the [official documentation](link-to-docs).

## Requirements

The following dependencies are required to use the package:

- Python >= 3.6
- pandas >= 1.0.0
- numpy >= 1.18.0
- matplotlib >= 3.0.0
- seaborn >= 0.10.0
- scikit-learn >= 0.22.0
- yellowbrick >= 1.0.0
- imblearn >= 0.7.0

These will be automatically installed when you install the package via pip, assuming the package is properly configured with a `setup.py` or `pyproject.toml` file.

## License

This package is distributed under the MIT License. See the [LICENSE](link-to-license) file for more information.

## Contact

For questions, bug reports, or contributions, please visit the [GitHub repository](link-to-repo) or contact the author at [email@example.com](mailto:email@example.com).

---

This README.md provides a clear and concise overview of the package, including its purpose, installation instructions, usage examples, function categories, dependencies, licensing, and contact information, making it suitable for PyPI.
