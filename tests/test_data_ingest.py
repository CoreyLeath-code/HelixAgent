"""Unit tests for HelixAgent's validated data-ingestion pipeline."""

from pathlib import Path

import pandas as pd
import pytest

from src.data_ingest import DataIngestor


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    frame = pd.DataFrame(
        {
            " Text ": [
                "The movie was great!",
                "The food was awful.",
                "Loved the service.",
                "Never going back.",
                "What a fantastic product!",
                "Excellent support.",
                "Poor experience.",
                "Would recommend.",
                "Not worth it.",
                "Very reliable.",
            ],
            "Label": [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        }
    )
    path = tmp_path / "sample_dataset.csv"
    frame.to_csv(path, index=False)
    return path


def test_load_data_returns_non_empty_frame(sample_csv: Path) -> None:
    frame = DataIngestor(sample_csv).load_data()

    assert frame.shape == (10, 2)
    assert " Text " in frame.columns


def test_preprocess_normalizes_headers_and_removes_nulls(tmp_path: Path) -> None:
    path = tmp_path / "dirty.csv"
    pd.DataFrame({" Text ": ["hello", None], "LABEL": [1, 0]}).to_csv(path, index=False)
    ingestor = DataIngestor(path)
    ingestor.load_data()

    frame = ingestor.preprocess()

    assert list(frame.columns) == ["text", "label"]
    assert len(frame) == 1
    assert frame.isnull().sum().sum() == 0


def test_split_data_is_complete_and_reproducible(sample_csv: Path) -> None:
    first = DataIngestor(sample_csv, test_size=0.2, val_size=0.2, random_state=7)
    first.load_data()
    first.preprocess()
    first_split = first.split_data()

    second = DataIngestor(sample_csv, test_size=0.2, val_size=0.2, random_state=7)
    second.load_data()
    second.preprocess()
    second_split = second.split_data()

    assert sum(len(partition) for partition in first_split) == 10
    for first_partition, second_partition in zip(first_split, second_split):
        assert first_partition.index.tolist() == second_partition.index.tolist()
        assert not first_partition.empty


@pytest.mark.parametrize("field,value", [("test_size", 0.0), ("test_size", 1.0), ("val_size", -0.1)])
def test_invalid_split_fractions_are_rejected(tmp_path: Path, field: str, value: float) -> None:
    kwargs = {field: value}
    with pytest.raises(ValueError, match=field):
        DataIngestor(tmp_path / "data.csv", **kwargs)


def test_non_csv_input_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dataset.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Only CSV"):
        DataIngestor(path).load_data()


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        DataIngestor(tmp_path / "missing.csv").load_data()


def test_empty_dataset_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("text,label\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        DataIngestor(path).load_data()
