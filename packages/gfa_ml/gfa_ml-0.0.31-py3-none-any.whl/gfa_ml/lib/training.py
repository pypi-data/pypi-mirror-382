import shutil
import joblib
import numpy as np
import pandas as pd
import logging
import traceback
import torch
import os
import shap
import matplotlib.pyplot as plt
import mlflow
import mlflow.pytorch
from gfa_ml.lib.default import (
    WRAPPED_MODEL,
    SCALER_PATH,
    DEFAULT_EXTENSION,
    INPUT_COLS_PATH,
)
from gfa_ml.lib.constant import COLOR_MAP
from tqdm import tqdm
from gfa_ml.data_model.data_type import ModelType
from gfa_ml.data_model.common import RunConfig, TransformerConfig, LSTMConfig
from gfa_ml.lib.utils import moving_average, downsample
from gfa_ml.lib.data_processing import (
    create_time_aware_sequences,
    apply_scalers,
    normalize_sequences,
    split_time_series_data,
)
from typing import Union

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
from gfa_ml.data_model.ml_model import (
    LSTMModel,
    MAPELoss,
    SMAPELoss,
    TransformerModel,
    MLModelWithScaler,
)
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


def build_lstm_model(input_size: int, ml_model_config: LSTMConfig):
    try:
        hidden_neurons: int = ml_model_config.hidden_neurons
        activation_function: str = ml_model_config.activation_function
        drop_rate: float = ml_model_config.drop_rate
        optimizer: str = ml_model_config.optimizer
        loss: str = ml_model_config.loss
        learning_rate: float = ml_model_config.learning_rate
        num_layers: int = ml_model_config.num_layers

        if activation_function.lower() == "tanh":
            activation_function = nn.Tanh
        elif activation_function.lower() == "relu":
            activation_function = nn.ReLU
        elif activation_function.lower() == "sigmoid":
            activation_function = nn.Sigmoid
        elif activation_function.lower() == "leakyrelu":
            activation_function = nn.LeakyReLU
        elif activation_function.lower() == "elu":
            activation_function = nn.ELU
        elif activation_function.lower() == "softmax":
            activation_function = nn.Softmax
        else:
            raise ValueError(f"Unsupported activation function: {activation_function}")
        model = LSTMModel(
            input_size=input_size,
            hidden_neurons=hidden_neurons,
            drop_rate=drop_rate,
            activation_function=activation_function,
            num_layers=num_layers,
        )

        # Setup optimizer
        if optimizer.lower() == "adam":
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer}")

        # Loss function
        if loss.lower() == "mse":
            loss_fn = nn.MSELoss()
        elif loss.lower() == "map":
            loss_fn = MAPELoss()
        elif loss.lower() == "smape":
            loss_fn = SMAPELoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss}")

        return model, optimizer, loss_fn
    except Exception as e:
        logging.error(f"Error building LSTM model: {e}")
        logging.error(traceback.format_exc())
        return None


def build_transformer_model(input_size: int, ml_model_config: TransformerConfig):
    try:
        d_model = ml_model_config.d_model
        nhead = ml_model_config.nhead
        num_layers = ml_model_config.num_layers
        dim_feedforward = ml_model_config.dim_feedforward
        drop_rate = ml_model_config.drop_rate
        activation_function = ml_model_config.activation_function
        optimizer = ml_model_config.optimizer
        loss = ml_model_config.loss
        learning_rate = ml_model_config.learning_rate

        if activation_function.lower() == "tanh":
            activation_fn = nn.Tanh
        elif activation_function.lower() == "relu":
            activation_fn = nn.ReLU
        elif activation_function.lower() == "sigmoid":
            activation_fn = nn.Sigmoid
        elif activation_function.lower() == "leakyrelu":
            activation_fn = nn.LeakyReLU
        elif activation_function.lower() == "elu":
            activation_fn = nn.ELU
        elif activation_function.lower() == "softmax":
            activation_fn = nn.Softmax
        else:
            raise ValueError(f"Unsupported activation function: {activation_function}")

        model = TransformerModel(
            input_size=input_size,
            d_model=d_model,
            nhead=nhead,
            num_layers=num_layers,
            dim_feedforward=dim_feedforward,
            drop_rate=drop_rate,
            activation_function=activation_fn,
        )

        if optimizer.lower() == "adam":
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer}")

        # Loss function
        if loss.lower() == "mse":
            loss_fn = nn.MSELoss()
        elif loss.lower() == "map":
            loss_fn = MAPELoss()
        elif loss.lower() == "smape":
            loss_fn = SMAPELoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss}")

        return model, optimizer, loss_fn

    except Exception as e:
        logging.error(f"Error building Transformer model: {e}")
        logging.error(traceback.format_exc())
        return None


def train_and_evaluate(
    df: pd.DataFrame,
    run_config: RunConfig,
    explainability: bool = False,
    plot_path: str = None,
    run_name: str = None,
    mlflow_enable: bool = False,
    interpolate_outliers: bool = False,
    image_extension: str = "svg",
    experiment_name: str = "default",
):
    try:
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run(run_name=run_name, nested=True) as run:
            mlflow_run_id = run.info.run_id
            ml_model_config = run_config.ml_model_config
            data_config = run_config.data_config
            training_config = run_config.training_config

            try:
                mlflow.log_param("epochs", training_config.epochs)
                mlflow.log_param("batch_size", training_config.batch_size)
                mlflow.log_param("patience", training_config.patience)
                mlflow.log_param("plot", training_config.plot)
                mlflow.log_param("sample_size", training_config.sample_size)
                mlflow.log_param(
                    "smooth_window_size", training_config.smooth_window_size
                )

                mlflow.log_param(
                    "activation_function", ml_model_config.activation_function
                )
                mlflow.log_param("drop_rate", ml_model_config.drop_rate)
                mlflow.log_param("model_type", ml_model_config.model_type.value)
                mlflow.log_param("optimizer", ml_model_config.optimizer)
                mlflow.log_param("loss", ml_model_config.loss)
                mlflow.log_param("learning_rate", ml_model_config.learning_rate)
                mlflow.log_param("num_layers", ml_model_config.num_layers)

                mlflow.log_param("train_ratio", data_config.train_ratio)
                mlflow.log_param("validation_ratio", data_config.validation_ratio)
                mlflow.log_param("history_size", data_config.history_size)
                mlflow.log_param("output_col", data_config.output_col)
                mlflow.log_param("index_col", data_config.index_col)
                mlflow.log_param("retention_col", data_config.retention_col)
                mlflow.log_param("retention_padding", data_config.retention_padding)
                mlflow.log_param("explainability", explainability)

            except Exception as e:
                logging.error(f"Error logging MLflow parameters: {e}")
            try:
                mlflow.log_param("input_cols", data_config.input_cols)

            except Exception as e:
                logging.error(f"Error logging input_cols: {e}")
            try:
                with open(INPUT_COLS_PATH, "w") as f:
                    f.write(f"{data_config.input_cols}")
                mlflow.log_artifact(INPUT_COLS_PATH)
            except Exception as e:
                logging.error(f"Error saving input_cols: {e}")
            output_col = data_config.output_col
            input_cols = data_config.input_cols
            train_ratio = data_config.train_ratio
            validation_ratio = data_config.validation_ratio
            history_size = data_config.history_size
            index_col = data_config.index_col
            retention_col = data_config.retention_col
            retention_padding = data_config.retention_padding
            interval_minutes = data_config.interval_minutes
            num_rows = data_config.num_rows
            min_rows = data_config.min_rows

            batch_size = training_config.batch_size
            epochs = training_config.epochs
            smooth_window_size = training_config.smooth_window_size
            sample_size = training_config.sample_size
            n_features_importance = training_config.n_features_importance
            use_markers = training_config.use_markers
            plot = training_config.plot

            if input_cols is None or output_col is None:
                logging.error("Input columns and output column must be specified.")
                return

            # split df in to train_validate df and test df
            test_ratio = 1 - train_ratio - validation_ratio
            # get the last part of the df following the test ratio for testing
            test_size = int(len(df) * test_ratio)
            test_df = df.iloc[-test_size:]
            train_validate_df = df.iloc[:-test_size]

            if interpolate_outliers:
                column_extension = DEFAULT_EXTENSION
            else:
                column_extension = None

            X, y = create_time_aware_sequences(
                train_validate_df,
                input_cols=input_cols,
                output_col=output_col,
                history_size=history_size,
                index_col=index_col,
                retention_col=retention_col,
                retention_padding=retention_padding,
                column_extension=DEFAULT_EXTENSION,
                interval_minutes=interval_minutes,
                num_rows=num_rows,
                min_rows=min_rows,
            )
            X_t, y_t, X_t_index, y_t_index = create_time_aware_sequences(
                test_df,
                input_cols=input_cols,
                output_col=output_col,
                history_size=history_size,
                index_col=index_col,
                retention_col=retention_col,
                retention_padding=retention_padding,
                column_extension=column_extension,
                interval_minutes=interval_minutes,
                num_rows=num_rows,
                min_rows=min_rows,
                return_index=True,
            )

            logging.info(
                f"Created dataset with X shape: {X.shape}, and y shape: {y.shape}"
            )

            model_type = ml_model_config.model_type
            if isinstance(model_type, str):
                model_type = ModelType(model_type.lower())

            if model_type == ModelType.LSTM:
                logging.info("Building LSTM model...")
                mlmodel, optimizer, loss_fn = build_lstm_model(
                    input_size=X.shape[-1], ml_model_config=ml_model_config
                )
                logging.info("LSTM model built successfully.")
                if mlflow_enable:
                    mlflow.log_param("hidden_neurons", ml_model_config.hidden_neurons)
            elif model_type == ModelType.TRANSFORMER:
                logging.info("Building Transformer model...")
                mlmodel, optimizer, loss_fn = build_transformer_model(
                    input_size=X.shape[-1], ml_model_config=ml_model_config
                )
                logging.info("Transformer model built successfully.")
                if mlflow_enable:
                    try:
                        mlflow.log_param("nhead", ml_model_config.nhead)
                        mlflow.log_param("d_model", ml_model_config.d_model)
                        mlflow.log_param(
                            "dim_feedforward", ml_model_config.dim_feedforward
                        )
                    except Exception as e:
                        logging.error(
                            f"Error logging MLflow parameters in {model_type}: {e}"
                        )
            else:
                logging.error(f"Unsupported model type: {model_type}")

            X_norm, Y_norm, x_scalers, y_scaler = normalize_sequences(X, y)
            X_train, y_train, X_val, y_val = split_time_series_data(
                X_norm,
                Y_norm,
                train_ratio=train_ratio,
                validation_ratio=validation_ratio,
            )

            X_test, y_test = apply_scalers(X_t, y_t, x_scalers, y_scaler)

            logging.info(f"Data split into train, validation, and test sets.")

            # Set device for training
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"Using device: {device}")
            mlmodel.to(device)

            # Convert numpy arrays to torch tensors and send to device
            X_train_t = torch.tensor(X_train, dtype=torch.float32)
            y_train_t = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
            X_val_t = torch.tensor(X_val, dtype=torch.float32)
            y_val_t = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)
            X_test_t = torch.tensor(X_test, dtype=torch.float32)
            y_test_t = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

            train_dataset = TensorDataset(X_train_t, y_train_t)
            train_loader = DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )

            val_dataset = TensorDataset(X_val_t, y_val_t)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

            test_dataset = TensorDataset(X_test_t, y_test_t)
            test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
            logging.info("Data loaders created successfully.")

            # Training loop
            logging.info("Starting training loop...")
            train_loss_history = []
            val_loss_history = []
            loop = tqdm(range(epochs), desc="Training Model", unit="epoch")
            for epoch in loop:
                mlmodel.train()
                train_loss = 0.0

                for X_batch, y_batch in train_loader:
                    X_batch, y_batch = X_batch.to(device), y_batch.to(device)

                    optimizer.zero_grad()
                    outputs = mlmodel(X_batch)
                    loss = loss_fn(outputs, y_batch)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item() * X_batch.size(0)

                # Average training loss
                train_loss /= len(train_loader.dataset)
                train_loss_history.append(train_loss)

                # Validation loss
                mlmodel.eval()
                with torch.no_grad():
                    val_outputs = mlmodel(X_val_t.to(device))
                    val_loss = loss_fn(val_outputs, y_val_t.to(device)).item()
                    val_loss_history.append(val_loss)

                if (epoch + 1) % 20 == 0:  # Log every 20 epochs
                    tqdm.write(
                        f"Epoch [{epoch + 1}/{epochs}], Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}"
                    )
            if explainability:
                try:
                    if device.type == "cpu":
                        X_train_torch = torch.from_numpy(X_train).float()
                        X_val_torch = torch.from_numpy(X_val).float()
                    else:
                        X_train_torch = torch.from_numpy(X_train).float().to(device)
                        X_val_torch = torch.from_numpy(X_val).float().to(device)
                    explainer = shap.GradientExplainer(mlmodel, X_train_torch)
                    mlmodel.train()  # Ensure model is in training mode for SHAP
                    shap_values = explainer.shap_values(X_val_torch)
                    logging.info("SHAP values calculated successfully.")
                    # Plot SHAP values
                    shap_values = shap_values.squeeze(-1)
                    # Get feature importance per sample
                    feature_importance_per_sample = np.mean(np.abs(shap_values), axis=1)
                    # Get time importance per sample
                    time_importance_per_sample = np.mean(np.abs(shap_values), axis=2)

                    # Plot feature importance
                    smoothed_features = moving_average(
                        feature_importance_per_sample, smooth_window_size
                    )
                    downsampled_features, downsampled_indices = downsample(
                        arr=smoothed_features, num_points=sample_size
                    )
                    # sort downsampled in descending order by mean and rearrange order of the input_cols as following
                    mean_importance = np.mean(downsampled_features, axis=0)
                    sorted_indices = np.argsort(mean_importance)[::-1]
                    downsampled_features = downsampled_features[:, sorted_indices]
                    input_cols = [input_cols[i] for i in sorted_indices]

                    plt.figure(figsize=(12, 6))
                    # plot with different line styles
                    line_count = 0

                    for f in range(downsampled_features.shape[1]):
                        if (
                            n_features_importance
                            and line_count >= n_features_importance
                        ):
                            continue
                        if use_markers:
                            color = COLOR_MAP[
                                list(COLOR_MAP.keys())[line_count % len(COLOR_MAP)]
                            ]
                            plt.plot(
                                downsampled_indices,
                                downsampled_features[:, f],
                                label=f"{input_cols[f]}",
                                color=color["color"],
                                linestyle=color["linestyle"],
                                marker=color["marker"],
                                linewidth=0.5,
                                markersize=3,
                            )
                        else:
                            plt.plot(
                                downsampled_indices,
                                downsampled_features[:, f],
                                label=f"{input_cols[f]}",
                            )
                        line_count += 1
                    plt.xlabel("Sample Index")
                    plt.ylabel("Mean |SHAP Value|")
                    plt.title("Feature Importance Over Samples")
                    plt.legend()
                    if plot_path:
                        if not os.path.exists(plot_path):
                            os.makedirs(plot_path)
                        file_path = f"{plot_path}/{run_name}_feature_importance.{image_extension}"
                        plt.savefig(file_path, bbox_inches="tight")
                        if mlflow_enable:
                            mlflow.log_artifact(file_path)
                        logging.info(f"Plot saved to {file_path}")
                    plt.show()
                except Exception as e:
                    logging.error(f"Error plotting feature importance: {e}")
                    logging.info(traceback.format_exc())

                # Plot time importance
                try:
                    smoothed_time = moving_average(
                        time_importance_per_sample, smooth_window_size
                    )
                    downsampled_time, downsampled_indices = downsample(
                        arr=smoothed_time, num_points=sample_size
                    )

                    plt.figure(figsize=(12, 6))
                    line_count = 0
                    for t in range(downsampled_time.shape[1]):
                        if use_markers:
                            color = COLOR_MAP[
                                list(COLOR_MAP.keys())[line_count % len(COLOR_MAP)]
                            ]
                            plt.plot(
                                downsampled_indices,
                                downsampled_time[:, t],
                                label=f"Time Step {int(t - history_size / 2)}",
                                color=color["color"],
                                linestyle=color["linestyle"],
                                marker=color["marker"],
                                linewidth=0.5,
                                markersize=3,
                            )
                        else:
                            plt.plot(
                                downsampled_indices,
                                downsampled_time[:, t],
                                label=f"Time Step {t}",
                            )
                        line_count += 1
                    plt.xlabel("Sample Index")
                    plt.ylabel("Mean |SHAP Value|")
                    plt.title("Time Step Importance Over Samples")
                    plt.legend()
                    if plot_path:
                        if not os.path.exists(plot_path):
                            os.makedirs(plot_path)
                        file_path = f"{plot_path}/{run_name}_time_step_importance.{image_extension}"
                        plt.savefig(file_path, bbox_inches="tight")
                        if mlflow_enable:
                            mlflow.log_artifact(file_path)
                        logging.info(f"Plot saved to {file_path}")
                    plt.show()
                    logging.info("Explainability analysis completed successfully.")
                except Exception as e:
                    logging.error(f"Error explaining time step importance: {e}")
                    logging.info(traceback.format_exc())
            # Evaluate model
            try:
                mlmodel.eval()
                with torch.no_grad():
                    test_outputs = mlmodel(X_test_t.to(device))
                    test_loss = loss_fn(test_outputs, y_test_t.to(device)).item()
                    test_outputs = test_outputs.cpu().numpy()
                    y_test_t = y_test_t.cpu().numpy()
                    y_test_t = y_test_t.reshape(-1, 1)
                    test_outputs = y_scaler.inverse_transform(test_outputs)
                    y_test_t = y_scaler.inverse_transform(y_test_t)
                    # Calculate metrics
                    test_mae = np.mean(np.abs(y_test_t - test_outputs))
                    test_mse = np.mean(np.square(y_test_t - test_outputs))
                    test_rmse = np.sqrt(test_mse)
                    test_mape = (
                        np.mean(np.abs(y_test_t - test_outputs) / y_test_t) * 100
                    )
                    test_r2 = 1 - (
                        np.sum((y_test_t - test_outputs) ** 2)
                        / np.sum((y_test_t - np.mean(y_test_t)) ** 2)
                    )

                    if plot:
                        plt.figure(figsize=(12, 6))
                        plt.plot(y_t_index, y_test_t, label="True Values", color="blue")
                        plt.plot(
                            y_t_index,
                            test_outputs,
                            label="Predicted Values",
                            color="red",
                        )
                        plt.title("LSTM Model Predictions vs True Values")
                        plt.xlabel("Time Steps")
                        plt.ylabel(f"{output_col}")
                        plt.legend()
                        if plot_path:
                            if not os.path.exists(plot_path):
                                os.makedirs(plot_path)
                            file_path = f"{plot_path}/{run_name}_test_prediction.{image_extension}"
                            plt.savefig(file_path, bbox_inches="tight")
                            if mlflow_enable:
                                mlflow.log_artifact(file_path)
                            logging.info(f"Plot saved to {file_path}")
                        plt.show()

                # plot training and validation loss
                if plot:
                    plt.figure(figsize=(12, 6))
                    plt.plot(train_loss_history, label="Train Loss", color="blue")
                    plt.plot(val_loss_history, label="Val Loss", color="red")
                    plt.title("LSTM Model Training and Validation Loss")
                    plt.xlabel("Epochs")
                    plt.ylabel("Loss")
                    plt.legend()
                    if plot_path:
                        if not os.path.exists(plot_path):
                            os.makedirs(plot_path)
                        file_path = f"{plot_path}/{run_name}_train_validation_loss.{image_extension}"
                        plt.savefig(file_path, bbox_inches="tight")
                        if mlflow_enable:
                            mlflow.log_artifact(file_path)
                        logging.info(f"Plot saved to {file_path}")
                    plt.show()

            except Exception as e:
                logging.error(f"Error evaluating model: {e}")
                logging.info(traceback.format_exc())

            input_example = np.array(X_test[:1], dtype=np.float32)
            raw_input_example = np.array(X_t[:1], dtype=np.float32)
            mlmodel = mlmodel.to("cpu")

            if mlflow_enable:
                try:
                    mlflow.log_metric("test_loss", test_loss)
                    mlflow.log_metric("test_mae", test_mae)
                    mlflow.log_metric("test_mse", test_mse)
                    mlflow.log_metric("test_rmse", test_rmse)
                    mlflow.log_metric("test_mape", test_mape)
                    mlflow.log_metric("test_r2", test_r2)

                    try:
                        joblib.dump(
                            {"input": x_scalers, "output": y_scaler}, SCALER_PATH
                        )
                        mlflow.pyfunc.log_model(
                            artifact_path=WRAPPED_MODEL,
                            python_model=MLModelWithScaler(
                                model=mlmodel,
                                scalers={"input": x_scalers, "output": y_scaler},
                            ),
                            artifacts={
                                "scalers": SCALER_PATH,
                                "input_cols": INPUT_COLS_PATH,
                            },
                            input_example=raw_input_example,
                        )
                        # remove redundant files
                        if os.path.isfile(SCALER_PATH):
                            os.remove(SCALER_PATH)
                        if os.path.isfile(INPUT_COLS_PATH):
                            os.remove(INPUT_COLS_PATH)
                    except Exception as e:
                        logging.warning(f"Error logging model artifacts: {e}")
                        logging.info(traceback.format_exc())
                except Exception as e:
                    logging.warning(f"Error logging model artifacts and metrics: {e}")
                    logging.info(traceback.format_exc())

            return {
                "train_loss": train_loss_history,
                "val_loss": val_loss_history,
                "test_loss": test_loss,
                "test_mae": test_mae,
                "test_mse": test_mse,
                "test_rmse": test_rmse,
                "test_mape": test_mape,
                "test_r2": test_r2,
                "ml_model": mlmodel,
                "input_example": input_example,
            }

    except Exception as e:
        logging.error(f"Error during training and evaluation setup: {e}")
        logging.error(traceback.format_exc())
        return None


def mlflow_run(
    df: pd.DataFrame,
    run_config: RunConfig,
    experiment_name: str,
    run_name: str,
    explainability: bool = False,
    plot_path: str = None,
    interpolate_outliers: bool = False,
    image_extension: str = "svg",
):
    try:
        # train and evaluate ML models
        training_result = train_and_evaluate(
            df=df,
            run_config=run_config,
            explainability=explainability,
            plot_path=plot_path,
            run_name=run_name,
            mlflow_enable=True,
            interpolate_outliers=interpolate_outliers,
            image_extension=image_extension,
            experiment_name=experiment_name,
        )
        test_loss = training_result.get("test_loss", -1)
        test_mae = training_result.get("test_mae", -1)
        test_mse = training_result.get("test_mse", -1)
        test_rmse = training_result.get("test_rmse", -1)
        test_mape = training_result.get("test_mape", -1)
        test_r2 = training_result.get("test_r2", -1)
        # ml_model = training_result.get("ml_model", None)
        # input_example = training_result.get("input_example", None)
        print(f"Test Loss: {test_loss:.6f}")
        print(f"Test MAE: {test_mae:.6f}")
        print(f"Test MSE: {test_mse:.6f}")
        print(f"Test RMSE: {test_rmse:.6f}")
        print(f"Test MAPE: {test_mape:.6f}%")
        print(f"Test R2: {test_r2:.6f}")
        return training_result
    except Exception as e:
        logging.error(f"Error during MLflow run setup: {e}")
        logging.error(traceback.format_exc())
        return None
