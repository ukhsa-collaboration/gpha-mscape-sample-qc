import os
from pathlib import Path

import pandas as pd
import pytest

os.environ["CONFIG"] = "Placeholder config"
os.environ["ONYX_DOMAIN"] = "Placeholder domain"
os.environ["ONYX_TOKEN"] = "Placeholder token"


@pytest.fixture(scope="module")
def example_classifier_df():  # From retrieve sample info
    with Path("tests/test_data/example_classifier_calls.csv").open("r") as file:
        class_df = pd.read_csv(file)

    return class_df


@pytest.fixture(scope="module")
def mock_onyx_query_response(example_classifier_df):
    classifier_calls = example_classifier_df.to_dict(orient="records")
    mock_onyx_record: dict[str, str | dict | list[dict[str, str]]] = {
        "climb-id": "ID-123456",
        "site": "test",
        "published_date": "2026-01-01",
        "data": {"datapoint1": 1, "datapoint2": 2, "datapoint3": 3},
        "versions": [
            {"name": "classifier_version", "version": "1.0.0"},
            {"name": "classifier_db_date", "version": "1970-01-01"},
            {"name": "ncbi_taxonomy_date", "version": "1970-01-01"},
            {"name": "scylla_version", "version": "1.0.0"},
            {"name": "sylph_db_version", "version": "1.0.0"},
            {"name": "alignment_db_version", "version": "1.0.0"},
            {"name": "new_tool_coming_soon", "version": "0.0.1"},
        ],
        "classifier_calls": classifier_calls,
    }
    return mock_onyx_record
