"""
Tests for qc metric functions
"""
import datetime
import json
import os
import pytest
import pandas as pd
from onyx import OnyxConfig, OnyxEnv
from mscape_sample_qc import qc_functions as qc

# Fixtures

@pytest.fixture
def config_file():
    file = "tests/test_data/example_qc_thresholds.yaml"
    return file

@pytest.fixture
def expected_config_dict():
    config = {"sample_thresholds": {
              "total_reads": {"pass": 10000, "fail": 2000},
              "percentage_spike_in": {"pass": 5, "fail": 20},
              "percentage_host": {"pass": 5, "fail": 10},
              "percentage_unclassified": {"pass": 10, "fail": 30},
              "percentage_genus": {"pass": 80, "fail": 60}
              }
             }
    return config

@pytest.fixture
def example_classifier_df(): # From retrieve sample info
    with open("tests/test_data/example_classifier_calls.csv") as file:
        class_df = pd.read_csv(file)

    return class_df

@pytest.fixture
def expected_proportions_dict():
    result_df = {"total_reads": 10,
                 "count_descendants_unclassified": 6, "percentage_unclassified": 60.0,
                 "count_descendants_spike_in": 2, "percentage_spike_in": 20.0,
                 "count_descendants_host": 1, "percentage_host": 10.0,
                 "count_descendants_genus": 4, "percentage_genus": 40.0}

    return result_df

@pytest.fixture
def expected_threshold_dict():
    result_df = {"total_reads": 10,
                 "count_descendants_unclassified": 6, "percentage_unclassified": 60.0,
                 "count_descendants_spike_in": 2, "percentage_spike_in": 20.0,
                 "count_descendants_host": 1, "percentage_host": 10.0,
                 "count_descendants_genus": 4, "percentage_genus": 40.0,
                 "total_reads_qc": "Fail", "percentage_spike_in_qc": "Fail",
                 "percentage_unclassified_qc": "Fail",
                 "percentage_genus_qc": "Fail", "percentage_host_qc": "Fail"}

    return result_df


@pytest.fixture
def expected_result_dict():
    result_df = {"total_reads": 10,
                 "count_descendants_unclassified": 6, "percentage_unclassified": 60.0,
                 "count_descendants_spike_in": 2, "percentage_spike_in": 20.0,
                 "count_descendants_host": 1, "percentage_host": 10.0,
                 "count_descendants_genus": 4, "percentage_genus": 40.0,
                 "total_reads_qc": "Fail", "percentage_spike_in_qc": "Fail",
                 "percentage_unclassified_qc": "Fail",
                 "percentage_genus_qc": "Fail", "percentage_host_qc": "Fail",
                 "spike_detected": "Pass"}

    return result_df

@pytest.fixture
def expected_result_dict_passes():
    result_df = {"total_reads": 10,
                 "count_descendants_unclassified": 6, "percentage_unclassified": 60.0,
                 "count_descendants_spike_in": 2, "percentage_spike_in": 20.0,
                 "count_descendants_host": 1, "percentage_host": 10.0,
                 "count_descendants_genus": 4, "percentage_genus": 40.0,
                 "total_reads_qc": "Pass", "percentage_spike_in_qc": "Pass",
                 "percentage_unclassified_qc": "Pass",
                 "percentage_genus_qc": "Pass", "percentage_host_qc": "Pass",
                 "spike_detected": "Pass"}

    return result_df

@pytest.fixture
def expected_fields_dict(expected_config_dict, expected_result_dict):
    fields_dict = {"name": "ukhsa-classifier-qc-metrics",
                   "description": "This is an analysis to generate QC statistics for individual samples",
                   "analysis_date": datetime.datetime.now().date().isoformat(),
                   "pipeline_name": "mscape-sample-qc",
                   "pipeline_url": "https://github.com/ukhsa-collaboration/mscape-sample-qc",
                   "pipeline_version": "0.1.0",
                   "methods": json.dumps(expected_config_dict),
                   "result": "Warning: Check QC results before use",
                   "result_metrics": json.dumps(expected_result_dict),
                   "report": "tests/test_data/C-123456789_qc_results.json",
                   "synthscape_records": ["C-123456789"],
                   "identifiers": []}

    return fields_dict


@pytest.fixture
def expected_result_file():
    file = "tests/test_data/C-123456789_qc_results.json"

    return file


@pytest.fixture
def qc_json_file_path(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("onyx_analysis_tests")

    return str(tmp_dir)

# Tests - those marked skip need test data making/some additional work

@pytest.mark.skip
def test_retrieve_sample_information(record_id): # Mock onyx call? Add error handling to retrieve_sample_information function?
    "Check df and dict returned as expected"
    print(record_id)

def test_read_config_file(config_file, expected_config_dict):
    "Checks config file read correctly"
    config = qc.read_config_file(config_file)
    print(config)
    assert config == expected_config_dict

def test_get_read_proportions(example_classifier_df, expected_proportions_dict):
    "Check read proportions calculated correctly"
    taxa_dict = qc.get_read_proportions(example_classifier_df)
    print(taxa_dict)
    print(expected_proportions_dict)
    assert taxa_dict == expected_proportions_dict

def test_check_thresholds(expected_proportions_dict, expected_config_dict, expected_threshold_dict):

    threshold_dict = qc.check_thresholds(expected_proportions_dict, expected_config_dict["sample_thresholds"])
    print(threshold_dict)
    print(expected_threshold_dict)
    assert threshold_dict == expected_threshold_dict

def test_spike_detected(expected_threshold_dict, expected_result_dict):
    spike_dict = qc.check_spike_detected(expected_threshold_dict)
    print(spike_dict)
    assert spike_dict == expected_result_dict

def test_write_qc_results_to_json(expected_result_dict, qc_json_file_path):
    qc_file = qc.write_qc_results_to_json(expected_result_dict, "C-123456789",
                                          qc_json_file_path)

    assert os.path.exists(qc_file)

def test_create_analysis_fields_pass(expected_config_dict, expected_result_dict,
                                     expected_fields_dict, expected_result_file):

    onyx_analysis, exitcode = qc.create_analysis_fields("C-123456789", expected_config_dict,
                                                        expected_result_dict, "testserver",
                                                        "Warning: Check QC results before use",
                                                        expected_result_file)
    print(onyx_analysis.__dict__)

    assert onyx_analysis.__dict__ == expected_fields_dict
    assert exitcode == 0


def test_create_analysis_fields_fail(expected_config_dict, expected_fields_dict,
                                     expected_result_dict, expected_result_file):

    onyx_analysis, exitcode = qc.create_analysis_fields("C-123456789", expected_config_dict,
                                                        expected_result_dict, "testserver",
                                                        "Warning: Check QC results before use",
                                                        "not a file path or dir")
    print(onyx_analysis.__dict__)

    assert exitcode == 1

def test_get_headline_result_pass(expected_result_dict_passes):

    headline_result = qc.get_headline_result(expected_result_dict_passes)

    assert headline_result == "QC results passed thresholds"


def test_get_headline_result_warning(expected_result_dict):

    headline_result = qc.get_headline_result(expected_result_dict)

    assert headline_result == "Warning: Check QC results before use"
