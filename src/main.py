# src/main.py

"""
HelixAgent CLI Entry Point
--------------------------
Run the agent locally from the command line.

Usage:
    python src/main.py
    python src/main.py --prompt "Compare vectors and draft a summary"
"""

import argparse
import os
import sys

# Ensure the project root is in the path when running as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.logger import setup_logger  # noqa: E402

log = setup_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HelixAgent – AI-powered agent framework"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Hello, HelixAgent! Run a quick smoke test.",
        help="Prompt to send to the agent",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log.info("HelixAgent starting...")
    log.info(f"Prompt: {args.prompt}")

    try:
        from agent.agent_core import AgenticAssistant  # noqa: E402

        log.info("Initializing agent core...")
        assistant = AgenticAssistant()
        output = assistant.run(args.prompt)
        log.info("Agent run complete.")
        print(f"Agent Output: {output}")
    except Exception as exc:  # noqa: BLE001
        log.warning(f"Agent core unavailable ({exc}); running echo mode.")
        print(f"[HelixAgent] Echo: {args.prompt}")


if __name__ == "__main__":
    main()
