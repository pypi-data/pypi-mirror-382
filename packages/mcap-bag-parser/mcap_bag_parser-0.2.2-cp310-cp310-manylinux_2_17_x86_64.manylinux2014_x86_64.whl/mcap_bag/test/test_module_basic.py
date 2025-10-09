#!/usr/bin/env python3
"""
Basic module functionality tests.
"""

import pandas as pd

from mcap_bag.rosx_mcap_adapter import (
    parse_mcap_file,
    create_mega_dataframe,
    parse_mcap_with_fallback,
    ROSX_AVAILABLE
)


def test_module_imports():
    """ simple test that all expected functions are available. """
    assert callable(parse_mcap_file)
    assert callable(create_mega_dataframe)
    assert callable(parse_mcap_with_fallback)
    assert isinstance(ROSX_AVAILABLE, bool)


def test_empty_dataframe_creation():
    """ test creating a mega DataFrame with empty input."""
    empty_topics = {}
    result = create_mega_dataframe(empty_topics)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_mock_dataframe_creation():
    """test creating mega DataFrame with mock data."""

    # Create mock topic DataFrames
    topic_dfs = {
        '/topic1': pd.DataFrame({
            'msg_timestamp': [1000000000, 1000000001],
            'field1': [1.0, 2.0],
            'field2': [10, 20]
        }),
        '/topic2': pd.DataFrame({
            'msg_timestamp': [1000000000, 1000000002],
            'fieldA': ['a', 'b'],
            'fieldB': [100, 200]
        })
    }

    # set proper indices
    for df in topic_dfs.values():
        df.set_index('msg_timestamp', drop=False, inplace=True)

    mega_df = create_mega_dataframe(topic_dfs, fillna=True, generate_relative_timestamps=True)

    assert isinstance(mega_df, pd.DataFrame)
    assert len(mega_df) > 0
    assert 'msg_timestamp' in mega_df.columns
    assert 'rel_timestamp' in mega_df.columns
    assert '/topic1.field1' in mega_df.columns
    assert '/topic2.fieldA' in mega_df.columns


def test_rosx_availability():
    """ super dumb test that we can check rosx availability."""

    # just verify the flag is a boolean - don't assert specific value
    # since it depends on installation
    assert ROSX_AVAILABLE in [True, False]

    if ROSX_AVAILABLE:
        # mock messages
        print("rosx_introspection is available - high performance parsing enabled")
    else:
        print("rosx_introspection not available - will use legacy fallback")
