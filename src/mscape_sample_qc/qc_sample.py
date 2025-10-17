#!/usr/bin/env python3

"""Main script for performing QC on samples submitted to QC. The code
queries the Onyx database to return key metrics on read quality and
classification. Results are returned in json format.
"""

import argparse
import logging
import sys
from importlib import resources
from pathlib import Path

import mscape_sample_qc.qc_functions as qc


def get_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(
        prog="QC sample",
        description="""Wrapper used to quality
        check mscape samples against a set of pre-defined criteria.
        Results are returned in a json format.
        """,
    )
    parser.add_argument("--input", "-i", type=str, required=True, help="Sample ID")
    parser.add_argument(
        "--config", "-c", type=str, required=False, help="Path to file with QC criteria"
    )
    parser.add_argument(
        "--output", "-o", type=str, required=True, help="Folder to save QC results to"
    )
    parser.add_argument(
        "--server",
        "-s",
        type=str,
        required=True,
        choices=["mscape", "synthscape"],
        help="Specify server code is being run on",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--no-onyx",
        required=False,
        action="store_true",
        help="Use this option to only write results to file",
    )
    group.add_argument(
        "--store-onyx",
        required=False,
        action="store_true",
        help="Use this option to store results as an onyx analysis object for later uplaod",
    )
    group.add_argument(
        "--test-onyx",
        required=False,
        action="store_true",
        help="Use this option to do a test upload and check for errors before attempting an upload to onyx",
    )
    group.add_argument(
        "--prod-onyx",
        required=False,
        action="store_true",
        help="Use this option to upload results to onyx",
    )

    return parser.parse_args()


def set_up_logger(stdout_file):
    """Creates logger for component - all logging messages go to stdout
    log file, error messages also go to stderr log. If component runs
    correctly, stderr is empty.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    out_handler = logging.FileHandler(stdout_file, mode="a")
    out_handler.setFormatter(formatter)
    logger.addHandler(out_handler)

    return logger


def main():
    "Main function to process a given sample through QC."

    args = get_args()

    # Set up log file
    log_file = Path(args.output) / f"{args.input}_qc_metrics_log.txt"
    set_up_logger(log_file)

    # Use default config if file is not supplied
    if not args.config:
        config_path = resources.files("mscape_sample_qc.lib").joinpath( "qc_thresholds.yaml")
        args.config = str(config_path)
        logging.info(
            "No config file specified, using default parameters from file: %s", args.config
        )

    else:
        logging.info("Reading qc parameters from file provided: %s", args.config)

    # Read in QC parameters from file
    try:
        threshold_dict = qc.read_config_file(args.config)
    except FileNotFoundError:
        logging.error("Specified config file not found, exiting program")
        exitcode = 1
        return exitcode

    ## Set up data needed for report
    # Retrieve classifier calls and metadata for record
    class_df, exitcode = qc.retrieve_sample_information(args.input, args.server)

    if exitcode == 1:
        return exitcode

    # Calculate proportions for key metrics based on classification
    # information and add to the metadata dict
    qc_results_dict = qc.get_read_proportions(class_df)

    # Get qc status for relevant sample level metrics
    qc_results_dict = qc.check_thresholds(qc_results_dict, threshold_dict["sample_thresholds"])

    # Check spike detected
    qc_results_dict = qc.check_spike_detected(qc_results_dict)

    # NOTE: Remove this step if decide to only add results to analysis table
    qc_result_file = qc.write_qc_results_to_json(qc_results_dict, args.input, args.output)

    if args.no_onyx:
        exitcode = 0
        return str(qc_result_file), exitcode

    ## Add QC metrics to onyx
    # Set up data for entry in analysis table
    headline_result = qc.get_headline_result(qc_results_dict)
    onyx_analysis, exitcode = qc.create_analysis_fields(
        args.input,
        threshold_dict["sample_thresholds"],
        qc_results_dict,
        args.server,
        headline_result,
        str(qc_result_file),
    )

    if exitcode == 1:
        logging.error("Invalid attribute in analysis fields submitted, check logs for details")
        return exitcode

    # Add data to analysis table
    if args.store_onyx:
        onyx_json_file = Path(args.output) / f"{args.input}_qc_metrics_analysis_fields.json"
        result_file = onyx_analysis.write_analysis_to_json(result_file=onyx_json_file)
        logging.info("Onyx analysis fields written to file %s", result_file)
        exitcode = 0
        return str(result_file), exitcode

    if args.test_onyx:
        result, exitcode = onyx_analysis.write_analysis_to_onyx(server=args.server, dryrun=True)

    if args.prod_onyx:
        result, exitcode = onyx_analysis.write_analysis_to_onyx(server=args.server, dryrun=False)

    return result, exitcode


if __name__ == "__main__":
    sys.exit(main())
