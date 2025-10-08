import os
import tempfile
import zipfile
from typing import Optional

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import numpy as np
import pandas as pd

from AnyQt.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QFileDialog
from AnyQt.QtCore import Qt
from AnyQt.QtGui import QFont

from Orange.data import Table
from Orange.base import Model
from Orange.preprocess import Preprocess
from Orange.widgets import gui
from Orange.widgets.widget import OWWidget, Input, Msg
from Orange.widgets.utils.widgetpreview import WidgetPreview


class OWMLFlowExport(OWWidget):
    name = "MLFlow Export"
    description = "Export a model (with preprocessing) to MLFlow format"
    icon = "icons/SaveModel.svg" 
    priority = 3100
    keywords = "mlflow, export, model, save"

    class Inputs:
        data = Input("Data", Table)  # Raw input data (before preprocessing)
        model = Input("Model", Model)  # Trained model
        preprocessor = Input("Preprocessor", Preprocess)  # Optional preprocessor

    class Error(OWWidget.Error):
        no_data = Msg("No data provided")
        no_model = Msg("No model provided")
        export_failed = Msg("Export failed: {}")

    class Warning(OWWidget.Warning):
        no_preprocessor = Msg("No preprocessor provided - only model will be exported")

    want_main_area = False
    resizing_enabled = False

    def __init__(self):
        super().__init__()
        
        self.data: Optional[Table] = None
        self.model: Optional[Model] = None
        self.preprocessor: Optional[Preprocess] = None
        
        self._setup_gui()

    def _setup_gui(self):
        box = gui.vBox(self.controlArea, "MLFlow Export")
        
        # Status labels
        self.data_label = QLabel("Data: Not connected")
        self.model_label = QLabel("Model: Not connected")
        self.preprocessor_label = QLabel("Preprocessor: Not connected")
        
        font = QFont()
        font.setPointSize(9)
        for label in [self.data_label, self.model_label, self.preprocessor_label]:
            label.setFont(font)
            box.layout().addWidget(label)
        
        gui.separator(box)
        
        # Export button
        self.export_button = QPushButton("Export to MLFlow Archive")
        self.export_button.clicked.connect(self.export_model)
        self.export_button.setEnabled(False)
        self.export_button.setDefault(True)  # Make it the default button
        box.layout().addWidget(self.export_button)
        
        # Info label
        info_label = QLabel(
            "Export requires both data and model inputs.\n"
            "Data input should be raw data (before preprocessing)."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        box.layout().addWidget(info_label)

    @Inputs.data
    def set_data(self, data: Optional[Table]):
        self.data = data
        self.data_label.setText(
            f"Data: {len(data)} instances, {len(data.domain.attributes)} features"
            if data is not None
            else "Data: Not connected"
        )
        self._update_state()

    @Inputs.model
    def set_model(self, model: Optional[Model]):
        self.model = model
        self.model_label.setText(
            f"Model: {type(model).__name__}"
            if model is not None
            else "Model: Not connected"
        )
        self._update_state()

    @Inputs.preprocessor
    def set_preprocessor(self, preprocessor: Optional[Preprocess]):
        self.preprocessor = preprocessor
        self.preprocessor_label.setText(
            f"Preprocessor: {type(preprocessor).__name__}"
            if preprocessor is not None
            else "Preprocessor: Not connected"
        )
        self._update_state()

    def _update_state(self):
        self.Error.clear()
        self.Warning.clear()
        
        # Check required inputs
        if self.data is None:
            self.Error.no_data()
            self.export_button.setEnabled(False)
            return
            
        if self.model is None:
            self.Error.no_model()
            self.export_button.setEnabled(False)
            return
        
        # Show warning if no preprocessor
        if self.preprocessor is None:
            self.Warning.no_preprocessor()
        
        # Enable export if we have data and model
        self.export_button.setEnabled(True)
    
    def export_model(self):
        if not self.data or not self.model:
            return
            
        # Open save dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save MLFlow Model",
            "mlflow_model.zip",
            "MLFlow Archive (*.zip);;All files (*.*)"
        )
        
        if not filename:
            return
            
        try:
            self._export_to_mlflow(filename)
            QMessageBox.information(
                self, "Export Successful", 
                f"Model exported successfully to:\n{filename}"
            )
        except Exception as e:
            self.Error.export_failed(str(e))
            QMessageBox.critical(
                self, "Export Failed",
                f"Failed to export model:\n{str(e)}"
            )

    def _export_to_mlflow(self, output_path: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = os.path.join(temp_dir, "model")
            
            # Create a wrapper class for the Orange model
            class OrangeModelWrapper(mlflow.pyfunc.PythonModel):
                def __init__(self, model, preprocessor=None, input_domain=None):
                    self.model = model
                    self.preprocessor = preprocessor
                    self.input_domain = input_domain  # Domain for input data
                    # Store the model's domain if it has one
                    self.model_domain = getattr(model, 'domain', None)
                
                def predict(self, context, model_input):
                    from Orange.data import Table
                    import logging
                    
                    logger = logging.getLogger(__name__)
                    
                    # Log input information
                    logger.info(f"=== MLflow Model Prediction Debug ===")
                    logger.info(f"Input type: {type(model_input)}")
                    
                    # Handle different input types
                    if isinstance(model_input, (list, tuple)):
                        # Convert list/tuple to numpy array
                        model_input = np.array(model_input)
                        logger.info(f"Converted list/tuple to numpy array")
                    
                    if isinstance(model_input, pd.DataFrame):
                        logger.info(f"DataFrame shape: {model_input.shape}")
                        logger.info(f"DataFrame columns: {list(model_input.columns)[:10]}...")  # First 10 columns
                        
                        expected_names = [attr.name for attr in self.input_domain.attributes]
                        
                        # Map column names to the domain's feature names
                        # This allows anonymous inputs (0, 1, 2...) or any other naming
                        if len(model_input.columns) != len(expected_names):
                            error_msg = (
                                f"Number of columns mismatch. Expected {len(expected_names)} "
                                f"but got {len(model_input.columns)}"
                            )
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                        
                        # Rename columns to match expected names
                        model_input = model_input.copy()
                        model_input.columns = expected_names
                        logger.info(f"Mapped input columns to domain feature names")
                        
                        # Convert to numpy array
                        input_array = model_input.values
                    else:
                        # Already numpy array or converted from list
                        input_array = model_input
                    
                    # Ensure 2D array
                    if len(input_array.shape) == 1:
                        input_array = input_array.reshape(1, -1)
                        logger.info(f"Reshaped 1D array to 2D")
                    
                    logger.info(f"Input array shape: {input_array.shape}")
                    logger.info(f"Input domain attributes: {len(self.input_domain.attributes)} features")
                    logger.info(f"Input domain feature names (first 5): {[attr.name for attr in self.input_domain.attributes[:5]]}")
                    
                    # Create Orange Table with the input domain
                    # The domain already has the correct feature names
                    orange_data = Table.from_numpy(self.input_domain, input_array)
                    logger.info(f"Created Orange Table with shape: {orange_data.X.shape}")
                    
                    # Apply preprocessing if available
                    if self.preprocessor:
                        logger.info(f"Applying preprocessor: {type(self.preprocessor).__name__}")
                        orange_data_before = orange_data
                        orange_data = self.preprocessor(orange_data)
                        logger.info(f"Data shape before preprocessing: {orange_data_before.X.shape}")
                        logger.info(f"Data shape after preprocessing: {orange_data.X.shape}")
                        logger.info(f"Domain after preprocessing: {len(orange_data.domain.attributes)} attributes")
                        
                        # Log the feature names after preprocessing
                        preprocessed_features = [attr.name for attr in orange_data.domain.attributes]
                        logger.info(f"Feature names after preprocessing (first 10): {preprocessed_features[:10]}")
                        if len(preprocessed_features) > 10:
                            logger.info(f"... and {len(preprocessed_features) - 10} more features")
                        
                        # Log if there are any class variables
                        if orange_data.domain.class_vars:
                            logger.info(f"Class variables: {[var.name for var in orange_data.domain.class_vars]}")
                    else:
                        logger.info("No preprocessor to apply")
                    
                    # Log model information
                    logger.info(f"Model type: {type(self.model).__name__}")
                    if self.model_domain is not None:
                        logger.info(f"Model domain expects: {len(self.model_domain.attributes)} features")
                        logger.info(f"Model domain feature names (first 5): {[attr.name for attr in self.model_domain.attributes[:5]]}")
                        
                        # Check domain compatibility - Orange requires exact domain matching
                        logger.info(f"Checking domain compatibility:")
                        logger.info(f"  Data shape: {orange_data.X.shape}")
                        logger.info(f"  Data features: {len(orange_data.domain.attributes)}")
                        logger.info(f"  Model expects: {len(self.model_domain.attributes)} features")
                        
                        # Verify shapes match
                        if len(orange_data.domain.attributes) != len(self.model_domain.attributes):
                            error_msg = (f"Feature count mismatch after preprocessing: "
                                       f"got {len(orange_data.domain.attributes)} but model expects {len(self.model_domain.attributes)}")
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                        
                        # Transform data to model's domain (required by Orange even if features match)
                        if orange_data.domain != self.model_domain:
                            logger.info(f"Transforming data to model's domain")
                            try:
                                orange_data = orange_data.transform(self.model_domain)
                                logger.info(f"Successfully transformed to model domain")
                            except Exception as e:
                                logger.error(f"Domain transform failed: {str(e)}")
                                # Fallback: create new table with model's domain
                                logger.info("Using fallback: creating new table with model domain")
                                orange_data = Table.from_numpy(self.model_domain, orange_data.X)
                                logger.info(f"Created new table with model domain")
                    
                    # Make predictions
                    logger.info("Making predictions...")
                    try:
                        predictions = self.model(orange_data)
                        logger.info(f"Predictions successful, type: {type(predictions)}")
                    except Exception as e:
                        logger.error(f"Prediction failed: {str(e)}")
                        logger.error(f"Orange data domain: {orange_data.domain}")
                        logger.error(f"Orange data shape: {orange_data.X.shape}")
                        raise
                    
                    # Return predictions as numpy array
                    if hasattr(predictions, 'X'):
                        logger.info(f"Returning predictions.X with shape: {predictions.X.shape}")
                        return predictions.X
                    logger.info(f"Returning predictions directly: {type(predictions)}")
                    return predictions
            
            # The input domain is from the raw data (before preprocessing)
            # This is what the MLflow model will accept as input
            input_domain = self.data.domain
            
            # Create the wrapper
            wrapper = OrangeModelWrapper(
                model=self.model,
                preprocessor=self.preprocessor,
                input_domain=input_domain
            )
            
            # Create sample data for MLFlow schema inference
            # Use anonymous column names for the MLflow signature
            column_names = None  # This will make MLflow use default names (0, 1, 2, ...)
            
            # Sample from the raw input data
            sample_data = pd.DataFrame(
                self.data.X[:min(5, len(self.data))],  # Use first 5 rows or all if less
                columns=column_names
            )
            
            # Save the model using MLFlow
            with mlflow.start_run():
                mlflow.pyfunc.save_model(
                    path=model_dir,
                    python_model=wrapper,
                    signature=mlflow.models.infer_signature(sample_data)
                )
            
            # Create ZIP archive
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(model_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, model_dir)
                        zipf.write(file_path, arcname)


if __name__ == "__main__":
    WidgetPreview(OWMLFlowExport).run()