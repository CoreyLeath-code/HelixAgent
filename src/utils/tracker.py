# src/utils/tracker.py

"""
Experiment Tracker for HelixAgent
---------------------------------
Provides MLflow integration for logging experiments, metrics,
parameters, and artifacts.
"""

import mlflow

from src.utils.logger import setup_logger

log = setup_logger()


class ExperimentTracker:
    def __init__(self, experiment_name: str = "HelixAgent-Experiments", tracking_uri: str = "http://127.0.0.1:5000"):
        """
        Initialize MLflow tracker.
        
        Args:
            experiment_name (str): Name of the MLflow experiment.
            tracking_uri (str): MLflow tracking server URI.
        """
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        log.info(f"Initialized MLflow tracker: {experiment_name}")

    def start_run(self, run_name: str | None = None):
        """Start a new MLflow run"""
        return mlflow.start_run(run_name=run_name)

    def log_params(self, params: dict):
        """Log parameters to MLflow"""
        mlflow.log_params(params)
        log.debug(f"Logged parameters: {params}")

    def log_metrics(self, metrics: dict, step: int | None = None):
        """Log metrics to MLflow"""
        mlflow.log_metrics(metrics, step=step)
        log.debug(f"Logged metrics: {metrics}")

    def log_artifact(self, file_path: str):
        """Log a file (artifact) to MLflow"""
        mlflow.log_artifact(file_path)
        log.debug(f"Logged artifact: {file_path}")

    def end_run(self):
        """End the current MLflow run"""
        mlflow.end_run()
        log.info("MLflow run ended.")


# Example usage:
# tracker = ExperimentTracker()
# with tracker.start_run("test-run"):
#     tracker.log_params({"learning_rate": 0.001, "batch_size": 32})
#     tracker.log_metrics({"accuracy": 0.85}, step=1)
#     tracker.log_artifact("models/agent_model.pt")
# tracker.end_run()
