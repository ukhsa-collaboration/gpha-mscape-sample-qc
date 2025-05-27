"""
Tests for qc metric functions
"""

import pytest
from mscape_sample_qc import qc_functions as qc

# Fixtures

@pytest.fixture
def config_file():
    file = "tests/example_qc_thresholds.yaml"
    return file


@pytest.fixture
def expected_config_dict():
    config = {'sample_thresholds': {
              'total_reads': {'pass': 10000, 'fail': 2000},
              'percentage_spike_in': {'pass': 5, 'fail': 20},
              'percentage_host': {'pass': 5, 'fail': 10},
              'percentage_unclassified': {'pass': 10, 'fail': 30},
              'percentage_genus': {'pass': 80, 'fail': 60}
              }
             }
    return config

@pytest.fixture
def expected_classifier_df():
    file = "" # Add basic example classifier df
    return file

@pytest.fixture
def expected_metadata_df():
    file = "" # Add basic example metadata df
    return file

@pytest.fixture
def expected_fields_dict():
    fields_dict = {} # Add basic example fields dict
    return fields_dict

@pytest.fixture
def expected_result():
    result = "" # Add basic example fields dict
    return result

# Tests - those marked skip need test data making/some additional work

@pytest.mark.skip
def test_retrieve_sample_information(record_id): # Mock onyx call? Add error handling to retrieve_sample_information function?
    "Check df and dict returned as expected"
    print(record_id)


def test_read_config_file(config_file, expected_config_dict):
    "Checks config file read correctly"
    config = qc.read_config_file(config_file)
    print(config)
    assert config == expected_config_yaml


@pytest.mark.skip
def test_get_read_proportions(expected_classifer_df, expected_taxa_dict):
    "Check read proportions calculated correctly"
    taxa_dict = qc.get_read_proportions(expected_classifer_df)
    print(taxa_dict)
    assert taxa_dict == expected_taxa_dict


@pytest.mark.skip
def test_check_thresholds(expected_metadata_dict, expected_config_dict, expected_result_dict):
    
    result_dict = qc.check_thresholds(expected_metadata_dict, expected_config_dict)
    print(result_dict)
    assert result_dict == expected_result_dict


@pytest.mark.skip
def test_spike_detected(): # Amend after spike code changes


@pytest.mark.skip
def test_create_analysis_fields_dict(mock_record_id, expected_config_dict, expected_result_dict, expected_fields_dict):
    
    fields_dict = qc.create_analysis_fields_dict(mock_record_id, expected_config_dict, expected_result_dict)
    print(fields_dict)
    assert fields_dict == expected_fields_dict


@pytest.mark.skip # Mock onyx call? 
def test_add_qc_analysis_to_onyx(expected_fields_dict, expected_result):
    result = qc.add_qc_analysis_to_onyx(expected_fields_dict)
    
    assert result == expected_result


@pytest.mark.skip # Parametrise error handle tests? 
def test_add_qc_analysis_to_onyx_connection_error(expected_fields_dict, expected_result):
    result = qc.add_qc_analysis_to_onyx(expected_fields_dict)
    
    assert result == expected_result
