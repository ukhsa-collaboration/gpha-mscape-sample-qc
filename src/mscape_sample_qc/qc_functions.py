#!/usr/bin/env python3

"Module containing functions required to QC a sample on mscape."

# Imports
import os
import datetime
import json
import yaml
import numpy as np
import pandas as pd
from onyx import OnyxConfig, OnyxClient, OnyxEnv, OnyxField

# Set up onyx config
CONFIG = OnyxConfig(
    domain=os.environ[OnyxEnv.DOMAIN],
    token=os.environ[OnyxEnv.TOKEN],
)

# Functions
def retrieve_sample_information(record_id: str) -> [pd.DataFrame, pd.DataFrame]:
    """Retrieves sample information for given climb id. Returns two dataframes:
    - One containing classification information for the sample
    - One containing all other metadata for the sample
    """
    # Retrieve record info
    with OnyxClient(CONFIG) as client:
        record = client.get(
            project = "mscape",
            climb_id = record_id)
    
    # Pop the cliassifer information from the record dictionary object and convert to df:
    classifier_df = pd.DataFrame(record.pop('classifier_calls'))
    
    # Remaining keys in dict to dataframe to retrieve metadata:
    #metadata_df = pd.DataFrame.from_dict(record, orient='index').transpose()
    metadata_df = record
    
    return classifier_df, metadata_df

def read_config_file(config_file: os.path) -> dict():
    """Reads config file to get QC criteria to filter sequences against.
    Arguments:
        config_file -- yaml file containing QC criteria

    Returns:
        dictionary of qc criteria
    """
    with open(config_file, encoding="utf-8") as file:
        qc_criteria = yaml.safe_load(file)

    return qc_criteria

def get_read_proportions(class_calls: pd.DataFrame) -> dict():
    """Gets proportions of reads that are in different subsets of the
    data including % unclassified, % host, % spike-in.
    Arguments:
        class_calls -- dataframe containing classifier information for
        reads in the sample
    Returns:
        A dictionary of read proportion statistics for the relevant 
        metrics.
    """
    taxa_dict = {}
    taxa_dict["total_reads"] =  class_calls['count_direct'].sum().item()

    try:
        taxa_dict[f"count_descendants_unclassified"] = class_calls.loc[
            class_calls['human_readable'] == 'unclassified', 'count_descendants'].item()
        taxa_dict[f"percentage_unclassified"] = class_calls.loc[
            class_calls['human_readable'] == 'unclassified', 'percentage'].item()
    except ValueError:
        taxa_dict[f"count_descendants_unclassified"] = 0
        taxa_dict[f"percentage_unclassified"] = 0
    try:
        taxa_dict[f"count_descendants_spike_in"] = class_calls.loc[
            class_calls['human_readable'] == 'Tobacco mosaic virus', 'count_descendants'].item()
        taxa_dict[f"percentage_spike_in"] = class_calls.loc[
            class_calls['human_readable'] == 'Tobacco mosaic virus', 'percentage'].item()
    except ValueError:
        taxa_dict[f"count_descendants_spike_in"] = 0
        taxa_dict[f"percentage_spike_in"] = 0
    try:
        taxa_dict[f"count_descendants_host"] = class_calls.loc[
            class_calls['human_readable'] == 'Homo sapiens', 'count_descendants'].item()
        taxa_dict[f"percentage_host"] = class_calls.loc[
            class_calls['human_readable'] == 'Homo sapiens', 'percentage'].item()
    except ValueError:
        taxa_dict[f"count_descendants_spike_in"] = 0
        taxa_dict[f"percentage_spike_in"] = 0
    try:
        taxa_dict[f"count_descendants_genus"] = class_calls.loc[
            class_calls['rank'] == "G", 'count_descendants'].sum().item()
        taxa_dict[f"percentage_genus"] = (taxa_dict[f"count_descendants_genus"]
                                          / taxa_dict["total_reads"]) * 100
    except ValueError:
        taxa_dict[f"count_descendants_genus"] = 0

    return taxa_dict

def check_thresholds(metadata_dict: dict, threshold_dict: dict) -> dict:
    """For each threshold, check if value falls with pass/warn/fail
    ranges and return value as appropriate.
    Arguments:
        metadata_dict -- dictionary containing metadata information
        threshold_dict -- dictionary containing threshold values to
        compare sample values from metadata_dict against.
    Returns:
        result_dict -- dictionary containing QC result values
    """
    result_dict = {}

    for metric in threshold_dict.keys():
        dict_key = f"{metric}"
        # Large values = better, lower values = fail
        if threshold_dict[metric]['pass'] > threshold_dict[metric]['fail']:
            if metadata_dict[metric] >= threshold_dict[metric]['pass']:
                result_dict[dict_key] = "Pass"
            elif metadata_dict[metric] > threshold_dict[metric]['fail']:
                result_dict[dict_key] = "Warn"
            elif metadata_dict[metric] <= threshold_dict[metric]['fail']:
                result_dict[dict_key] = "Fail"
        # Large values = fail, lower values = pass
        else:
            if metadata_dict[metric] <= threshold_dict[metric]['pass']:
                result_dict[dict_key] = "Pass"
            elif metadata_dict[metric] < threshold_dict[metric]['fail']:
                result_dict[dict_key] = "Warn"
            elif metadata_dict[metric] >= threshold_dict[metric]['fail']:
                result_dict[dict_key] = "Fail"

    return result_dict

def check_spike_detected(metadata_dict: dict, qc_dict: dict) -> dict:
    """Check if spike in detected and add results to qc results dict
    Arguments:
        metadata_dict -- dictionary containing metadata information
        threshold_dict -- dictionary containing threshold values to
        compare sample values from metadata_dict against.
    Returns:
        qc_dict -- dictionary containing QC result values that has
        been updated with spike in detection result.
    """
    if metadata_dict["count_descendants_spike_in"] == 0:
        qc_dict['spike_detected'] = "Fail"
        qc_dict['percentage_spike_in'] = "Not applicable"
    else:
        qc_dict['spike_detected'] = "Pass"

    return qc_dict

def write_qc_results_to_json(qc_dict: dict, sample_id: str, results_dir: os.path) -> os.path:
    """Write qc results dictionary to json output file.
    Arguments:
        qc_dict -- Dictionary containing qc results
        sample_id -- Sample ID to use in file name
        results_dir -- Directory to save results to
    Returns:
        os.path of saved json file
    """
    
    result_file = os.path.join(results_dir, f"{sample_id}_qc_results.json")
    
    with open(result_file, "w", encoding = "utf-8") as file:
        json.dump(qc_dict, file)
    
    return result_file
