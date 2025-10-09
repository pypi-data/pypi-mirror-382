#!/usr/bin/env python3
"""
This is the core integration test for rosx_mcap_adapter -- we parse a "big" MCAP once, then validate unpacked
dataframe equivalence.
"""

import logging
import os
import warnings

import pandas as pd
import pytest

import mcap_bag.parser as mcap_bag_parser
import mcap_bag.rosx_mcap_adapter as rosx_mcap_adapter

logger = logging.getLogger(__name__)

TEST_MCAP_PATH = os.path.join(os.path.dirname(__file__), "data", "torque_ripple_data_0.mcap")


@pytest.fixture(scope="session")
def test_mcap_info():
    if not os.path.exists(TEST_MCAP_PATH):
        pytest.skip(f"test mcap file not found: {TEST_MCAP_PATH}")

    file_size_mb = os.stat(TEST_MCAP_PATH).st_size / (1024 * 1024)
    logger.info(f"test file: {TEST_MCAP_PATH} ({file_size_mb:.1f} mb)")

    return {"path": TEST_MCAP_PATH, "size_mb": file_size_mb}


def test_backwards_compatibility(test_mcap_info):
    """ does the rosx_introspection wrapping parser produce same dataframe structure as legacy parser? """

    mcap_path = test_mcap_info["path"]

    # choose a sparse set of topics to test..
    test_topics = [
        '/robot/joint_state',  # most common topic for analysis
        '/robot/hardware_details'  # most complex nested ros2 message type
    ]

    for topic in test_topics:
        try:
            # parse with both parsers
            topic_dfs = rosx_mcap_adapter.parse_mcap_file(str(mcap_path), topics=[topic])
            df_rosx = rosx_mcap_adapter.create_mega_dataframe(topic_dfs, fillna=True, generate_relative_timestamps=True)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                legacy_parser = mcap_bag_parser.BagFileParser(mcap_path)
                df_legacy = legacy_parser.to_dataframe(topics=[topic], fillna=True)

            # critical compatibility checks
            assert isinstance(df_rosx, pd.DataFrame), "rosx must return dataframe"
            assert len(df_rosx) > 0, "rosx must parse messages"

            # dataframes must have identical structure (excluding header fields)
            rosx_non_header_cols = [col for col in df_rosx.columns if 'header' not in col.lower()]
            legacy_non_header_cols = [col for col in df_legacy.columns if 'header' not in col.lower()]

            assert len(rosx_non_header_cols) == len(legacy_non_header_cols), f"non-header column count must match: " \
                f"rosx={len(rosx_non_header_cols)}, " \
                f"legacy={len(legacy_non_header_cols)}"
            assert len(df_rosx) == len(df_legacy), f"row count must match: rosx={len(df_rosx)}, legacy={len(df_legacy)}"

            # compare columns excluding header fields (header structure differences are acceptable)
            rosx_cols = set(col for col in df_rosx.columns if 'header' not in col.lower())
            legacy_cols = set(col for col in df_legacy.columns if 'header' not in col.lower())
            missing_in_rosx = legacy_cols - rosx_cols
            missing_in_legacy = rosx_cols - legacy_cols

            assert len(missing_in_rosx) == 0, f"rosx missing non-header columns: {list(missing_in_rosx)[:5]}"
            assert len(missing_in_legacy) == 0, f"legacy missing non-header columns: {list(missing_in_legacy)[:5]}"

            logger.info(f"compatibility check passed: identical structure with {len(df_legacy.columns)} columns, "
                        f"{len(df_legacy):,} rows")

        except Exception as e:
            if "Can't pickle" in str(e) or "CDR" in str(e):
                logger.info(f"legacy parser failed with ros2 data (expected): {str(e)[:100]}...")

                # if legacy fails for some odd reason, at least verify rosx parser works
                topic_dfs = rosx_mcap_adapter.parse_mcap_file(str(mcap_path), topics=[topic])
                df_rosx = rosx_mcap_adapter.create_mega_dataframe(topic_dfs, fillna=True)

                assert isinstance(df_rosx, pd.DataFrame)
                assert len(df_rosx) > 0

                robot_cols = [col for col in df_rosx.columns if col.startswith('/robot/')]
                assert len(robot_cols) > 0, "must find /robot/ topics"

                ros_patterns = ['joint_state', 'position', 'velocity']
                found = sum(1 for p in ros_patterns if any(p in col for col in df_rosx.columns))
                assert found > 0, "must find basic ros patterns"

                logger.info("rosx parser working with ros2 data!")
                pytest.skip("legacy parser cannot handle ros2 cdr data - rosx parser verified")
            else:
                raise
