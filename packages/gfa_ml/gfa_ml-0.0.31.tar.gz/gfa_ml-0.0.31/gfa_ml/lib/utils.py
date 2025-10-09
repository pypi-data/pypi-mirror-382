import os
from typing import Union
import logging
import traceback
import json
import pandas as pd
import yaml
from typing import Literal
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def save_yaml(
    dictionary: dict,
    path: str,
    sort_keys: bool = False,
    allow_unicode: bool = True,
    default_flow_style: bool = False,
):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as file:
            yaml.dump(
                dictionary,
                file,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=allow_unicode,
                Dumper=NoAliasDumper,
            )
    except Exception as e:
        logging.error(f"Error saving YAML file {path}: {e}")
        logging.debug(traceback.format_exc())


def load_yaml(path: str) -> dict:
    try:
        if not os.path.exists(path):
            logging.error(f"YAML file {path} does not exist.")
            return {}
        with open(path, "rb") as file:
            content = yaml.load(file, Loader=yaml.FullLoader)
        return content
    except Exception as e:
        logging.error(f"Error loading YAML file {path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def save_json(dictionary: dict, path: str):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as file:
            json.dump(dictionary, file)
    except Exception as e:
        logging.error(f"Error saving JSON file {path}: {e}")
        logging.debug(traceback.format_exc())


def load_json(path: str) -> dict:
    try:
        with open(path, "rb") as file:
            content = json.load(file)
        return content
    except Exception as e:
        logging.error(f"Error loading JSON file {path}: {e}")
        logging.debug(traceback.format_exc())
        return {}


def load_csv_to_dataframe(file_path: str) -> Union[pd.DataFrame, None]:
    """
    Loads a CSV file into a Pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: A DataFrame containing the data from the CSV file.
    """
    try:
        dataframe = pd.read_csv(file_path)
        logging.info(f"File {file_path} successfully loaded into a DataFrame.")
        return dataframe
    except Exception as e:
        logging.error(f"An error occurred while loading the file: {e}")
        return None


def save_dataframe_to_csv(
    dataframe: pd.DataFrame,
    file_path: str,
    mode: Literal["w", "x", "a"] = "w",
    header: bool = True,
) -> None:
    """
    Saves a Pandas DataFrame to a CSV file.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame to save.
    file_path (str): The path where the CSV file will be saved.
    """
    try:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        dataframe.to_csv(file_path, mode=mode, index=False, header=header)
        logging.info(f"DataFrame successfully saved to {file_path} in mode '{mode}'.")
    except Exception as e:
        logging.error(f"An error occurred while saving the DataFrame: {e}")


def get_outer_directory(
    current_dir: Union[str, None], levels_up: int = 1
) -> Union[str, None]:
    """
    Get the outer directory path by moving up a specified number of levels from the current directory.
    """
    try:
        if current_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        outer_dir = current_dir
        for _ in range(levels_up):
            outer_dir = os.path.dirname(outer_dir)
        return outer_dir
    except Exception as e:
        logging.error(f"Error getting outer directory: {e}")
        logging.debug(traceback.format_exc())
        return None


def moving_average(arr, window_size=10):
    try:
        # Pad start of array to keep same length
        if window_size < 1:
            window_size = 1
        if window_size > arr.shape[0]:
            logging.warning(
                f"Window size ({window_size}) exceeds input array length ({arr.shape[0]})."
            )
            window_size = arr.shape[0] // 20
        cumsum = np.cumsum(np.insert(arr, 0, 0, axis=0), axis=0)
        ma = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
        return ma
    except Exception as e:
        logging.error(f"Error calculating moving average: {e}")
        logging.error(traceback.format_exc())
        return None


def downsample(arr, num_points=200):
    try:
        if num_points < 1:
            num_points = 1
        if num_points > arr.shape[0]:
            logging.warning(
                f"Number of sampling points ({num_points}) exceeds input array length ({arr.shape[0]})."
            )
            num_points = arr.shape[0]
        # Downsample array along axis=0 to num_points points by uniform sampling
        indices = np.linspace(0, arr.shape[0] - 1, num_points).astype(int)
        return arr[indices], indices
    except Exception as e:
        logging.error(f"Error downsampling array: {e}")
        logging.error(traceback.format_exc())
        logging.error(
            f"Input array shape: {arr.shape}, Number of points requested: {num_points}"
        )
        return None, None
