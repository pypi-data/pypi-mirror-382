# This module provides utilities and useful functions for time series data processing, model training, and evaluation.

## 1. Data Processing for Time Series
- Load data from CSV files
    - `load_csv_to_dataframe`: import from `gfa_ml.lib.utils`
        - The function loads a CSV file from the specified file path into a pandas DataFrame. Example usage:
          ```python
          df = load_csv_to_dataframe("path/to/file.csv")
          ```
        - More examples can be found in the [unit tests](../../test/unit_test/data_model/metric_report.ipynb).
- Define the Metric specification
    - Each metric need to be defined with the following attributes:
        - `metric_name`: The name of the metric.
        - `en_description`: A brief description of the metric in English (optional).
        - `fi_description`: A brief description of the metric in Finnish (optional).
        - `column_name`: The name of the column in the DataFrame to which the metric applies.
        - `display_name`: The name to be displayed in reports following snake_case, and will be used as the new column name in the DataFrame for better readability (optional - recommended).
        - `unit`: The unit of measurement for the metric (optional).
        - `stage`: The stage of the production pipeline where the metric is measured (optional).
        - `tag`: A list of tags associated with the metric, or sensor that measure the metric (optional).
        - `measurement_method`: The method used to measure the metric, e.g., continuous, calculative, or lab-measurement (optional).
        - `metric_type`: The type of the metric, e.g., control parameters, quality measurements (optional).
        - `smoothing_function`: The function used to smooth the metric values. This will be used in later processing steps.
        - Example in YAML:
        ```yaml
        metric_1:
            column_name: VALKAISUN SYÖTTÖ
            display_name: d0_input_bleaching_throughput
            en_description: Bleaching feed
            fi_description: VALKAISUN SYÖTTÖ
            measurement_method: continuous
            metric_type: control_parameter
            metric_name: metric_10
            stage: D0
            sort: 3
            tag: 643FC601.MES
            unit: l/s
            smoothing_function:
                function_name: moving_average
                smoothing_param:
                smoothing_function_type: moving_average
                window_size: 25
                min_periods: 1
                smoothing_type: mean
        ```
    - Multiple `Metric` specification can be load from a YAML file using the `load_metrics` function from `gfa_ml.lib.common`. This function return a dictionary `Dict[str, Metric]`.
    - With metric specifications save in YAML with multiple stages, use `load_multi_stage_metrics` function. This function also returns a dictionary `Dict[str, Dict[str, Metric]]`.
        - Example of multi-stage metric specification in YAML
        ```yaml
        D0:
            metric_1:
                column_name: VALKAISUN SYÖTTÖ
                display_name: d0_input_bleaching_throughput
                ...
        ```
- Rename the column: Because the column names in the raw data may not convenience for programming (e.g., they may contain spaces or special characters), it is recommended to rename the columns to a more suitable format (e.g., snake_case) before processing the data.
Example can be found in the [unit tests](../../test/unit_test/data_model/metric_report.ipynb).

- Normalize time column: The time column in the raw data may not be in a suitable format for analysis. It is recommended to normalize the time column to a consistent format (e.g., minutes) before processing the data.
    - Use the function `normalize_time_column` from `gfa_ml.lib.common`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `time_column`: the name of the time column in the DataFrame.
        - `norm`: the type of normalization to apply. It must be in enum `gfa_ml.data_model.data_type.TimeNormalizationType`. Options include:
            - `ZERO_BASE_NORM`: Normalize the time column to start from zero.
            - `MIN_MAX_NORM`: Normalize the time column to a range between 0 and 1.
            - `STANDARD_NORM`: Normalize the time column to have a mean of 0 and a standard deviation of 1.
        - `unit`: the unit to convert the time column to. It must be in enum `gfa_ml.data_model.data_type.TimeUnit`. Options include:
            - `SECONDS`
            - `MINUTES`
            - `HOURS`
            - `DAYS`
    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
        data_df = normalize_time_column(data_df, time_column="Time", norm=TimeNormalizationType.ZERO_BASE_NORM, unit=TimeUnit.MINUTES)
        ```
    - Result: data from string datetime format e.g., "2025-09-01 22:04:20" to time normalized to seconds/minutes/hours (int/float numbers).

- Evaluate the time series data of individual metrics: from the metric specifications, we can apply the preliminary evaluation steps to the time series data in the DataFrame using the `evaluate_metric_from_df` function from `gfa_ml.lib.common`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `metric_name`: the name of the metric to evaluate (must match the display_name in the metric specification/column name).
        - `save_path`: the path to save the evaluation results.
        - Other optional parameters can be included:
            - `index_col`: for estimating some statistics based on the DataFrame index.
            - `remove_zeros`: for removing zero values from the DataFrame before estimating some specific statistics, default is True.
            - `remove_inf`: for removing infinite values from the DataFrame before estimating some specific statistics, default is True.
            - `remove_negatives`: for removing negative values from the DataFrame before estimating some specific statistics, default is True.
            - `remove_nans`: for removing NaN values from the DataFrame before estimating some specific statistics, default is True.
            - `start_row`: for specifying the starting row for evaluation, default is 0.
            - `end_row`: for specifying the ending row for evaluation, default is -1 (last row).
            - `n_rows`: for specifying the number of rows to evaluate, default is None (all rows).
            - `n_percent`: for specifying the percentage of rows to evaluate, default is None (all rows).
            - `start_percent`: for specifying the starting percentage of rows for evaluation, default is None, starting at 0%.

    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
            evaluate_metric_from_df(data_df, metric_name=metric.display_name, save_path="./data_file/")
        ```

- Visualize the time series data: This step is for better understanding the trends and patterns in the data. You can use the function `plot_dataframe` from `gfa_ml.lib.common`.
    - This function will take input as:
        - `dataframe`: a pandas DataFrame containing the time series data.
        - `title`: a string representing the title of the plot.
        - `x_col`: a string representing the series data for the x-axis.
        - `y_col`: representing the series data for the y-axis. It can be a single column name or a list of column names.
        - `xlabel`: a string representing the label for the x-axis.
        - `ylabel`: a string representing the label for the y-axis.
        - Other optional parameters:
            - `plot_path`: a string representing the path to save the plot.
            - `start_row`: an integer representing the starting row for the plot, default is 0.
            - `end_row`: an integer representing the ending row for the plot, default is -1 (last row).
            - `chart_type`: a string representing the type of chart to plot (default is line chart). `ChartType` must be in enum `gfa_ml.data_model.data_type.ChartType`.
            - `fig_width`: an integer representing the width of the figure (default is 10).
            - `fig_height`: an integer representing the height of the figure (default is 6).
            - `save_plot`: a boolean indicating whether to save the plot (default is False).
            - `remove_zeros`: a boolean indicating whether to remove zero values (default is True).
            - `remove_inf`: a boolean indicating whether to remove infinite values (default is True).
            - `remove_negatives`: a boolean indicating whether to remove negative values (default is True).
            - `remove_nans`: a boolean indicating whether to remove NaN values (default is True).
            - `start_percent`: a float representing the starting percentage of rows for evaluation (default is None, starting at 0%).
            - `n_percent`: a float representing the percentage of rows to evaluate (default is None, all rows).
            - `n_rows`: an integer representing the number of rows to evaluate (default is None, all rows).
            - `metrics`: providing additional metrics for evaluation.
            - `include_tag`: a boolean indicating whether to include the metric tag in the legend (default is False).
    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
            plot_dataframe(
                data_df,
                title=f"Plot of {metric.display_name} over Time",
                x_col="Time",
                y_col=metric.display_name,
                xlabel="Time (minutes)",
                ylabel=metric.display_name,
                plot_path=data_plot_path,
                start_row=0,
                end_row=-1,
                chart_type=ChartType.LINE,
                fig_width=10,
                fig_height=6,
                save_plot=False,
                metrics=metric,
                include_tag=True,
            )
        ```
    - Other chart types:
        - `ChartType.BAR`: Bar chart
        - `ChartType.SCATTER`: Scatter plot
        - `ChartType.HISTOGRAM`: Histogram (recommended for distribution of values)
        - To do: implement other chart types
- Smooth the data frame based on the metric's smoothing parameters
    - Use the function `smooth_data_frame` from `gfa_ml.lib.data_processing`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `metric_dict`: a dictionary of metrics loaded from the YAML file using `load_metrics` function.
        - `inplace`: a boolean indicating whether to modify the DataFrame in place (default is True). If the `inplace` is False, the column will not be modified, but new columns with smoothed values will be added. The new column will be named `f"{column_name}_interpolated"`. If `inplace` is True, the original column will be replaced with the smoothed values. **Note** `inplace` is applied to column not dataframe, so the function will always return completely new dataframe.
        - For training dataset, we can use `inplace=True` to replace the original columns. For testing dataset, we can use `inplace=True` to keep the original columns without interpolated values.
    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
        new_df = smooth_data_frame(data_df, metric_dict=metric_dict)
        ```
    - Result: a new DataFrame with smoothed values based on the smoothing parameters defined in the metric specifications. The visualization of the smoothed data can be done using the `plot_dataframe` function.

- Save the smoothed DataFrame to a file
    - Use the function `save_dataframe_to_csv` from `gfa_ml.lib.utils`.
    - This function will take input as:
        - `dataframe`: a pandas DataFrame.
        - `file_path`: the file path to save the DataFrame (e.g., "./data_file/smoothed_data.csv").
        - `mode`: the file mode (default is "w" for write). Other options include "a" for append.
        - `header`: a boolean indicating whether to write the header (default is True).
    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
        save_dataframe_to_csv(new_df, file_path="./data_file/smoothed_data.csv")
        ```
**Important** With these step, the new data frame is smoothed and have `time` normalization applied.

- Remove outliers using sliding z-score
    - Use the function `remove_outliers_sliding_zscore` from `gfa_ml.lib.data_processing`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `window`: an integer representing the window size for the rolling calculation (default is 100).
        - `threshold`: a float value representing the z-score threshold for outlier detection (default is 3.0).
        - `cols`: a list of column names to apply the outlier removal (default is None, which means all numeric columns will be processed).
    - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
        cleaned_df = remove_outliers_sliding_zscore(new_df, window=10, threshold=3.0, cols=None)
        ```
- Remove outliers using quantile via sliding window
    - Use the function `remove_outliers_sliding_window` from `gfa_ml.lib.data_processing`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `lower_threshold`: a float value representing the lower quantile threshold for outlier detection (default is 0.1).
        - `upper_threshold`: a float value representing the upper quantile threshold for outlier detection (default is 0.9).
        - `cols`: a list of column names to apply the outlier removal (default is None, which means all numeric columns will be processed).

- Interpolate outlier value using sliding window and z-score or IQR
    - Use the function `interpolate_outliers_sliding` from `gfa_ml.lib.data_processing`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `window`: an integer representing the window size for the rolling calculation (default is 100).
        - `threshold`: a float value representing the z-score threshold for outlier detection (default is 3.0).
        - `method`: a string representing the interpolation method to use ("z-score" or "iqr", default is "zscore").
        - `cols`: a list of column names to apply the interpolation (default is None, which means all numeric columns will be processed).
        - `inplace`: a boolean indicating whether to modify the DataFrame in place (default is False).


- Extract dataframe: In general, a ML model cannot learn the underlying patterns from the raw data entirely. Therefore, we need to extract specific parts of the data that have specific patterns, where the model can focus on learning those patterns more effectively.
    - Use function `extract_dataframe` from `gfa_ml.lib.data_processing`.
    - This function will take input as:
        - `df`: a pandas DataFrame containing the time series data.
        - `remove_zeros`: a boolean indicating whether to remove zero values (default is False).
        - `remove_inf`: a boolean indicating whether to remove infinite values (default is False).
        - `remove_negatives`: a boolean indicating whether to remove negative values (default is False).
        - `remove_nans`: a boolean indicating whether to remove NaN values (default is False).
        - `start_row`: an integer representing the starting row for extraction (default is 0).
        - `end_row`: an integer representing the ending row for extraction (default is None, which means all rows will be extracted).
        - `n_rows`: an integer representing the number of rows to extract (default is None, which means all rows will be extracted).
        - `n_percent`: a float representing the percentage of rows to extract (default is None, which means all rows will be extracted).
        - `start_percent`: a float representing the starting percentage of rows to extract (default is None - start at 0%).
        - Example use (from [unit test](../../test/unit_test/data_model/metric_report.ipynb)):
        ```python
        extract_df = extract_dataframe(data_df, start_row=0, n_rows=10)
        ```



## 2. [Utils](../gfa_ml/lib/utils.py) (utilities)
Contains utility functions that do not use the data model abstractions.
- `load_yaml`: Load a YAML file and return its content as a dictionary.
```text
Args:
    path (str): The path to the YAML file.
Returns:
    dict: The content of the YAML file as a dictionary.
```
- `save_yaml`: Save a dictionary to a YAML file. If the directory does not exist, it will be created.
```text
Args:
    dictionary (dict): The dictionary to save.
    path (str): The path to the YAML file.
```
- `load_json`: Load a JSON file and return its content as a dictionary.
```text
Args:
    path (str): The path to the JSON file.
Returns:
    dict: The content of the JSON file as a dictionary.
```
- `save_json`: Save a dictionary to a JSON file. If the directory does not exist, it will be created.
```text
Args:
    dictionary (dict): The dictionary to save.
    path (str): The path to the JSON file.
```
- `load_csv_to_dataframe`: Load a CSV file into a Pandas DataFrame.
```text
Args:
    file_path (str): The path to the CSV file.
Returns:
    pd.DataFrame: A DataFrame containing the data from the CSV file.
```
- `save_dataframe_to_csv`: Save a Pandas DataFrame to a CSV file. If the directory does not exist, it will be created.
```text
Args:
    df (pd.DataFrame): The DataFrame to save.
    file_path (str): The path to the CSV file.
    mode (str): The mode to open the file in ('w' for write, 'a' for append). Default is 'w'.
```
- `get_outer_directory`: Get the outer directory of the current directory by going up a specified number of levels.
```text
Args:
    current_dir (str or None): The current directory path. If None, the current working directory will be used.
    levels_up (int): The number of levels to go up in the directory structure. Default is 1.

Returns:
    str: The path to the outer directory.   
```


## 3. Other [Common](../gfa_ml/lib/common.py) functions using the data model abstractions
The `lib/common.py` module contains common functions that utilize the data model abstractions defined in the `gfa_ml.data_model` package.
- `convert_time_column`: Converts a time column from a Pandas DataFrame from datatime string to integer number of seconds/minute/hours.
```text
Args:
    df (pd.DataFrame): The DataFrame containing the time column (should be master data).
    time_column (str): The name of the time column to convert.
    unit (TimeUnit): The time unit to convert to.

Returns:
    pd.DataFrame: The DataFrame with the converted time column.
```
- `normalize_time_column`: Normalize the time column of a DataFrame to a specified time unit.
```text
Args:
    df (pd.DataFrame): The DataFrame containing the time column (should be master data).
    time_column (str): The name of the time column to normalize.
    unit (TimeUnit): The time unit to normalize to.

Returns:
    pd.DataFrame: The DataFrame with the normalized time column.
```
- `gen_uml_diagram`: Generate a UML diagram for the given class object.
```text
Args:
    class_object: The class object to generate the UML diagram.
    format: The format of the output file (default is "png").
    output_file: The name of the output file (default is "uml_diagram").
    graph_attributes: The attributes to apply to the graph (default is None).
    docs: If True, the output file will be saved in the docs/img directory.
```

- `load_metrics`: Load metrics from a YAML file and return them as a dictionary. The structure of the Yaml file should be as follows:
```yaml
<metrics_name>: <metric_as_dictionary>
```
Where `<metric_as_dictionary>` is a dictionary representation of the `Metric` class.

```text
Args:
    file_path (str): The path to the YAML file containing the metrics.

Returns:
    Dict[str, Metric]: A dictionary mapping metric names to Metric objects.
```
- `load_multi_stage_metrics`: Load multi-stage metrics from a list of YAML files and return them as a dictionary. The structure of the YAML files should be as follows:
```yaml
<stage_name>:
  <metrics_name>: <metric_as_dictionary>
```
Where `<metric_as_dictionary>` is a dictionary representation of the `Metric` class.
```text
Args:
    file_paths (List[str]): A list of paths to the YAML files containing the multi-stage metrics.
Returns:
    Dict[str, Metric]: A dictionary mapping metric names to Metric objects.
```

-`plot_dataframe`: Plot a DataFrame using the specified parameters and save the plot to a file.
```text
Args:
    dataframe: DataFrame, data to plot.
    title: str, Title of the plot.
    x_col: Union[str, None], Name of the column to use for the x-axis, if None, the index will be used.
    y_col: Union[str, list], Name of the column(s) to use for the y-axis.
    xlabel: str, Label for the x-axis.
    ylabel: str, Label for the y-axis.
    plot_path: str, Path to save the plot.
    start_row: int, Starting row index for the plot.
    end_row: int, Ending row index for the plot. Can be negative to indicate counting from the end.
    chart_type: ChartType = ChartType.LINE, Type of chart to plot (default is LINE).
    fig_width: int = 10, Width of the figure in inches (default is 10).
    fig_height: int = 6, Height of the figure in inches (default is 6).
    plot: bool = False, Whether to plot the data or not.
```
