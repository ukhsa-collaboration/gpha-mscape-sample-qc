#!/usr/bin/env python3

"Module containing functions required to QC a sample on mscape."

# Imports
import datetime
import json
import logging
import os
import time
from importlib.metadata import version
from onyx_analysis_helper import onyx_analysis_helper_functions as oa

import pandas as pd
import yaml
from onyx import OnyxClient, OnyxConfig, OnyxEnv
from onyx.exceptions import OnyxClientError, OnyxConfigError, OnyxConnectionError, OnyxHTTPError

# Set up onyx config
CONFIG = OnyxConfig(
    domain=os.environ[OnyxEnv.DOMAIN],
    token=os.environ[OnyxEnv.TOKEN],
)

# Functions
def retrieve_sample_information(record_id: str, server: str) -> [pd.DataFrame, dict]:
    """Retrieves sample information for given climb id. Returns two dataframes:
    - One containing classification information for the sample
    - One containing all other metadata for the sample
    """
    # Retrieve record info
    with OnyxClient(CONFIG) as client:
        metadata_dict = client.get(
            project = server,
            climb_id = record_id)

    # Pop the classifier information from the record dictionary object and convert to df:
    classifier_df = pd.DataFrame(metadata_dict.pop('classifier_calls'))

    return classifier_df, metadata_dict

def read_config_file(config_file: os.path) -> dict:
    """Reads config file to get QC criteria to filter sequences against.
    Arguments:
        config_file -- yaml file containing QC criteria

    Returns:
        dictionary of qc criteria
    """
    with open(config_file) as file:
        qc_criteria = yaml.safe_load(file)

    return qc_criteria

def get_read_proportions(class_calls: pd.DataFrame) -> dict:
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
    taxa_dict['total_reads'] =  class_calls['count_direct'].sum().item()

    try:
        taxa_dict['count_descendants_unclassified'] = class_calls.loc[
            class_calls['taxon_id'] == 0, 'count_descendants'].item()
        taxa_dict['percentage_unclassified'] = class_calls.loc[
            class_calls['taxon_id'] == 0, 'percentage'].item()
    except ValueError:
        taxa_dict['count_descendants_unclassified'] = 0
        taxa_dict['percentage_unclassified'] = 0

    try:
        taxa_dict['count_descendants_spike_in'] = class_calls.loc[
            class_calls['taxon_id'] == 12242, 'count_descendants'].item()
        taxa_dict['percentage_spike_in'] = class_calls.loc[
            class_calls['taxon_id'] == 12242, 'percentage'].item()
    except ValueError:
        taxa_dict['count_descendants_spike_in'] = 0
        taxa_dict['percentage_spike_in'] = 0

    try:
        taxa_dict['count_descendants_host'] = class_calls.loc[
            class_calls['taxon_id'] == 9606, 'count_descendants'].item()
        taxa_dict['percentage_host'] = class_calls.loc[
            class_calls['taxon_id'] == 9606, 'percentage'].item()
    except ValueError:
        taxa_dict['count_descendants_host'] = 0
        taxa_dict['percentage_host'] = 0

    try:
        taxa_dict['count_descendants_genus'] = class_calls.loc[
            class_calls['rank'] == "G", 'count_descendants'].sum().item()
        taxa_dict['percentage_genus'] = (taxa_dict['count_descendants_genus']
                                          / taxa_dict['total_reads']) * 100
    except ValueError:
        taxa_dict['count_descendants_genus'] = 0

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

    for metric in threshold_dict:
        result_dict[f'{metric}'] = metadata_dict[metric]
        dict_key = f"{metric}_qc"
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
    if metadata_dict['count_descendants_spike_in'] == 0:
        qc_dict['spike_detected'] = "Fail"
        qc_dict['percentage_spike_in_qc'] = "NA"
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

def write_onyx_fields_to_json(fields_dict: dict, sample_id: str, results_dir: os.path) -> os.path:
    "Write onyx analysis details to json output file."
    result_file = os.path.join(results_dir, f"{sample_id}_qc_results_onyx.json")

    with open(result_file, "w", encoding = "utf-8") as file:
        json.dump(fields_dict, file)

    return result_file

def create_analysis_fields(record_id: str, qc_thresholds: dict,
                           qc_results: dict, server: str) -> dict:
    """Set up fields dictionary used to populate analysis table containing
    QC metrics.
     Arguments:
        record_id -- Climb ID for sample
        qc_thresholds -- Dictionary containing qc criteria used to generate metrics
        qc_results -- Dictionary containing qc results
        server -- Server code is running on, one of "mscape" or "synthscape"
    Returns:
        onyx_analysis -- Class containing required fields for input to onyx
                         analysis table
    """
    if "Fail" in qc_results.values() or "Warn" in qc_results.values():
        headline_result = "Warning: Check QC results before use"
    else:
        headline_result = "QC results passed thresholds"

    onyx_analysis = oa.OnyxAnalysis()
    onyx_analysis.add_analysis_details(
        analysis_name="ukhsa-classifier-qc-metrics",
        analysis_description="""This is an analysis to generate QC statistics for individual samples"""
    )
    onyx_analysis.add_package_metadata(package_name = "mscape-sample-qc")
    onyx_analysis.add_methods(methods_dict = qc_thresholds)
    onyx_analysis.add_results(top_result=headline_result, results_dict = qc_results)
    onyx_analysis.add_server_records(sample_id = record_id, server_name = "synthscape")

    return onyx_analysis

def add_qc_analysis_to_onyx(fields_dict: dict, server: str, dryrun: bool) -> str:
    """Attempts to add QC information as an analysis table to onyx. If
    3 attempts fail due to connections issues the program will exit
    and returns an error. Errors requiring manual fixing are also raised.

    Arguments:
        fields_dict -- Dictionary containing required fields for input to analysis table
    Returns:
        Name of analysis
    """
    # Test connection/creation of table then add table to onyx?

    connection_attempts = 1
    success = False

    while success is False:
        try:
            logging.debug("Attempting connection to Onyx. Attempt number %s",
                          connection_attempts)

            with OnyxClient(CONFIG) as client:
                result = client.create_analysis(
                    project=server,
                    fields=fields_dict,
                    test=dryrun
        )
            success = True

            logging.debug("Successful connection to onyx")

            return result

        except OnyxConnectionError as exc:
            if connection_attempts < 3:
                connection_attempts += 1
                logging.debug("OnyxConnectionError: %s. Retrying connection in 5 seconds",
                              exc)
                time.sleep(5)

            else:
                logging.error("""OnyxConnectionError: %s. Connection to Onyx failed %s times,
                              exiting program""",
                              exc, connection_attempts)

                return

        except OnyxConfigError as exc:
            logging.error("""OnyxConfigError: %s. Check credentials and details in OnyxConfig
                          are correct. See
                          https://climb-tre.github.io/onyx-client/api/documentation/exceptions/
                          for more details.""",
                          exc)
            return

        except OnyxClientError as exc:
            logging.error("""OnyxClientError: %s. Check calls to OnyxClient are correct
                          and required arguments e.g. climb_id are present. See
                          https://climb-tre.github.io/onyx-client/api/documentation/exceptions/
                          for more details""",
                          exc)
            return

        except OnyxHTTPError as exc:
            logging.error("""OnyxHTTPError: %s. See
                          https://climb-tre.github.io/onyx-client/api/documentation/exceptions/
                          for more details""",
                          exc.response.json())

            return

        except Exception as exc:
            logging.error("""Unhandled error: %s. See
                          https://climb-tre.github.io/onyx-client/api/documentation/exceptions/
                          for more details""",
                          exc)
            return
