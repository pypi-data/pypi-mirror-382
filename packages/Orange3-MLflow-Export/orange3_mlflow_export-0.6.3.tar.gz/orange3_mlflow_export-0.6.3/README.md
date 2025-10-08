Orange3 MLflow Export Add-on
============================

This add-on for [Orange3](http://orange.biolab.si) provides a **MLflow Export Widget** that enables exporting Orange3 machine learning models to MLflow format with preprocessing pipelines and all dependencies for reproducible deployment.

## Key Features

- **Complete Pipeline Export**: Captures both trained models and preprocessing transformations
- **Automatic Dependency Management**: Includes Orange3, scikit-learn, pandas, numpy, and all required dependencies
- **MLflow Integration**: Creates deployable MLflow models with proper signatures and metadata
- **Cross-platform Compatibility**: Generated models can be served on any platform that supports MLflow
- **Flexible Input Handling**: Accepts pandas DataFrames and automatically handles domain transformations
- **Smart Column Mapping**: Intelligently handles feature name mismatches through positional mapping

## Installation

### Prerequisites

First, install MLflow and required dependencies:

```bash
pip install -r requirements-dev.txt
```

### Install the Add-on

To install the add-on from source:

```bash
pip install .
```

For development installation (keeps code in development directory):

```bash
pip install -e .
```

### Documentation

Build documentation and widget help:

```bash
make html htmlhelp
```

from the doc directory.

## Quick Start

### Using the Widget in Orange GUI

1. **Launch Orange**:
   ```bash
   orange-canvas
   # or
   python -m Orange.canvas
   ```

2. **Build your workflow**:
   - Load data using a File widget
   - Apply preprocessing (Normalize, Impute, etc.)
   - Train a model with any Orange learner
   - Connect the model to the **MLflow Export** widget (found in the Example section)

3. **Configure the widget**:
   - Connect your trained model to the widget
   - Connect your preprocessing step (must be a Preprocess widget)
   - Provide sample data to define the expected data format for predictions

4. **Export your model**:
   - Set the export path
   - Click save to create a `.mlflow` model

### Programmatic Usage

```python
from orangecontrib.example.widgets.owmlflowexport import OWMLFlowExport
import Orange

# Load and preprocess data
iris = Orange.data.Table("iris")
preprocessor = Orange.preprocess.preprocess.PreprocessorList([
    Orange.preprocess.Normalize(),
    Orange.preprocess.Impute()
])

# Train model with preprocessing
preprocessed_data = preprocessor(iris)
learner = Orange.classification.LogisticRegressionLearner()
model = learner(preprocessed_data)

# Export to MLflow
widget = OWMLFlowExport()
widget.set_model(model)
widget.set_preprocessor(preprocessor)  # Required: provide preprocessing step
widget.set_sample_data(iris)  # Required: define expected data format
widget.filename = "/path/to/model.mlflow"
widget.do_save()
```

### Using Exported Models

```python
import mlflow.pyfunc
import pandas as pd

# Load the exported model
model = mlflow.pyfunc.load_model("/path/to/model.mlflow")

# Prepare input data
data = pd.DataFrame({
    'feature_0': [0.1, 0.2],
    'feature_1': [0.3, 0.4],
    # ... more features
})

# Make predictions
predictions = model.predict(data)
print(predictions)
```

### Serving Models

Deploy your exported model using MLflow's serving capabilities:

```bash
# Serve the model locally
mlflow models serve -m ./model.mlflow -p 8080

# Or serve using Docker
mlflow models build-docker -m ./model.mlflow -n my-model
docker run -p 8080:8080 my-model
```

## Why Use MLflow Export?

### Advantages Over Basic Model Saving

| Feature | Standard Orange Save | MLflow Export |
|---------|---------------------|---------------|
| Preprocessing | ❌ Ignored | ✅ Fully included |
| Dependencies | ❌ Not tracked | ✅ Automatically managed |
| Deployment | ❌ Manual setup required | ✅ MLflow serving ready |
| Cross-platform | ❌ Limited portability | ✅ Universal compatibility |
| Metadata | ❌ Minimal information | ✅ Complete model info |
| Versioning | ❌ None | ✅ MLflow tracking |

### Supported Orange Models

Works with any Orange model that supports the standard prediction interface:

- **Classification**: LogisticRegression, SVM, Tree, RandomForest, NeuralNetwork, etc.
- **Regression**: LinearRegression, RandomForestRegressor, SVR, etc.
- **Preprocessing**: Normalization, Imputation, Continuization, Feature Selection, etc.

## Testing Your Installation

Use the provided test scripts to verify your exported models work correctly:

```bash
# Test with spectral data (125 features)
python test_spectra_model.py ./your_model.mlflow

# Test with generic predictor
python load_predictor.py
```

## Current Limitations

Based on the recent architectural changes:

1. **Single preprocessing step only**: Currently only supports a single Preprocess widget, not multiple preprocessing steps chained together
2. **Explicit data format specification**: Users must provide sample data to define the expected format for predictions
3. **Preprocessing requirement**: The preprocessing step must be explicitly provided as a separate parameter
4. **No headless Orange support**: The widget cannot be used in fully headless environments as Orange3 requires GUI components

## Troubleshooting

### Common Issues

1. **Column name mismatches**: The widget automatically handles feature name differences through positional mapping
2. **Missing dependencies**: Ensure all required packages are installed in your conda environment
3. **Signature inference errors**: Provide sample data when exporting complex models

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Architecture

The add-on centers around the `OrangeModelWrapper` class that bridges Orange models and MLflow:

- **Input Conversion**: Automatically converts pandas DataFrames to Orange Tables
- **Domain Transformation**: Applies all preprocessing steps stored in the model
- **Output Standardization**: Returns predictions in consistent numpy array format
- **Metadata Extraction**: Captures model type, features, and target information

## Contributing

Contributions are welcome! Areas for improvement:

- Additional model format support
- Enhanced metadata extraction
- Performance optimizations
- Documentation improvements

## License

This project follows the same license as Orange3.

## Widget Location

After installation, the **MLflow Export** widget appears in the Orange toolbox under the **Example** section.

![Orange3 MLflow Export Widget](screenshot.png)
