"""Annotation-based tuning converters for PyTorchJob."""

import logging
import re

from optuna import Trial

from .pytorchjob import PyTorchJob

logger = logging.getLogger("zenith-tune")


def annotation_job_converter(trial: Trial, job: PyTorchJob) -> PyTorchJob:
    """
    Convert job based on annotation configuration.

    This function reads the zenith-tune/optimization-config annotation
    and applies the hyperparameter values suggested by the trial.

    Args:
        trial: Optuna trial object
        job: Original PyTorchJob

    Returns:
        Modified PyTorchJob with trial parameters applied

    Raises:
        ValueError: If tuning config is invalid or missing required fields
    """
    tuning_config = job.get_tuning_config()
    if tuning_config is None:
        raise ValueError("No tuning config found")

    variables = tuning_config.get("variables", [])
    if not variables:
        raise ValueError("Invalid tuning config: no variables found")

    for i, variable in enumerate(variables):
        try:
            # Validate required fields
            if "name" not in variable:
                raise ValueError("Invalid tuning config: variable missing 'name' field")
            if "type" not in variable:
                raise ValueError("Invalid tuning config: variable missing 'type' field")

            name = variable["name"]
            var_type = variable["type"]
            target_env = variable.get("target_env", name.upper())

            if var_type == "float":
                if "range" not in variable:
                    raise ValueError(
                        "Invalid tuning config: float variable missing 'range' field"
                    )
                try:
                    low, high = variable["range"]
                    if len(variable["range"]) != 2:
                        raise ValueError(
                            "Invalid tuning config: range must have exactly 2 values"
                        )
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        "Invalid tuning config: invalid range format"
                    ) from e

                log = variable.get("log", False)
                try:
                    value = trial.suggest_float(name, low, high, log=log)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid tuning config: invalid float range for {name}"
                    ) from e

            elif var_type == "int":
                if "range" not in variable:
                    raise ValueError(
                        "Invalid tuning config: int variable missing 'range' field"
                    )
                try:
                    low, high = variable["range"]
                    if len(variable["range"]) != 2:
                        raise ValueError(
                            "Invalid tuning config: range must have exactly 2 values"
                        )
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        "Invalid tuning config: invalid range format"
                    ) from e

                step = variable.get("step", 1)
                try:
                    value = trial.suggest_int(name, low, high, step=step)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid tuning config: invalid int range for {name}"
                    ) from e

            elif var_type == "categorical":
                if "choices" not in variable:
                    raise ValueError(
                        "Invalid tuning config: categorical variable missing 'choices' field"
                    )
                choices = variable["choices"]
                if not choices or not isinstance(choices, list):
                    raise ValueError(
                        "Invalid tuning config: choices must be a non-empty list"
                    )
                try:
                    value = trial.suggest_categorical(name, choices)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid tuning config: invalid choices for {name}"
                    ) from e

            else:
                raise ValueError(
                    f"Invalid tuning config: unsupported variable type: {var_type}"
                )

            # Set environment variable
            job.set_env(target_env, str(value))

        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Invalid tuning config: error processing variable {i}"
            ) from e

    return job


def annotation_value_extractor(log_path: str, job: PyTorchJob) -> float:
    """
    Extract objective value from logs based on annotation configuration.

    This function reads the zenith-tune/optimization-config annotation
    and extracts the objective value using the specified regex pattern.

    Args:
        log_path: Path to the log file
        job: PyTorchJob object

    Returns:
        Extracted objective value

    Raises:
        ValueError: If no objective configuration found or value cannot be extracted
    """
    tuning_config = job.get_tuning_config()
    if tuning_config is None:
        raise ValueError("No tuning config found")

    objective_config = tuning_config.get("objective")
    if objective_config is None:
        raise ValueError("No objective configuration found in annotation")

    # Validate objective config structure
    if not isinstance(objective_config, dict):
        raise ValueError("Invalid objective config: must be a dictionary")

    if "regex" not in objective_config:
        raise ValueError("Invalid objective config: missing 'regex' field")

    regex_pattern = objective_config["regex"]
    if not regex_pattern or not isinstance(regex_pattern, str):
        raise ValueError("Invalid objective config: 'regex' must be a non-empty string")

    try:
        with open(log_path) as f:
            log_content = f.read()
    except FileNotFoundError:
        raise ValueError(f"Log file not found: {log_path}") from None
    except OSError as e:
        raise ValueError(f"Error reading log file {log_path}: {e}") from e

    # Validate regex pattern
    try:
        compiled_pattern = re.compile(regex_pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern '{regex_pattern}': {e}") from e

    # Find all matches and use the first one
    try:
        matches = compiled_pattern.findall(log_content)
    except Exception as e:
        raise ValueError(f"Error applying regex pattern: {e}") from e

    if not matches:
        raise ValueError(f"No matches found for pattern: {regex_pattern}")

    try:
        # Use the first match
        value = float(matches[0])
        logger.info(f"Extracted objective value: {value}")
        return value
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to convert extracted value to float: {e}") from None
