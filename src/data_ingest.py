"""Validated, reproducible data-ingestion utilities for HelixAgent."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.logger import setup_logger

log = setup_logger()
_MIN_ROWS_FOR_THREE_WAY_SPLIT: Final[int] = 3


class DataIngestor:
    """Load, normalize, validate, and split CSV datasets reproducibly."""

    def __init__(
        self,
        file_path: str | Path,
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42,
    ) -> None:
        self.file_path = Path(file_path)
        self.test_size = self._validate_fraction("test_size", test_size)
        self.val_size = self._validate_fraction("val_size", val_size)
        self.random_state = random_state
        self.df: pd.DataFrame | None = None

    @staticmethod
    def _validate_fraction(name: str, value: float) -> float:
        if not 0.0 < value < 1.0:
            raise ValueError(f"{name} must be between 0 and 1; received {value!r}.")
        return value

    def load_data(self) -> pd.DataFrame:
        """Load a non-empty CSV file from disk."""
        if self.file_path.suffix.lower() != ".csv":
            raise ValueError(f"Only CSV inputs are supported: {self.file_path}")
        if not self.file_path.is_file():
            raise FileNotFoundError(f"Dataset does not exist: {self.file_path}")

        frame = pd.read_csv(self.file_path)
        if frame.empty:
            raise ValueError(f"Dataset is empty: {self.file_path}")

        self.df = frame
        log.info("Loaded dataset: %s | Shape: %s", self.file_path, frame.shape)
        return frame

    def preprocess(self) -> pd.DataFrame:
        """Drop null rows and normalize column names to lowercase snake-like text."""
        if self.df is None:
            raise RuntimeError("No dataset loaded. Run load_data() first.")

        normalized = self.df.dropna().copy()
        normalized.columns = [str(column).strip().lower() for column in normalized.columns]
        if normalized.empty:
            raise ValueError("Dataset contains no usable rows after null-value removal.")
        if normalized.columns.duplicated().any():
            duplicates = normalized.columns[normalized.columns.duplicated()].tolist()
            raise ValueError(f"Normalized dataset contains duplicate columns: {duplicates}")

        self.df = normalized
        log.info("Preprocessed dataset: removed null rows and normalized headers.")
        return normalized

    def split_data(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Create deterministic train, validation, and test partitions."""
        if self.df is None:
            raise RuntimeError("No dataset loaded. Run load_data() first.")
        if len(self.df) < _MIN_ROWS_FOR_THREE_WAY_SPLIT:
            raise ValueError("At least three rows are required for train/validation/test splits.")
        if self.test_size + self.val_size >= 1.0:
            raise ValueError("test_size + val_size must be less than 1.0.")

        train_and_val, test = train_test_split(
            self.df,
            test_size=self.test_size,
            random_state=self.random_state,
            shuffle=True,
        )
        validation_fraction = self.val_size / (1.0 - self.test_size)
        train, validation = train_test_split(
            train_and_val,
            test_size=validation_fraction,
            random_state=self.random_state,
            shuffle=True,
        )

        log.info(
            "Split data -> Train: %s, Validation: %s, Test: %s",
            train.shape,
            validation.shape,
            test.shape,
        )
        return train, validation, test
