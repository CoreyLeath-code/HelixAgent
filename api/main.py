# api/main.py

"""
HelixAgent FastAPI Application
-------------------------------
Main API entrypoint. Mounts monitoring (Prometheus + OpenTelemetry) and
exposes core routes for agent inference.
"""

import os

from fastapi…2402 tokens truncated…abels:
    app: helixagent
data:
  config.yaml: |
    project:
      name: "HelixAgent"
      version: "1.1.0"
      author: "Corey Leath"
      description: "Modular AI agent framework for automation, reasoning, and decision-making."

    logging:
      level: "INFO"
      log_to_file: true
      log_file: "logs/helixagent.log"

    agent:
      model: "gpt-neo"
      max_tokens: 512
      temperature: 0.7
      top_p: 0.9

    api:
      host: "0.0.0.0"
      port: 8000
      reload: true

    dashboard:
      host: "0.0.0.0"
      port: 8501

    mlflow:
      enabled: true
      experiment_name: "HelixAgent-Experiments"
      tracking_uri: "http://mlflow:5000"

    data:
      input_path: "data/input/"
      output_path: "data/output/"
      batch_size: 32
      shuffle: true
      validation_split: 0.1
