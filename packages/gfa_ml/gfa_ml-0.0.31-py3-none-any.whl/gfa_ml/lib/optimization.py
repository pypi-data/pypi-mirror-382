import optuna

from gfa_ml.data_model.data_type import ModelType, OptimizationObjective, OptunaSampler
from gfa_ml.data_model.common import (
    LSTMConfig,
    OutputConstraint,
    OutputQuality,
    TransformerConfig,
)
from gfa_ml.data_model.common import InputSpecification, ControlParameter
import pandas as pd
from gfa_ml.data_model.common import DataConfig
from gfa_ml.lib.data_processing import create_inference_input
from gfa_ml.lib.common import make_prediction
from gfa_ml.lib.serving import ModelServing
from gfa_ml.lib.training import mlflow_run
from gfa_ml.lib.utils import load_yaml
import logging
import traceback
import copy
import math
from gfa_ml.lib.constant import (
    DEFAULT_HIDDEN_NEURONS,
    DEFAULT_NUM_HIDDEN_LAYERS,
    DEFAULT_BATCH_SIZES,
    DEFAULT_LEARNING_RATES,
    DEFAULT_DROPOUT_RATES,
    DEFAULT_ACTIVATION_FUNCTIONS,
    DEFAULT_OPTIMIZERS,
    DEFAULT_LOSSES,
    DEFAULT_NHEADS,
    DEFAULT_DIM_FEEDFORWARDS,
    DEFAULT_D_MODELS,
)
from gfa_ml.data_model.common import RunConfig
import importlib
from gfa_ml.data_model.common import ProcessesOptimizationSpecification

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ControlParameterOptimizer:
    def __init__(
        self,
        specification: ProcessesOptimizationSpecification,
    ):
        process_dict = {}
        self.control_parameters_spec = {}
        self.output_constraints = {}
        self.use_relative_window = False
        self.relative_window_cfg = {
            "min_pct": 0.0,  # as fraction: 0.05 == 5%
            "max_pct": 0.0,
            "clamp_to_absolute": True,
            "value_selector": "last",  # or "mean"
        }
        self.dynamic_bounds = {}  # {param_name: (low, high)}

        for (
            process_name,
            process_info,
        ) in specification.data_specifications.items():
            process_dict[process_name] = {}
            model_path = process_info.model_path
            data_config = process_info.data_config
            history_size = data_config.history_size
            interval_minutes = data_config.interval_minutes
            ml_model = ModelServing(model_path=model_path, data_config=data_config)
            input_spec = process_info.input_specification
            output_constraint = process_info.output_constraint
            if output_constraint != None:
                self.output_constraints[process_name] = output_constraint
            for parameter in input_spec.specification.values():
                if (
                    isinstance(parameter, ControlParameter)
                    and parameter.parameter_name not in self.control_parameters_spec
                ):
                    self.control_parameters_spec[parameter.parameter_name] = parameter
            process_dict[process_name]["model"] = ml_model
            process_dict[process_name]["history_size"] = history_size
            process_dict[process_name]["interval_minutes"] = interval_minutes
            process_dict[process_name]["input_spec"] = input_spec

        self.process_dict = process_dict
        self.optimization_objective = specification.optimization_objectives

        if self.optimization_objective != None:
            self.output_constraints[self.optimization_objective.parameter_name] = (
                self.optimization_objective
            )

    def align_bounds_to_step(
        self, low: float, high: float, step: float
    ) -> tuple[float, float]:
        if not step or step <= 0:
            return low, high
        span = high - low
        k = math.floor(span / step)
        if k <= 0:
            high = low + step
        else:
            high = low + k * step
        high = max(high, low + step)
        return low, high

    def set_relative_search_window(
        self,
        min_pct: float,
        max_pct: float,
        clamp_to_absolute: bool = True,
        value_selector: str = "last",
    ):
        """Enable relative windowing around current value from input_df."""

        def _norm(p):
            return p / 100.0 if p > 1 else p

        self.use_relative_window = True
        self.relative_window_cfg = {
            "min_pct": _norm(min_pct),
            "max_pct": _norm(max_pct),
            "clamp_to_absolute": clamp_to_absolute,
            "value_selector": value_selector,
        }

    def get_directions(self) -> list[str]:
        try:
            """Return a list of 'maximize'/'minimize' for objectives."""
            directions = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return directions
            for quality in self.output_constraints.values():
                if quality.objective != OptimizationObjective.NONE:
                    directions.append(quality.objective.value)
            return directions
        except Exception as e:
            logging.error(f"Error getting directions: {e}")
            logging.info(traceback.format_exc())
            return []

    def pick_objectives(self, result: dict):
        try:
            """Return actual objective values for a trial."""
            objectives = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return objectives
            for name, quality in self.output_constraints.items():
                if quality.objective != OptimizationObjective.NONE:
                    objectives.append(result[name])
            return objectives
        except Exception as e:
            logging.error(f"Error picking objectives: {e}")
            logging.info(traceback.format_exc())
            return []

    def compute_constraints(self, result: dict) -> list[float]:
        try:
            """Convert black-box outputs into Optuna constraint values."""
            values = []
            if self.output_constraints == {}:
                logging.warning("No output constraints defined.")
                return values
            for name, quality in self.output_constraints.items():
                val = result[name]

                # check upper bound
                if quality.upper_limit is not None:
                    values.append(val - quality.upper_limit)

                # check lower bound
                if quality.lower_limit is not None:
                    values.append(quality.lower_limit - val)
            return values
        except Exception as e:
            logging.error(f"Error computing constraints: {e}")
            logging.info(traceback.format_exc())
            return []

    def _compute_dynamic_bounds(self, input_df: pd.DataFrame):
        """Compute per-parameter dynamic [low, high] bounds from input_df."""
        self.dynamic_bounds = {}
        cfg = self.relative_window_cfg

        def pick_value(series: pd.Series, selector: str):
            s = pd.to_numeric(series, errors="coerce").dropna()
            if s.empty:
                return None
            if selector == "mean":
                return float(s.mean())
            # default: last non-null
            return float(s.iloc[-1])

        for p in self.control_parameters_spec.values():
            name = p.parameter_name
            col = name

            cur_val = None
            if input_df is not None and col in input_df.columns:
                cur_val = pick_value(input_df[col], cfg["value_selector"])

            if cur_val is None:
                # fallback to ControlParameter.current_value if available; else mid of absolute window
                cur_val = getattr(p, "current_value", None)
                if cur_val is None:
                    cur_val = (p.min_value + p.max_value) / 2.0

            low = cur_val * (1.0 - cfg["min_pct"])
            high = cur_val * (1.0 + cfg["max_pct"])

            # ensure ordering (handles negative cur_val and asymmetric pcts)
            low, high = (low, high) if low <= high else (high, low)

            if cfg["clamp_to_absolute"]:
                low = max(low, p.min_value)
                high = min(high, p.max_value)

            if high - low < (p.step_size or 0.0):
                # expand symmetrically around cur_val within absolutes
                half = max(p.step_size or 0.0, 0.0) / 2.0
                low = max(cur_val - half, p.min_value)
                high = min(cur_val + half, p.max_value)
                if high <= low:  # worst case: collapse to a single point, bump high
                    high = min(low + (p.step_size or 1e-9), p.max_value)

            low, high = self.align_bounds_to_step(low, high, p.step_size)
            self.dynamic_bounds[name] = (float(low), float(high))

    def _bounds_for(self, parameter) -> tuple[float, float]:
        """Return (low, high) for a parameter, preferring dynamic bounds."""
        if self.use_relative_window and parameter.parameter_name in self.dynamic_bounds:
            return self.dynamic_bounds[parameter.parameter_name]
        return (parameter.min_value, parameter.max_value)

    def __call__(self, trial: optuna.Trial) -> float:
        try:
            # Define the search space
            for parameter in self.control_parameters_spec.values():
                low, high = self._bounds_for(parameter)
                parameter.trial_value = trial.suggest_float(
                    parameter.parameter_name, low, high, step=parameter.step_size
                )
            result = {}
            for process_name, process_info in self.process_dict.items():
                try:
                    input_data = create_inference_input(
                        self.input_df,
                        process_info["history_size"],
                        process_info["interval_minutes"],
                        process_info["input_spec"],
                        trial_run=True,
                    )
                    ml_model = process_info["model"]
                    input_data = input_data.astype("float32")
                    result[process_name] = ml_model.single_inference_np(input_data)

                except Exception as e:
                    logging.error(f"Error creating inference input: {e}")
                    logging.info(traceback.format_exc())

            if self.optimization_objective != None:
                cost_saving = 0
                for parameter in self.control_parameters_spec.values():
                    if parameter.cost_function != None:
                        cost_function_module = importlib.import_module(
                            "gfa_ml.custom.cost_function"
                        )
                        cost_function = getattr(
                            cost_function_module, parameter.cost_function
                        )
                        cost_saving += cost_function(
                            parameter.current_value, parameter.trial_value
                        )
                result[self.optimization_objective.parameter_name] = cost_saving

            # define objective
            constraints = self.compute_constraints(result)
            trial.set_user_attr("constraints", constraints)

            objectives = self.pick_objectives(result)
            return tuple(objectives)
        except Exception as e:
            logging.error(f"Error during trial evaluation: {e}")
            logging.info(traceback.format_exc())
            return ()

    def optimize(
        self,
        input_df: pd.DataFrame,
        n_trials: int = 50,
        sampler_type: OptunaSampler = OptunaSampler.QMCSampler,
        log_info: bool = False,
        relative_window: tuple[float, float] | None = None,  # (min_pct, max_pct)
        clamp_to_absolute: bool = True,
        value_selector: str = "last",
    ) -> optuna.Study:
        try:
            self.input_df = input_df

            if relative_window is not None:
                self.set_relative_search_window(
                    min_pct=relative_window[0],
                    max_pct=relative_window[1],
                    clamp_to_absolute=clamp_to_absolute,
                    value_selector=value_selector,
                )
            if self.use_relative_window:
                self._compute_dynamic_bounds(input_df)

            if log_info:
                optuna.logging.set_verbosity(optuna.logging.INFO)
            else:
                optuna.logging.set_verbosity(optuna.logging.ERROR)
            directions = self.get_directions()
            if sampler_type == OptunaSampler.TPE:
                sampler = optuna.samplers.TPESampler()
            elif sampler_type == OptunaSampler.CMAES:
                sampler = optuna.samplers.CmaEsSampler()
            elif sampler_type == OptunaSampler.QMCSampler:
                sampler = optuna.samplers.QMCSampler()
            elif sampler_type == OptunaSampler.GRID:
                sampler = optuna.samplers.GridSampler()
            elif sampler_type == OptunaSampler.RANDOM:
                sampler = optuna.samplers.RandomSampler()
            elif sampler_type == OptunaSampler.NSGAII:
                sampler = optuna.samplers.NSGAIISampler()
            elif sampler_type == OptunaSampler.BRUTE_FORCE:
                sampler = optuna.samplers.BruteForceSampler()
            elif sampler_type == OptunaSampler.BOTORCH:
                sampler = optuna.samplers.BoTorchSampler()
            elif sampler_type == OptunaSampler.GP:
                sampler = optuna.samplers.GPSampler()
            else:
                sampler = optuna.samplers.TPESampler()

            study = optuna.create_study(directions=directions, sampler=sampler)
            # --- Run optimization ---
            study.optimize(self, n_trials=n_trials)

            feasible_trials = []
            for t in study.trials:
                cons = t.user_attrs["constraints"]
                if all(c <= 0 for c in cons):
                    feasible_trials.append(t)
            logging.info(f"Number of feasible trials: {len(feasible_trials)}")
            # Get the best trial
            if feasible_trials:
                if self.optimization_objective is not None:
                    if (
                        self.optimization_objective.objective
                        == OptimizationObjective.MAXIMIZE
                    ):
                        best_trial = max(
                            feasible_trials, key=lambda t: t.values[0]
                        )  # maximize first objective
                    elif (
                        self.optimization_objective.objective
                        == OptimizationObjective.MINIMIZE
                    ):
                        best_trial = min(feasible_trials, key=lambda t: t.values[0])
                    else:
                        logging.error("Invalid optimization objective.")
                        return None
                else:
                    logging.error("No optimization objective defined.")
                    return None

                logging.info(
                    f"Best trial: {best_trial.number}, Objectives: {best_trial.values}, Parameters: {best_trial.params}"
                )
                return best_trial
            else:
                logging.info("No feasible trial found, selecting best overall trial.")
                return None

        except Exception as e:
            logging.error(f"Error during optimization: {e}")
            logging.info(traceback.format_exc())
            return None


class HyperParameterOptimizer:
    def __init__(
        self,
        experiment_name: str,
        run_config: RunConfig,
        input_cols_list: list,
        history_size_list: list,
        retention_padding_list: list,
        model_type_list: list,
        batch_size_list: list = DEFAULT_BATCH_SIZES,
        drop_rate_list: list = DEFAULT_DROPOUT_RATES,
        loss_list: list = DEFAULT_LOSSES,
        learning_rate_list: list = DEFAULT_LEARNING_RATES,
        num_layers_list: list = DEFAULT_NUM_HIDDEN_LAYERS,
        activation_function_list: list = DEFAULT_ACTIVATION_FUNCTIONS,
        optimizer_list: list = DEFAULT_OPTIMIZERS,
        d_model_list: list = DEFAULT_D_MODELS,
        nhead_list: list = DEFAULT_NHEADS,
        dim_feedforward_list: list = DEFAULT_DIM_FEEDFORWARDS,
        hidden_neurons_list: list = DEFAULT_HIDDEN_NEURONS,
        explainability: bool = True,
        plot_path: str = None,
        interpolate_outliers: bool = False,
        image_extension: str = "png",
        optimization_objective: str = "test_mape",
    ):
        self.df = None
        self.experiment_name = experiment_name
        self.run_config = run_config
        self.input_cols_list = input_cols_list
        self.history_size_list = history_size_list
        self.retention_padding_list = retention_padding_list
        self.model_type_list = model_type_list
        self.batch_size_list = batch_size_list
        self.drop_rate_list = drop_rate_list
        self.loss_list = loss_list
        self.learning_rate_list = learning_rate_list
        self.num_layers_list = num_layers_list
        self.activation_function_list = activation_function_list
        self.optimizer_list = optimizer_list
        self.d_model_list = d_model_list
        self.nhead_list = nhead_list
        self.dim_feedforward_list = dim_feedforward_list
        self.hidden_neurons_list = hidden_neurons_list
        self.explainability = explainability
        self.plot_path = plot_path
        self.interpolate_outliers = interpolate_outliers
        self.image_extension = image_extension
        self.optimization_objective = optimization_objective

    def run_study(
        self,
        df: pd.DataFrame,
        n_trials: int = 20,
        n_jobs: int = 1,
        sampler_type: OptunaSampler = OptunaSampler.QMCSampler,
    ):
        try:
            self.df = df
            if sampler_type == OptunaSampler.TPE:
                sampler = optuna.samplers.TPESampler()
            elif sampler_type == OptunaSampler.CMAES:
                sampler = optuna.samplers.CmaEsSampler()
            elif sampler_type == OptunaSampler.QMCSampler:
                sampler = optuna.samplers.QMCSampler()
            elif sampler_type == OptunaSampler.GRID:
                sampler = optuna.samplers.GridSampler()
            elif sampler_type == OptunaSampler.RANDOM:
                sampler = optuna.samplers.RandomSampler()
            elif sampler_type == OptunaSampler.NSGAII:
                sampler = optuna.samplers.NSGAIISampler()
            elif sampler_type == OptunaSampler.BRUTE_FORCE:
                sampler = optuna.samplers.BruteForceSampler()
            elif sampler_type == OptunaSampler.BOTORCH:
                sampler = optuna.samplers.BoTorchSampler()
            elif sampler_type == OptunaSampler.GP:
                sampler = optuna.samplers.GPSampler()
            else:
                sampler = optuna.samplers.TPESampler()
            study = optuna.create_study(direction="minimize", sampler=sampler)
            study.optimize(self.objective, n_trials=n_trials, n_jobs=n_jobs)
            logging.info(f"Best trial: {study.best_trial.number}")
            logging.info(f"Best value: {study.best_trial.value}")
            logging.info(f"Best params: {study.best_trial.params}")
            return study, study.best_trial
        except Exception as e:
            logging.error(f"Error running study: {e}")
            logging.info(traceback.format_exc())
            return None

    def objective(self, trial: optuna.Trial) -> float:
        try:
            temp_run_config = copy.deepcopy(self.run_config)
            input_cols_index = trial.suggest_int(
                "input_cols_index", 0, len(self.input_cols_list) - 1
            )
            history_size_index = trial.suggest_int(
                "history_size_index", 0, len(self.history_size_list) - 1
            )
            retention_padding_index = trial.suggest_int(
                "retention_padding_index", 0, len(self.retention_padding_list) - 1
            )
            batch_size_index = trial.suggest_int(
                "batch_size_index", 0, len(self.batch_size_list) - 1
            )
            drop_rate_index = trial.suggest_int(
                "drop_rate_index", 0, len(self.drop_rate_list) - 1
            )
            loss_index = trial.suggest_int("loss_index", 0, len(self.loss_list) - 1)
            learning_rate_index = trial.suggest_int(
                "learning_rate_index", 0, len(self.learning_rate_list) - 1
            )
            num_layers_index = trial.suggest_int(
                "num_layers_index", 0, len(self.num_layers_list) - 1
            )
            activation_function_index = trial.suggest_int(
                "activation_function_index", 0, len(self.activation_function_list) - 1
            )
            optimizer_index = trial.suggest_int(
                "optimizer_index", 0, len(self.optimizer_list) - 1
            )
            input_cols = self.input_cols_list[input_cols_index]
            history_size = self.history_size_list[history_size_index]
            retention_padding = self.retention_padding_list[retention_padding_index]
            batch_size = self.batch_size_list[batch_size_index]
            drop_rate = self.drop_rate_list[drop_rate_index]
            loss = self.loss_list[loss_index]
            learning_rate = self.learning_rate_list[learning_rate_index]
            num_layers = self.num_layers_list[num_layers_index]
            activation_function = self.activation_function_list[
                activation_function_index
            ]
            optimizer = self.optimizer_list[optimizer_index]
            trial.set_user_attr("input_cols", input_cols)
            trial.set_user_attr("history_size", history_size)
            trial.set_user_attr("retention_padding", retention_padding)
            trial.set_user_attr("batch_size", batch_size)
            trial.set_user_attr("drop_rate", drop_rate)
            trial.set_user_attr("loss", loss)
            trial.set_user_attr("learning_rate", learning_rate)
            trial.set_user_attr("num_layers", num_layers)
            trial.set_user_attr("activation_function", activation_function)
            trial.set_user_attr("optimizer", optimizer)

            temp_run_config.data_config.input_cols = input_cols
            temp_run_config.data_config.history_size = history_size
            temp_run_config.data_config.retention_padding = retention_padding
            temp_run_config.training_config.batch_size = batch_size
            temp_run_config.ml_model_config.drop_rate = drop_rate
            temp_run_config.ml_model_config.loss = loss
            temp_run_config.ml_model_config.learning_rate = learning_rate
            temp_run_config.ml_model_config.num_layers = num_layers
            temp_run_config.ml_model_config.activation_function = activation_function
            temp_run_config.ml_model_config.optimizer = optimizer

            model_type_index = trial.suggest_int(
                "model_type_index", 0, len(self.model_type_list) - 1
            )
            model_type = self.model_type_list[model_type_index]
            trial.set_user_attr("model_type", model_type)
            model_config_dict = temp_run_config.ml_model_config.to_dict()
            model_config_dict["model_type"] = model_type
            if model_type == ModelType.TRANSFORMER.value:
                d_model_index = trial.suggest_int(
                    "d_model_index", 0, len(self.d_model_list) - 1
                )
                nhead_index = trial.suggest_int(
                    "nhead_index", 0, len(self.nhead_list) - 1
                )
                dim_feedforward_index = trial.suggest_int(
                    "dim_feedforward_index", 0, len(self.dim_feedforward_list) - 1
                )
                d_model = self.d_model_list[d_model_index]
                nhead = self.nhead_list[nhead_index]
                dim_feedforward = self.dim_feedforward_list[dim_feedforward_index]
                trial.set_user_attr("d_model", d_model)
                trial.set_user_attr("nhead", nhead)
                trial.set_user_attr("dim_feedforward", dim_feedforward)
                model_config_dict.update(
                    {
                        "d_model": d_model,
                        "nhead": nhead,
                        "dim_feedforward": dim_feedforward,
                    }
                )
                temp_run_config.ml_model_config = TransformerConfig.from_dict(
                    model_config_dict
                )
            elif model_type == ModelType.LSTM.value:
                hidden_neurons_index = trial.suggest_int(
                    "hidden_neurons_index", 0, len(self.hidden_neurons_list) - 1
                )
                hidden_neurons = self.hidden_neurons_list[hidden_neurons_index]
                trial.set_user_attr("hidden_neurons", hidden_neurons)
                lstm_config_dict = {"hidden_neurons": hidden_neurons}
                temp_run_config.ml_model_config = LSTMConfig.from_dict(lstm_config_dict)

            training_result = mlflow_run(
                df=self.df,
                run_config=temp_run_config,
                experiment_name=self.experiment_name,
                run_name=f"run_{trial.number}",
                explainability=self.explainability,
                plot_path=self.plot_path,
                interpolate_outliers=self.interpolate_outliers,
                image_extension=self.image_extension,
            )
            if training_result is None:
                return float("inf")
            loss_value = training_result.get(self.optimization_objective, float("inf"))
            return loss_value
        except Exception as e:
            logging.error(f"Error in objective function: {e}")
            logging.info(traceback.format_exc())
            return float("inf")
