"""End to end test of main.py"""

import argparse
from unittest.mock import patch

from mscape_sample_qc import qc_sample


@patch("onyx_analysis_helper.onyx_analysis_helper_functions.OnyxClient.get")
@patch(
    "argparse.ArgumentParser.parse_args",
    return_value=argparse.Namespace(
        input="ID-12345678",
        config=None,
        output="tests/end_to_end",
        server="synthscape",
        store_onyx=True,
        no_onyx=False,
        test_onyx=False,
        prod_onyx=False,
    ),
)
def test_end_to_end(mock_args, mock_query, mock_onyx_query_response, capsys, caplog):
    # First mock the onyx query results.
    mock_query.return_value = mock_onyx_query_response

    exitcode = qc_sample.main()
    print(caplog.text)
    assert exitcode == 0
