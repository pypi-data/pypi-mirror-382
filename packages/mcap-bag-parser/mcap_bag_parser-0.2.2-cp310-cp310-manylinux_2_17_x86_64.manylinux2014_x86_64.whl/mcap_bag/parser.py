import functools
import pathlib
import pickle
import time
from collections import defaultdict
from typing import Iterable, Optional

import pandas as pd
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory

MAX_ARRAY_SIZE_TO_SPLIT = 10


def read_messages(bag_file: str,
                  topics: Optional[Iterable[str]] = None,
                  start_time: Optional[int] = None,
                  end_time: Optional[int] = None,
                  log_time_order: bool = True,
                  reverse: bool = False):
    """ iterates through the messages in an MCAP.

    Parameters:
        bag_file: path/name of bag file
        topics: if not None, only messages from these topics will be returned.
        start_time: an integer nanosecond timestamp. messages logged before this timestamp are not included.
        end_time: an integer nanosecond timestamp. messages logged after this timestamp are not included.
        log_time_order: if True, messages will be yielded in ascending log time order.
                        if False, messages will be yielded in the order they appear in the MCAP file.
        reverse: if both `log_time_order` and `reverse` are True, messages will be
                 yielded in descending log time order.
    """
    with open(bag_file, "rb") as fobj:
        reader = make_reader(fobj, decoder_factories=[DecoderFactory()])
        for schema, channel, message, ros_msg in reader.iter_decoded_messages(topics=topics,
                                                                              start_time=start_time,
                                                                              end_time=end_time,
                                                                              log_time_order=log_time_order,
                                                                              reverse=reverse):
            yield channel.topic, ros_msg, message.log_time


def members(msg):
    """ Return the public members of a message """
    return [attr for attr in dir(msg) if
            not callable(getattr(msg, attr)) and
            not attr.startswith("_") and
            attr not in ['real', 'imag', 'numerator', 'denominator']]


# https://stackoverflow.com/a/31174427
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


# https://docs.python.org/3/library/operator.html#operator.attrgetter
def resolve_attr(obj, attr):
    for name in attr.split("."):
        if name in [f'{idx}' for idx in range(100)]:
            # interpret field names of simple numbers as array indices
            try:
                idx = int(name)
                obj = obj[idx]
            except IndexError:
                obj = None
        else:
            obj = getattr(obj, name)
    return obj


def generic_convert(value):
    """
    recursively convert a value to built‑in types without hard‑coding specific attributes, to deal with
    custom messages. this is used for converting a ROS2 message to a dict of built‑in types.
    """
    # base case: built in primitives
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value

    # if the object is already a dict, process it recursively.
    if isinstance(value, dict):
        return {k: generic_convert(v) for k, v in value.items()}

    # if the object is a list or tuple, process each element.
    if isinstance(value, (list, tuple)):
        return [generic_convert(item) for item in value]

    # if the object has a non-empty __dict__, use it.
    if hasattr(value, "__dict__"):
        if value.__dict__:  # non-empty
            return {k: generic_convert(v) for k, v in value.__dict__.items()}
        else:
            # if empty, use members() to extract public attributes
            attrs = members(value)
            if attrs:
                return {attr: generic_convert(getattr(value, attr)) for attr in attrs}

    # fallback: convert to str and hope for the best
    return str(value)


class MessageSchema:
    """ Describes how we decompose a message into a DataFrame entry """

    def __init__(self, topic, msg, prefix_with_topic=False):
        """ Generate the schema from an example message """
        self._topic = topic
        self._name_indexed_fields = []
        self._names = None
        self._field_map = {}  # alternative approach

        if 'name' in members(msg) and isinstance(getattr(msg, 'name'), Iterable):
            # Lots of ROS messages use parallel arrays that are indexed by a `name` array
            # We want to unwrap these for the user
            # TODO: figure out how to handle multiple messages on same topic with different name lists
            # TODO: Push parsing of name-indexed arrays down into recursive approach below so that
            #       it works at more than just the top level
            self._names = getattr(msg, 'name')
            for member_name in members(msg):
                member_var = getattr(msg, member_name)
                if member_name == 'name':
                    pass
                elif isinstance(member_var, Iterable) \
                        and len(member_var) == len(self._names) \
                        and not isinstance(member_var, str):
                    # This field is the same length as the name field, so we will assume they are paired
                    self._name_indexed_fields.append(member_name)
                    for idx, name in enumerate(self._names):
                        self._parse_field(key_name=f'{member_name}.{name}',
                                          data_name=f'{member_name}.{idx}',
                                          var=member_var[idx])
                else:
                    # not name-index, so we'll deal with it separately
                    pass

        for member_name in members(msg):
            member_var = getattr(msg, member_name)
            if member_name in self._name_indexed_fields or member_name == 'name':
                # already dealt with these
                pass
            else:
                self._parse_field(key_name=member_name, data_name=member_name, var=member_var)

        if prefix_with_topic:
            prefixed_field_map = {}
            for column, member_name in self._field_map.items():
                if column in ['msg_timestamp', 'header', 'stamp']:
                    # there are a few special fields that we do NOT want to be unique between topics
                    prefixed_field_map[column] = member_name
                else:
                    prefixed_field_map[f'{self._topic}.{column}'] = member_name
            self._field_map = prefixed_field_map

        # print(f'Header for {self._topic} is {self.header}')

    def _parse_field(self, key_name, data_name, var):
        """ Parse an individual field in the data structure, likely to recurse! """
        # print(f'parse_field({key_name}, {data_name}, {var}')
        # print(f'members = {members(var)}')
        # If this looks like a struct, recurse down into each named member
        if len(members(var)):
            for member in members(var):
                member_var = getattr(var, member)
                self._parse_field(key_name=f'{key_name}.{member}',
                                  data_name=f'{data_name}.{member}',
                                  var=member_var)

        # If this looks like an array, recurse down into each numbered element
        elif isinstance(var, Iterable) \
                and len(var) <= MAX_ARRAY_SIZE_TO_SPLIT \
                and not isinstance(var, str) \
                and key_name not in ['arg', 'changed_parameters', 'deleted_parameters']:
            # TODO: figure out how to handle arrays (such as `arg` field) with variable lengths message to message
            for idx in range(len(var)):
                # recurse down into each sub_member
                self._parse_field(key_name=f'{key_name}.{idx}',
                                  data_name=f'{data_name}.{idx}',
                                  var=var[idx])
            else:  # The thing in the array looks like a scalar, so go ahead and add it to the field map
                self._field_map.update(
                    {f'{key_name}.{idx}': f'{data_name}.{idx}' for idx in range(len(var))})

        # Otherwise, presume that we have reached the end of the tree and add this field to the map
        elif key_name != 'name':
            # No special situations found, so just use each member as its own column
            self._field_map[f'{key_name}'] = f'{data_name}'

    @property
    def header(self):
        return tuple(['msg_timestamp'] + list(self._field_map.keys()))

    def generate_row(self, timestamp, msg):
        """ Use the pre-determined schema to generate one row in the dataframe """
        row_data = [timestamp]

        for header, member_name in self._field_map.items():
            row_data.append(resolve_attr(msg, member_name))

        return row_data

    def generate_dict(self, timestamp, msg):
        """
        convert a message into a dict of builtin Python types. the idea is to make it easier
        to handle custom ROS2 messages, and allow us to inject some conversion logic into the dataframe generation.
        """

        row_dict = {'msg_timestamp': generic_convert(timestamp)}
        for header, member_name in self._field_map.items():
            value = resolve_attr(msg, member_name)
            row_dict[header] = generic_convert(value)

        # create a list row by ordering the values according to the header
        # with this, we can try and maintain compatibility with the generate_row() interface
        row = [row_dict[col] for col in self.header]

        return row


class BagFileParser:
    """ Class-based parser to mimic existing sql-based parser interface """

    def __init__(self, bag_file, use_pickle_if_exists=False):
        self._bag_file: pathlib.Path = bag_file
        assert '.mcap' in str(self._bag_file), 'bag file must be an MCAP file.'
        self._pickle_path = pathlib.Path(str(self._bag_file).replace('.mcap', '.pickle'))

        # Write to/read from a locally stored dataframe for faster post-processing
        self._use_pickle_if_exists: bool = use_pickle_if_exists

    def _get_summary(self):
        with open(self._bag_file, "rb") as fobj:
            reader = make_reader(fobj, decoder_factories=[DecoderFactory()])
            summary = reader.get_summary()
        return summary

    @property
    def pickle_path(self):
        return self._pickle_path

    @pickle_path.setter
    def pickle_path(self, path):
        assert '.pickle' in str(path), 'input path must contain the .pickle extension'
        self._pickle_path = path

    @property
    def message_start_time(self):
        return self._get_summary().statistics.message_start_time

    @property
    def message_end_time(self):
        return self._get_summary().statistics.message_end_time

    @property
    def topics(self):
        summary = self._get_summary()
        topics = [channel.topic for idx, channel in summary.channels.items()]
        return tuple(topics)

    @property
    def message_counts(self):
        summary = self._get_summary()
        message_counts = {}
        for idx, count in summary.statistics.channel_message_counts.items():
            message_counts[summary.channels[idx].topic] = count
        return message_counts

    def read_messages(self, *args, **kwargs):
        return read_messages(self._bag_file, *args, **kwargs)

    def topic_to_dataframe(self, topic: str,
                           start_time: Optional[int] = None,  # [ns]
                           end_time: Optional[int] = None,  # [ns]
                           rel_start_time: Optional[float] = None,  # [s]
                           rel_end_time: Optional[float] = None,):  # [s]
        """ Generate a pandas.DataFrame from a single topic  """
        if rel_start_time is not None:
            start_time = self.message_start_time + int(1E9*rel_start_time)
        if rel_end_time is not None:
            end_time = self.message_start_time + int(1E9*rel_end_time)

        # TODO: fix message counts for loading a partial bagfile
        print(f'Expect {self.message_counts[topic]} messages for {topic}')
        schema = None  # have to wait until we get the first message
        data = []
        msg_count = 0
        for topic, msg, message_time in self.read_messages(topics=[topic], start_time=start_time, end_time=end_time):
            if schema is None:
                # figure out how we are going to represent this type of message in the dataframe
                schema = MessageSchema(topic=topic, msg=msg)
            data.append(schema.generate_row(timestamp=message_time, msg=msg))
            msg_count += 1
            if msg_count % 10000 == 0:
                print(f'Processed {msg_count} messages')
        print('Generating data frame')
        df = pd.DataFrame(data, columns=schema.header)
        df.set_index('msg_timestamp', inplace=True)
        return df

    def has_messages_for_topic(self, topic: str) -> bool:
        return topic in self.message_counts

    def check_for_existing_data(self) -> bool:
        """ Check if the file exists and is non-empty. """
        return pathlib.Path.exists(self._pickle_path) and self._pickle_path.stat().st_size > 0

    def to_dataframe(self, topics: Optional[Iterable[str]] = None,
                     start_time: Optional[int] = None,  # [ns]
                     end_time: Optional[int] = None,  # [ns]
                     rel_start_time: Optional[float] = None,  # [s]
                     rel_end_time: Optional[float] = None,  # [s]
                     fillna=False,
                     generate_relative_timestamps=True):
        """ Generate a pandas.DataFrame from a list of topics

        DataFrame field names will be prepended with the topic name

        Automatically uses high-performance rosx_introspection when available,
        falls back to legacy parser otherwise.
        """

        # Try modern parser first
        try:
            from .rosx_mcap_adapter import parse_mcap_with_fallback

            # Convert relative times to absolute if needed
            abs_start_time = start_time
            abs_end_time = end_time
            if rel_start_time is not None:
                abs_start_time = self.message_start_time + int(1E9 * rel_start_time)
            if rel_end_time is not None:
                abs_end_time = self.message_start_time + int(1E9 * rel_end_time)

            return parse_mcap_with_fallback(
                str(self._bag_file),
                topics=list(topics) if topics else None,
                start_time=abs_start_time,
                end_time=abs_end_time,
                fillna=fillna,
                generate_relative_timestamps=generate_relative_timestamps
            )

        except ImportError:
            print("rosx_introspection not available, using legacy parser")

        # Legacy parser implementation
        start = time.time()

        if rel_start_time is not None:
            start_time = self.message_start_time + int(1E9*rel_start_time)
        if rel_end_time is not None:
            end_time = self.message_start_time + int(1E9*rel_end_time)

        if self._use_pickle_if_exists:
            # Check if we already have the dataframe downloaded. If so, just use that, instead of re-parsing the MCAP.
            if self.check_for_existing_data():
                try:
                    with open(self._pickle_path, 'rb') as f:
                        # The protocol version used is detected automatically, so we do not
                        # have to specify it.
                        mega_data_frame = pickle.load(f)
                        return mega_data_frame
                except EOFError as e:
                    print(f'Pickle file is empty: {e}')
            else:
                print(f'Data not found at {self._pickle_path}. Proceeding to MCAP parsing...')

        if topics is None:
            print(f'Expected message counts are {self.message_counts}')
        else:
            for topic in topics:
                print(f'Expect {self.message_counts[topic]} messages for {topic}')

        schemas = {}
        data_tables = defaultdict(list)
        msg_count = 0
        for topic, msg, message_time in self.read_messages(topics=topics, start_time=start_time, end_time=end_time):
            if topic not in schemas:
                print(f'Trying to infer schema for {topic}')
                # figure out how we are going to represent this type of message in the dataframe
                schemas[topic] = MessageSchema(topic=topic, msg=msg, prefix_with_topic=True)
            data_tables[topic].append(schemas[topic].generate_dict(timestamp=message_time, msg=msg))
            # data_tables[topic].append(schemas[topic].generate_row(timestamp=time, msg=msg))
            msg_count += 1
            if msg_count % 10000 == 0:
                print(f'Processed {msg_count} messages')

        # create a dataframe for each topic, and then concatenate
        print('Generating data frames')
        dataframes = []
        for topic in schemas:
            dataframes.append(pd.DataFrame(data_tables[topic], columns=schemas[topic].header))
            dataframes[-1].set_index('msg_timestamp', drop=False, inplace=True)
        print('Concatenating data frames')
        mega_data_frame = pd.concat(dataframes)
        print('Sorting resultant data frame')
        mega_data_frame.sort_index(inplace=True)

        if generate_relative_timestamps:
            print('Creating relative timestamps')
            mega_data_frame['rel_timestamp'] = (mega_data_frame.index - self.message_start_time) / 1E9
            mega_data_frame.set_index('rel_timestamp', drop=False, inplace=True)
        if fillna:
            print('Filling NaNs')
            mega_data_frame.fillna(method='ffill', inplace=True)

        if self._use_pickle_if_exists:
            # If we've gotten here, it's because we didn't find an existing pickle, so let's create one for this data
            with open(self._pickle_path, 'wb') as f:
                pickle.dump(mega_data_frame, f, pickle.HIGHEST_PROTOCOL)
                print(f'Stored data frame at: {self._pickle_path}')

        print('Done!')

        end = time.time()
        total_parsing_time = end - start
        print(f'Total parsing time: {total_parsing_time} seconds')

        return mega_data_frame
