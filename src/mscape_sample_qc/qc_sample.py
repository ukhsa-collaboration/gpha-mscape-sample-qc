#!/usr/bin/env python3

"""Main script for performing QC on samples submitted to QC. The code
queries the Onyx database to return key metrics on read quality and
classification. Results are returned in json format.
"""

import argparse
import logging
import os
import sys
import mscape_sample_qc.qc_functions as qc
from importlib import resources

def get_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(
        prog = "QC sample", description = """Wrapper used to quality
        check mscape samples against a set of pre-defined criteria.
        Results are returned in a json format. 
        """
    )
    parser.add_argument("--input", "-i", type=str, required=True,
                        help="Sample ID")
    parser.add_argument("--config", "-c", type=str, required=False,
                        help="Path to file with QC criteria")
    parser.add_argument("--output", "-o", type=str, required=True,
                        help="Folder to save QC results to")
    parser.add_argument("--server", "-s", type=str, required=True,
                        choices=["mscape", "synthscape"],
                        help="Specify server code is being run on")

    return parser.parse_args()

def set_up_logger(stdout_file):
    """Creates logger for component - all logging messages go to stdout
    log file, error messages also go to stderr log. If component runs
    correctly, stderr is empty.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    out_handler = logging.FileHandler(stdout_file, mode = "a")
    out_handler.setFormatter(formatter)
    logger.addHandler(out_handler)

    return logger

def main():
    "Main function to process a given sample through QC."

    args = get_args()

    # Set up log file
    log_file = "/home/jovyan/shared-team/component_logs/mscape-sample-qc_logfile.txt"
    set_up_logger(log_file)

    # Use default config if file is not supplied
    if not args.config:
        lib_path = resources.files("mscape_sample_qc") / "lib"
        with resources.as_file(lib_path / "qc_thresholds.yaml") as config_path:
            args.config = str(config_path)
        logging.info("No config file specified, using default parameters from file: %s",
                     args.config)

    else:
        logging.info("Reading qc parameters from file provided: %s", args.config)

    # Read in QC parameters from file
    try:
        threshold_dict = qc.read_config_file(args.config)
    except FileNotFoundError:
        logging.error("Specified config file not found, exiting program")
        return

    ## Set up data needed for report
    # Retrieve classifier calls and metadata for record
    class_df, metadata_dict = qc.retrieve_sample_information(args.input, args.server)

    # Calculate proportions for key metrics based on classification
    # information and add to the metadata dict
    proportion_data = qc.get_read_proportions(class_df)
    metadata_dict.update(proportion_data)

    # Get qc status for relevant sample level metrics
    qc_results = qc.check_thresholds(metadata_dict, threshold_dict['sample_thresholds'])

    # Check spike detected
    qc_results = qc.check_spike_detected(metadata_dict, qc_results)

    # NOTE: Remove this step if decide to only add results to analysis table
    result_file = qc.write_qc_results_to_json(qc_results, args.input, args.output)

    ## Add QC metrics to onyx
    # Set up data for entry in analysis table
    fields_dict = qc.create_analysis_fields_dict(args.input,
                                                 threshold_dict['sample_thresholds'],
                                                 qc_results, args.server)
    #Add data to analysis table
    # TODO: Comment in analysis table step + checks once functions complete and have correct
    # permissions
    result = ""
    #result = qc.add_qc_analysis_to_onyx(fields_dict, args.server)

    return result

if __name__ == '__main__':
    sys.exit(main())
