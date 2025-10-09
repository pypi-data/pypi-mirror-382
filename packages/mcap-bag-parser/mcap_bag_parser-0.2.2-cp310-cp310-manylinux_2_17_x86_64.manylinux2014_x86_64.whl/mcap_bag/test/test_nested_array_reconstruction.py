#!/usr/bin/env python3
"""
unit test for nested array reconstruction functionality.
tests that flattened rosx columns are properly reconstructed into legacy array format.
"""

import pandas as pd
import pytest

from mcap_bag.rosx_mcap_adapter import reconstruct_nested_arrays, clean_cdr_string


def test_reconstruct_serial_number_list():
    """test reconstruction of ComponentSerialNumber[] array from flattened columns."""
    # create test dataframe with flattened rosx columns
    df = pd.DataFrame({
        'msg_timestamp': [123456789],
        '/robot/hardware_details/header/seq': [0],
        '/robot/hardware_details/serial_number_list/component_name': ['C1_A'],
        '/robot/hardware_details/serial_number_list/serial_number': ['2147697738'],
        '/robot/joint_state/position': [1.23]
    })

    # apply reconstruction
    result_df = reconstruct_nested_arrays(df)

    # verify reconstruction
    assert '/robot/hardware_details/serial_number_list' in result_df.columns
    assert '/robot/hardware_details/serial_number_list/component_name' not in result_df.columns
    assert '/robot/hardware_details/serial_number_list/serial_number' not in result_df.columns

    # check reconstructed data
    serial_data = result_df['/robot/hardware_details/serial_number_list'].iloc[0]
    assert isinstance(serial_data, list)
    assert len(serial_data) == 1

    obj = serial_data[0]
    assert hasattr(obj, 'component_name')
    assert hasattr(obj, 'serial_number')
    assert obj.component_name == 'C1_A'
    assert obj.serial_number == '2147697738'


def test_reconstruct_multiple_nested_arrays():
    """test reconstruction handles multiple different nested arrays."""
    df = pd.DataFrame({
        'msg_timestamp': [123456789],
        '/robot/array1/field_a': ['value_a1'],
        '/robot/array1/field_b': ['value_b1'],
        '/robot/array2/field_x': ['value_x1'],
        '/robot/array2/field_y': ['value_y1'],
        '/robot/scalar_field': ['scalar_value']
    })

    result_df = reconstruct_nested_arrays(df)

    # verify both arrays reconstructed
    assert '/robot/array1' in result_df.columns
    assert '/robot/array2' in result_df.columns
    assert '/robot/scalar_field' in result_df.columns  # unchanged

    # check array1
    array1_data = result_df['/robot/array1'].iloc[0]
    assert isinstance(array1_data, list)
    assert len(array1_data) == 1
    assert array1_data[0].field_a == 'value_a1'
    assert array1_data[0].field_b == 'value_b1'

    # check array2
    array2_data = result_df['/robot/array2'].iloc[0]
    assert isinstance(array2_data, list)
    assert len(array2_data) == 1
    assert array2_data[0].field_x == 'value_x1'
    assert array2_data[0].field_y == 'value_y1'


def test_no_reconstruction_for_single_fields():
    """test that single fields are not reconstructed as arrays."""
    df = pd.DataFrame({
        'msg_timestamp': [123456789],
        '/robot/hardware_details/header/seq': [0],
        '/robot/single_field': ['value']
    })

    result_df = reconstruct_nested_arrays(df)

    # single fields should remain unchanged
    assert '/robot/hardware_details/header/seq' in result_df.columns
    assert '/robot/single_field' in result_df.columns
    assert len(result_df.columns) == 3  # no new columns created


def test_empty_data_handling():
    """test reconstruction handles empty/null data properly."""
    df = pd.DataFrame({
        'msg_timestamp': [123456789],
        '/robot/array1/field_a': [None],
        '/robot/array1/field_b': [''],
        '/robot/array2/field_x': ['  '],  # whitespace only
        '/robot/array2/field_y': [None]
    })

    result_df = reconstruct_nested_arrays(df)

    # arrays with only empty data should create empty arrays
    array1_data = result_df['/robot/array1'].iloc[0]
    array2_data = result_df['/robot/array2'].iloc[0]

    assert isinstance(array1_data, list)
    assert isinstance(array2_data, list)
    assert len(array1_data) == 0
    assert len(array2_data) == 0


def test_cdr_string_cleaning():
    """test cdr-encoded string cleaning functionality."""
    # test normal strings (should be unchanged)
    assert clean_cdr_string('normal_string') == 'normal_string'
    assert clean_cdr_string('') == ''
    assert clean_cdr_string(123) == 123  # non-strings unchanged

    # test cdr-encoded string (like from rosx_introspection)
    cdr_string = '\x05\x00\x00\x00C1_A\x00\x00\x00'
    cleaned = clean_cdr_string(cdr_string)
    assert cleaned == 'C1_A'

    # test another cdr-encoded string format
    cdr_string2 = '\x08\x00\x00\x00TestName\x00\x00\x00\x00'
    cleaned2 = clean_cdr_string(cdr_string2)
    assert cleaned2 == 'TestName'


def test_cdr_string_in_reconstruction():
    """test that cdr string cleaning works during array reconstruction."""
    # create test dataframe with cdr-encoded strings
    df = pd.DataFrame({
        'msg_timestamp': [123456789],
        '/robot/hardware_details/serial_number_list/component_name': ['\x05\x00\x00\x00C1_A\x00\x00\x00'],
        '/robot/hardware_details/serial_number_list/serial_number': ['2147697738']
    })

    result_df = reconstruct_nested_arrays(df)

    # verify cdr cleaning happened during reconstruction
    serial_data = result_df['/robot/hardware_details/serial_number_list'].iloc[0]
    assert len(serial_data) == 1
    obj = serial_data[0]
    assert obj.component_name == 'C1_A'  # should be cleaned
    assert obj.serial_number == '2147697738'  # should be unchanged


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
