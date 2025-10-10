# Data Model
This module provides abstract classes for the whole library.

- [Common](common.py): Implements common data model abstractions.
    - `SmoothingParam`: the data model class for smoothing parameters.
        - `MovingAverageSmoothingParam`: inherits from `SmoothingParam`, and will be used for moving average smoothing.
        - To do: implement other smoothing parameter types.
    - `SmoothingFunction`: the data model class for smoothing functions. That need `function_name`, `description` (optional), and `smoothing_param`. ***Note:*** The unit test for `SmoothingFunction` and `SmoothingParam` can be found in `tests/unit_test/data_model/smoothing_data.ipynb`.



    - `Metric`: the data model class for parameters and measures in the data in general.
        - `metric_name`: name of the metric (can be anything, e.g., in Finnish)
        - `column_name`: name of the column in the raw data (it can be Finnish and not suitable for data processing)
        - `unit`: unit of measurement (e.g., "kg", "m", "s")
        - `stage`: stage where the data is measured (e.g., "D0", "OEP")
        - `tag`: unique tag of the metrics/sensors
        - `measurement_method`: method used for measurement (e.g., "continuous", "lab", "calculative)
        - `sort`: (unknown in Stora Enso)
        - `en_description`: English description of the metric
        - `fi_description`: Finnish description of the metric
        - `display_name`: display name used for rename the columns for better processing and reference
        - `metric_type`: type of the metric (e.g., "control parameter", "quality measurement")
        - `smoothing_function`: smoothing function applied to the time series of this metric.
        - How to load a metric: 
            - Load from dictionary: `metric = Metric.from_dict(metric_dict)`
            - Load from file: `metric = load_metrics(file_path)` (import `load_metrics` from `gfa_ml.lib.common`)

    - `StageInfo`: the data model class for stage information.
        - `stage_name`: name of the stage (e.g., "D0", "OEP")
        - `input_parameters`: dictionary of input parameters (type: `Dict[str,Metric]`)
        - `quality_indicators`: dictionary of quality indicators (type: `Dict[str,Metric]`)
        - `control_parameters`: dictionary of control parameters (type: `Dict[str,Metric]`)
    - `MultiStageInfo`: the data model class for multi-stage information.
        - `stages`: list of stages (type: `Dict[str,StageInfo]`)

    - `MetricReport`: the data model class for metric reports in the data. **Important: From the metric report, we understand more about the data and decide what to do with the metric.**
        - `metric_name`: name of the metric
        - `total_count`: total number of measurements included in the data (type: `int`)
        - `missing_count`: number of missing measurements included in the data (type: `int`)
        - `missing_rate`: ratio of the missing measurements in the data (type: `float`)
        - `zero_count`: number of measurements with zero values included in the data (type: `int`)
        - `zero_rate`: ratio of the zero measurements in the data (type: `float`)
        - `min_value`: minimum value of the measurements included in the data (type: `float`)
        - `max_value`: maximum value of the measurements included in the data (type: `float`)
        - `mean_value`: mean value of the measurements included in the data (type: `float`)
        - `median_value`: median value of the measurements included in the data (type: `float`)
        - `standard_deviation`: standard deviation of the measurements included in the data (type: `float`)
        - `variance`: variance of the measurements included in the data (type: `float`)
        - `quantile_25th`: 25th percentile of the measurements included in the data (type: `float`)
        - `quantile_75th`: 75th percentile of the measurements included in the data (type: `float`)
        - `interquartile_range`: interquartile range of the measurements included in the data (type: `float`)
        - `skewness`: skewness of the measurements included in the data (type: `float`)
        - `kurtosis`: kurtosis of the measurements included in the data (type: `float`)
        - `positive_count`: number of measurements with positive values included in the data (type: `int`)
        - `negative_count`: number of measurements with negative values included in the data (type: `int`)
        - `positive_rate`: ratio of the positive measurements in the data (type: `float`)
        - `negative_rate`: ratio of the negative measurements in the data (type: `float`)
        - `mean_measurement_interval`: mean measurement interval of the measurements included in the data (type: `float`)
        - `min_measurement_interval`: minimum measurement interval of the measurements included in the data (type: `float`)
        - `max_measurement_interval`: maximum measurement interval of the measurements included in the data (type: `float`)
        - The metric report will be generated by using `evaluate_metric_from_df` (import from `gfa_ml.lib.common`). Example: in `test/unit_test/data_model/metric_report_test.ipynb`


    - `DataConfig`: the data model class for data configuration used in the ml model training. It will be part of the experiment run configuration
        