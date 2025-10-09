import numpy as np
import pandas as pd
import logging
import traceback
from sklearn.preprocessing import MinMaxScaler
from gfa_ml.lib.default import (
    TRAIN_RATE,
    VALIDATION_RATE,
    DEFAULT_RETENTION_PADDING,
    DATA_INTERVAL_MINUTES,
)

from typing import Dict
from ..data_model.common import (
    MeasurementParameter,
    Metric,
    ControlParameter,
    InputSpecification,
)
from ..data_model.data_type import SmoothingFunctionType, SmoothingType

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def smooth_data_frame(
    df: pd.DataFrame, metric_dict: Dict[str, Metric], inplace: bool = True
) -> pd.DataFrame:
    """
    Apply smoothing to the DataFrame based on the metric definitions.
    """
    try:
        new_df = df.copy()
        for metric_name, metric in metric_dict.items():
            column_name = metric.display_name
            if inplace == False:
                new_col_name = f"{column_name}_interpolated"
                if new_col_name not in new_df.columns:
                    new_df[new_col_name] = new_df[column_name].copy()
                column_name = new_col_name
            if column_name not in new_df.columns:
                logging.warning(
                    f"Column '{column_name}' not found in DataFrame. Skipping smoothing for this metric."
                )
                continue
            if metric.smoothing_function:
                logging.info(
                    f"Smoothing column: {column_name} with {metric.smoothing_function.function_name}"
                )
                smooth_param = metric.smoothing_function.smoothing_param
                if (
                    smooth_param.smoothing_function_type
                    == SmoothingFunctionType.MOVING_AVERAGE
                ):
                    window_size = smooth_param.window_size
                    min_periods = smooth_param.min_periods
                    if smooth_param.smoothing_type == SmoothingType.MEDIAN:
                        new_df[column_name] = (
                            new_df[column_name]
                            .rolling(window=window_size, min_periods=min_periods)
                            .median()
                        )
                    elif smooth_param.smoothing_type == SmoothingType.MAX:
                        new_df[column_name] = (
                            new_df[column_name]
                            .rolling(window=window_size, min_periods=min_periods)
                            .max()
                        )
                    elif smooth_param.smoothing_type == SmoothingType.MIN:
                        new_df[column_name] = (
                            new_df[column_name]
                            .rolling(window=window_size, min_periods=min_periods)
                            .min()
                        )
                    elif smooth_param.smoothing_type == SmoothingType.MEAN:
                        new_df[column_name] = (
                            new_df[column_name]
                            .rolling(window=window_size, min_periods=min_periods)
                            .mean()
                        )
                else:
                    logging.warning(
                        f"Smoothing type {smooth_param.smoothing_function_type} is not yet implemented."
                    )
        return new_df
    except Exception as e:
        logging.error(f"Error occurred while smoothing data frame: {e}")
        logging.error(traceback.format_exc())
        return df


def extract_dataframe(
    df: pd.DataFrame,
    remove_zeros: bool = False,
    remove_inf: bool = False,
    remove_negatives: bool = False,
    remove_nans: bool = False,
    start_row: int = 0,
    end_row: int = -1,
    n_rows: int = None,
    n_percent: float = None,
    start_percent: float = None,
) -> pd.DataFrame:
    try:
        if start_row < 0 or start_row >= len(df):
            start_row = 0
            logging.warning("start_row is less than 0, setting to 0.")
        if start_percent is not None:
            start_row = int(len(df) * (start_percent / 100))
        if n_rows is not None:
            end_row = start_row + n_rows
        if n_percent is not None:
            end_row = start_row + int(len(df) * (n_percent / 100))
        if end_row > len(df):
            end_row = len(df)
            logging.warning(
                "end_row is greater than DataFrame length, setting to DataFrame length."
            )
        if end_row < 0:
            end_row = len(df) + end_row
            logging.warning("end_row is negative, setting to relative index.")

        process_df = df.iloc[start_row:end_row].copy()
        if remove_zeros:
            process_df = process_df[(process_df != 0).all(axis=1)]
        if remove_inf:
            process_df = process_df[
                (process_df != float("inf")).all(axis=1)
                & (process_df != float("-inf")).all(axis=1)
            ]
        if remove_negatives:
            process_df = process_df[(process_df >= 0).all(axis=1)]
        if remove_nans:
            process_df = process_df.dropna()
        logging.info(
            f"Extracted DataFrame from rows {start_row} to {end_row} with shape {process_df.shape}."
        )
        return process_df
    except Exception as e:
        logging.error(f"Error extracting DataFrame: {e}")
        logging.debug(traceback.format_exc())
        return pd.DataFrame()


def remove_outliers_sliding_window(
    df, window=100, upper_threshold=0.9, lower_threshold=0.1, cols: list = None
):
    try:
        clean_df = df.copy()
        if cols is None:
            cols = df.select_dtypes(include="number").columns
        for col in cols:
            mask = np.ones(len(df), dtype=bool)  # keep track of valid rows
            for i in range(len(df)):
                start = max(0, i - window // 2)
                end = min(len(df), i + window // 2)
                window_data = df[col].iloc[start:end]

                Q1 = window_data.quantile(lower_threshold)
                Q3 = window_data.quantile(upper_threshold)

                if not (Q1 <= df[col].iloc[i] <= Q3):
                    mask[i] = False
            clean_df = clean_df[mask]
        return clean_df
    except Exception as e:
        logging.error(f"Error removing outliers (sliding window): {e}")
        logging.info(traceback.format_exc())
        return df


def remove_outliers_sliding_zscore(
    df: pd.DataFrame, window: int = 100, threshold: float = 3.0, cols: list = None
):
    try:
        clean_df = df.copy()
        if cols is None:
            cols = df.select_dtypes(include="number").columns
        for col in cols:
            rolling_mean = df[col].rolling(window, center=True, min_periods=1).mean()
            rolling_std = df[col].rolling(window, center=True, min_periods=1).std()
            z_scores = (df[col] - rolling_mean) / rolling_std
            mask = np.abs(z_scores) <= threshold
            clean_df = clean_df[mask]
        return clean_df
    except Exception as e:
        logging.error(f"Error removing outliers (sliding z-score): {e}")
        logging.info(traceback.format_exc())
        return df


def interpolate_outliers_sliding(
    df: pd.DataFrame,
    window: int = 100,
    threshold: int = 3,
    method: str = "zscore",
    cols: list = None,
    inplace: bool = True,
):
    try:
        clean_df = df.copy()

        if cols is None:
            cols = clean_df.columns

        for col in cols:
            if inplace == False:
                new_col_name = f"{col}_interpolated"
                clean_df[new_col_name] = clean_df[col].copy()
                col = new_col_name
            if method == "zscore":
                rolling_mean = (
                    clean_df[col].rolling(window, center=True, min_periods=1).mean()
                )
                rolling_std = (
                    clean_df[col].rolling(window, center=True, min_periods=1).std()
                )
                z_scores = (clean_df[col] - rolling_mean) / rolling_std
                outliers = np.abs(z_scores) > threshold

            elif method == "iqr":
                rolling_q1 = (
                    clean_df[col]
                    .rolling(window, center=True, min_periods=1)
                    .quantile(0.25)
                )
                rolling_q3 = (
                    clean_df[col]
                    .rolling(window, center=True, min_periods=1)
                    .quantile(0.75)
                )
                iqr = rolling_q3 - rolling_q1
                lower = rolling_q1 - 1.5 * iqr
                upper = rolling_q3 + 1.5 * iqr
                outliers = (clean_df[col] < lower) | (clean_df[col] > upper)

            clean_df.loc[outliers, col] = np.nan

            clean_df[col] = clean_df[col].interpolate(method="linear").ffill().bfill()

        return clean_df
    except Exception as e:
        logging.error(f"Error interpolating outliers: {e}")
        logging.info(traceback.format_exc())
        return df


def remove_interpolated_values(df: pd.DataFrame, cols: list = None) -> pd.DataFrame:
    try:
        if cols is None:
            cols = df.columns
        for col in cols:
            interpolated_col = f"{col}_interpolated"
            null_indices = df[col].isna()
            # set value to null in interpolated column where original column is null
            df[interpolated_col] = df[interpolated_col].mask(null_indices)
        return df
    except Exception as e:
        logging.error(f"Error removing interpolated values: {e}")
        logging.info(traceback.format_exc())
        return df


def create_inference_input(
    df: pd.DataFrame,
    history_size: int,
    interval_minutes: int,
    input_spec: InputSpecification,
    trial_run: bool = False,
) -> np.ndarray:
    try:
        input_df = pd.DataFrame()
        window_size = history_size / interval_minutes
        window_size = int(window_size)
        for parameter in input_spec.specification.values():
            if isinstance(parameter, ControlParameter):
                if trial_run and parameter.trial_value is not None:
                    input_df[parameter.parameter_name] = parameter.trial_value
                else:
                    input_df[parameter.parameter_name] = parameter.current_value
            elif isinstance(parameter, MeasurementParameter):
                input_df[parameter.parameter_name] = (
                    df[parameter.column_name].head(window_size).copy()
                )
        return input_df.to_numpy().reshape(1, window_size, -1)
    except Exception as e:
        logging.error(f"Error creating inference input: {e}")
        logging.info(traceback.format_exc())
        return np.empty((1, window_size, 0))


def create_time_aware_sequences(
    df: pd.DataFrame,
    input_cols: list,
    output_col: str,
    history_size: int,
    index_col: str = None,
    retention_period: int = 10,
    retention_col: str = None,
    retention_padding: int = DEFAULT_RETENTION_PADDING,  # only apply for specific stage in stora enso
    column_extension: str = None,
    return_index: bool = False,
    interval_minutes: int = None,
    num_rows: int = None,
    min_rows: int = None,
):
    try:
        if num_rows is None:
            if interval_minutes is not None and interval_minutes > 0:
                num_rows = history_size // interval_minutes
            else:
                num_rows = history_size

        if column_extension is not None and (
            f"{output_col}_{column_extension}" in df.columns
        ):
            output_col = f"{output_col}_{column_extension}"
        internal_df = df.copy()
        if index_col:
            internal_df.set_index(index_col, inplace=True)
            internal_df.sort_values(by=index_col)

        # get index where the output column is not Nan
        valid_indices = internal_df[output_col].index[internal_df[output_col].notna()]

        # fill nan by interpolation
        for col_i in input_cols:
            if col_i != output_col:
                internal_df[col_i] = internal_df[col_i].interpolate(
                    method="linear", limit_direction="both"
                )
            else:
                # fill nan by forward fill
                internal_df[col_i] = internal_df[col_i].ffill()
                internal_df[col_i] = internal_df[col_i].bfill()

        X = []
        y = []
        X_index = []
        y_index = []

        min_index = internal_df.index.min()
        max_index = internal_df.index.max()
        # iterate index in valid_indices
        for index_i in valid_indices:
            output_value = internal_df.loc[index_i][output_col]
            if pd.isna(output_value):
                continue
            if retention_col in internal_df.columns:
                retention_time = (
                    internal_df.loc[index_i][retention_col] + retention_padding
                )
            else:
                retention_time = retention_period
                print(f"Using default retention time: {retention_time}")

            start_index = index_i - (retention_time + history_size)
            end_index = index_i - (retention_time)

            if start_index < min_index or end_index >= max_index:
                continue

            input_df = internal_df.loc[int(start_index) : int(end_index)][input_cols]
            if min_rows is not None and len(input_df) < min_rows:
                continue
            elif len(input_df) < num_rows:
                # to do: interpolate missing values
                continue
            elif len(input_df) > num_rows:
                # sampling num_rows from input_df
                input_df = input_df.iloc[-num_rows :]

            input_sequence = input_df.values

            if input_sequence.shape[0] == num_rows:
                X.append(input_sequence)
                y.append(output_value)
                y_index.append(index_i)
                X_index.append((start_index, end_index))
        if return_index:
            return np.array(X), np.array(y), np.array(X_index), np.array(y_index)
        return np.array(X), np.array(y)
    except Exception as e:
        logging.error(f"Error creating time-aware sequences: {e}")
        logging.error(traceback.format_exc())
        return None, None, None, None


def apply_scalers(X, y, x_scalers, y_scaler):
    try:
        X_norm = np.empty_like(X)
        for index, scaler in x_scalers.items():
            i = int(index)
            X_norm[:, :, i] = scaler.transform(X[:, :, i])
        y_norm = y_scaler.transform(y.reshape(-1, 1))
        return X_norm, y_norm
    except Exception as e:
        logging.error(f"Error applying scalers: {e}")
        logging.error(traceback.format_exc())
        return None, None


def normalize_sequences(X, y):
    try:
        n_features = X.shape[2]
        scalers = {}
        for i in range(n_features):
            scaler = MinMaxScaler()
            X[:, :, i] = scaler.fit_transform(X[:, :, i])
            scalers[i] = scaler

        y_scaler = MinMaxScaler()
        y = y_scaler.fit_transform(y.reshape(-1, 1)).flatten()
        logging.info("Sequences normalized successfully.")
        return X, y, scalers, y_scaler
    except Exception as e:
        logging.error(f"Error normalizing sequences: {e}")
        logging.error(traceback.format_exc())
        return X, y, {}, None


def split_time_series_data(
    X, y, train_ratio=TRAIN_RATE, validation_ratio=VALIDATION_RATE
):
    try:
        new_train_ratio = train_ratio / (train_ratio + validation_ratio)
        new_validation_ratio = validation_ratio / (train_ratio + validation_ratio)
        n = len(X)
        n_train = int(n * new_train_ratio)
        n_val = int(n * new_validation_ratio)

        X_train = X[:n_train]
        y_train = y[:n_train]

        X_val = X[n_train : n_train + n_val]
        y_val = y[n_train : n_train + n_val]

        logging.info(
            "Time series data split into train, validation, and test sets successfully."
        )
        return X_train, y_train, X_val, y_val
    except Exception as e:
        logging.error(f"Error splitting time series data: {e}")
        logging.error(traceback.format_exc())
        return None, None, None, None
