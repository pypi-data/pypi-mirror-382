import pytest
import pandas as pd
from collections import defaultdict
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import parser  # noqa: E402

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))


def test_always_passes():
    assert True


@pytest.fixture
def bag_parser():
    return parser.BagFileParser(os.path.join(SCRIPT_DIR, 'bagfile', 'bagfile_0.mcap'))


@pytest.fixture
def bag_parser_with_custom_messages():
    """ alternate bagfile with custom ROS2 message types """
    return parser.BagFileParser(os.path.join(SCRIPT_DIR, 'alternate_bagfile', 'alternate_bagfile_0.mcap'),
                                use_pickle_if_exists=False)


@pytest.fixture
def bag_parser_with_pickling_enabled():
    """ alternate bagfile with custom ROS2 message types """
    return parser.BagFileParser(os.path.join(SCRIPT_DIR, 'alternate_bagfile', 'alternate_bagfile_0.mcap'),
                                use_pickle_if_exists=True)


def test_read_messages():
    num_msgs = defaultdict(lambda: 0)
    for topic, msg, timestamp in parser.read_messages(
            os.path.join(SCRIPT_DIR, 'bagfile', 'bagfile_0.mcap')):
        num_msgs[topic] = num_msgs[topic] + 1
        # if topic in '/device/status':
        #     print(f"{topic} [{timestamp}]: '{msg}'")

    print(f'Found {num_msgs}')
    assert num_msgs['/rosout'] == 166
    assert num_msgs['/parameter_events'] == 9
    assert num_msgs['/robot/joint_command'] == 3998
    assert num_msgs['/device/estimated_pose'] == 3998
    assert num_msgs['/device/status'] == 3999
    assert num_msgs['/device/state'] == 3999
    assert num_msgs['/device/command'] == 6


def test_read_messages_through_class(bag_parser):
    num_msgs = defaultdict(lambda: 0)
    for topic, msg, timestamp in bag_parser.read_messages():
        num_msgs[topic] = num_msgs[topic] + 1
        # if topic in '/device/status':
        #     print(f"{topic} [{timestamp}]: '{msg}'")

    print(f'Found {num_msgs}')
    assert num_msgs['/rosout'] == 166
    assert num_msgs['/parameter_events'] == 9
    assert num_msgs['/robot/joint_command'] == 3998
    assert num_msgs['/device/estimated_pose'] == 3998
    assert num_msgs['/device/status'] == 3999
    assert num_msgs['/device/state'] == 3999
    assert num_msgs['/device/command'] == 6


def test_topic_to_dataframe(bag_parser):
    df = bag_parser.topic_to_dataframe(topic='/device/command')
    print(f'\n/device/command = \n{df}')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6
    assert list(df.columns) == ['arg', 'event']

    df = bag_parser.topic_to_dataframe(topic='/device/status')
    print(f'\n/device/status = \n{df}')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3999
    assert 'active_driving_view' in df.columns
    assert 'state' in df.columns

    df = bag_parser.topic_to_dataframe(topic='/robot/joint_command')
    print(f'\n/robot/joint_command = \n{df}')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3998
    print(df.columns)
    assert 'enable.C1_E' in df.columns
    assert 'position.C3_ROLL' in df.columns

    df = bag_parser.topic_to_dataframe(topic='/device/estimated_pose')
    print(f'\n/device/estimated_pose = \n{df}')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3998
    assert 'section.DISTAL.insertion' in df.columns
    assert 'section.PROXIMAL.roll' in df.columns


def test_to_dataframe(bag_parser):
    df = bag_parser.to_dataframe(topics=['/device/command', '/device/status', '/robot/joint_command'])
    print(f'\ncombined dataframe = \n{df}')
    assert '/device/command.event' in df.columns
    assert '/device/status.state' in df.columns
    assert '/robot/joint_command.enable.C1_E' in df.columns


def test_to_dataframe_with_custom_messages(bag_parser_with_custom_messages):
    df = bag_parser_with_custom_messages.to_dataframe(topics=['/robot/joint_state', '/robot/joint_command',
                                                              '/robot/hardware_details'])
    print(f'\ncombined dataframe = \n{df}')

    assert '/robot/hardware_details.serial_number_list' in df.columns
    assert '/robot/joint_state.status_word.C1_A' in df.columns
    assert '/robot/joint_command.position.C1_K' in df.columns


def test_to_dataframe_with_pickling_enabled(bag_parser_with_pickling_enabled):
    df = bag_parser_with_pickling_enabled.to_dataframe(topics=['/robot/joint_state', '/robot/joint_command',
                                                               '/robot/hardware_details'])
    print(f'\npickle file = {bag_parser_with_pickling_enabled._pickle_path}')

    # check that the pickle has actually been generated, and is non-empty
    assert os.path.exists(bag_parser_with_pickling_enabled._pickle_path)
    assert os.path.getsize(bag_parser_with_pickling_enabled._pickle_path) > 0

    assert '/robot/hardware_details.serial_number_list' in df.columns
    assert '/robot/joint_state.status_word.C1_A' in df.columns
    assert '/robot/joint_command.position.C1_K' in df.columns

    # clean up and remove the pickle
    print(f'\nremoving pickle file = {bag_parser_with_pickling_enabled._pickle_path}')
    os.remove(bag_parser_with_pickling_enabled._pickle_path)
    assert not os.path.exists(bag_parser_with_pickling_enabled._pickle_path)


def test_topics(bag_parser):
    topics = bag_parser.topics
    print(topics)
    assert '/rosout' in topics
    assert '/parameter_events' in topics
    assert '/robot/joint_command' in topics
    assert '/device/estimated_pose' in topics
    assert '/device/status' in topics
    assert '/device/state' in topics
    assert '/device/estimated_pose' in topics
    assert '/device/command' in topics


def test_message_counts(bag_parser):
    message_counts = bag_parser.message_counts
    print(message_counts)
    assert message_counts['/device/command'] == 6
    assert message_counts['/device/estimated_pose'] == 3998
    assert message_counts['/device/status'] == 3999
