#!/usr/bin/env python3
"""
Simplified ROS2 MCAP parser using a wrapper around rosx_introspection library.
This adapter aims to provide backwards compatibility with our legacy MCAP parser, to support the same API for analysis scripts.
"""

import io
import logging
import struct
import time
import types
from collections import defaultdict
from typing import Dict, Optional, Iterable, List, Tuple

import msgpack
import numpy as np
import pandas as pd
from mcap.reader import make_reader

try:
    import rosx_introspection
    ROSX_AVAILABLE = True
except ImportError:
    rosx_introspection = None
    ROSX_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_name_mapping(df: pd.DataFrame) -> Dict[str, List[Tuple[int, str]]]:
    """
    Extract name mappings from dataframe columns for backwards compatibility.
    maps array indices to joint names (e.g., effort[0] --> effort.C1_A).
    """
    name_cols = sorted([col for col in df.columns if col.startswith('/name[')])

    if not name_cols or len(df) == 0:
        return {}

    first_row = df.iloc[0]
    name_mapping = []

    for col in name_cols:
        # extract index from /name[0] format
        idx_str = col[6:-1]  # extract "0" from "/name[0]"
        try:
            idx = int(idx_str)
            name = first_row[col]
            if pd.notna(name):
                name_mapping.append((idx, name))
        except (ValueError, KeyError):
            continue

    return {'': name_mapping} if name_mapping else {}


def clean_cdr_string(value):
    """
    clean cdr-encoded string artifacts from rosx_introspection output.
    uses struct to properly decode cdr format strings.
    """
    if not isinstance(value, str):
        return value

    # check if this looks like cdr-encoded string data (starts with length bytes)
    if len(value) > 4 and ord(value[0]) < 32 and ord(value[1]) == 0:
        try:
            # cdr format: little-endian 4-byte length + string + padding
            data = value.encode('latin1')  # preserve raw bytes
            length = struct.unpack('<I', data[:4])[0]  # little-endian uint32

            if 4 + length <= len(data):
                # extract string content
                string_data = data[4:4 + length]
                # decode as utf-8, removing null terminators
                cleaned = string_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
                if cleaned and cleaned.isprintable():
                    return cleaned
        except (struct.error, UnicodeDecodeError, ValueError):
            pass

    return value


def reconstruct_nested_arrays(df: pd.DataFrame) -> pd.DataFrame:
    """
    reconstruct nested message arrays to match legacy format.
    converts flattened rosx columns like /array_name/field1, /array_name/field2
    back to a single /array_name column containing list of objects.
    """
    # identify nested patterns - columns with shared base paths
    nested_patterns = {}

    for col in df.columns:
        if col.count('/') >= 2:  # at least /base_path/field_name
            parts = col.split('/')
            if len(parts) >= 3:
                base_path = '/'.join(parts[:-1])
                field_name = parts[-1]

                if base_path not in nested_patterns:
                    nested_patterns[base_path] = []
                nested_patterns[base_path].append((col, field_name))

    # reconstruct arrays from flattened columns
    for base_path, field_info in nested_patterns.items():
        if len(field_info) < 2:  # need multiple fields to reconstruct
            continue

        columns = [col for col, _ in field_info]

        # create array column with list of dynamic objects
        reconstructed_data = []
        for idx in range(len(df)):
            # create object with all field values
            obj_dict = {}
            for col, field_name in field_info:
                raw_value = df[col].iloc[idx]
                # clean potential cdr string artifacts
                obj_dict[field_name] = clean_cdr_string(raw_value)

            # only create object if we have meaningful data
            if any(str(v).strip() for v in obj_dict.values() if v is not None):
                # create object using built-in types with proper repr
                class_name = base_path.split('/')[-1].title().replace('_', '')

                # create dynamic class inheriting from SimpleNamespace for clean repr
                obj_class = type(class_name, (types.SimpleNamespace,), {
                    '__repr__': lambda self: f"{class_name}({', '.join(f'{k}={v}' for k, v in self.__dict__.items())})"
                })

                obj = obj_class(**obj_dict)
                reconstructed_data.append([obj])  # single-element array
            else:
                reconstructed_data.append([])  # empty array

        # replace flattened columns with single array column
        df[base_path] = reconstructed_data
        df = df.drop(columns=columns)

    return df


def apply_name_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """
    apply name-based remapping to dataframe columns;
    renames columns like /effort[0] to /effort.C1_A based on /name array.
    also handles nested message array reconstruction for backwards compatibility.
    """
    # first, try to reconstruct nested arrays before other processing
    df = reconstruct_nested_arrays(df)

    mapping = extract_name_mapping(df)

    if not mapping or '' not in mapping:
        # still apply format conversions even without name mapping
        # Remove leading slash from all columns for backwards compatibility
        df.columns = [col[1:] if col.startswith('/') else col for col in df.columns]
        # Convert path separators from / to . for nested fields
        df.columns = [col.replace('/', '.') for col in df.columns]
        return df

    name_list = mapping['']
    rename_dict = {}

    # find all array columns that should be renamed
    for col in df.columns:
        if col.startswith('/name['):
            continue  # skip name columns themselves

        if '[' in col and ']' in col:
            prefix = col[:col.index('[')]
            idx_part = col[col.index('[') + 1:col.index(']')]

            try:
                idx = int(idx_part)
                # Find corresponding name
                for map_idx, name in name_list:
                    if map_idx == idx:
                        new_name = f"{prefix}.{name}"
                        rename_dict[col] = new_name
                        break
            except ValueError:
                continue

    # Apply renaming
    if rename_dict:
        df = df.rename(columns=rename_dict)

    # Drop name columns as they're no longer needed
    name_cols_to_drop = [col for col in df.columns if col.startswith('/name[')]
    if name_cols_to_drop:
        df = df.drop(columns=name_cols_to_drop)

    # Remove leading slash from all columns for backwards compatibility
    # Legacy parser doesn't include leading slash in field names
    df.columns = [col[1:] if col.startswith('/') else col for col in df.columns]

    # Convert path separators from / to . for nested fields (like header/stamp/sec)
    # This matches legacy parser format
    df.columns = [col.replace('/', '.') for col in df.columns]

    return df


def parse_mcap_file(
    mcap_file: str,
    topics: Optional[Iterable[str]] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> Dict[str, pd.DataFrame]:
    """
    parse ros2 mcap file using rosx_introspection.

    args:
        mcap_file: path to mcap file
        topics: optional topic filter
        start_time/end_time: optional time filters in nanoseconds

    returns:
        dict mapping topic names to dataframes
    """
    if not ROSX_AVAILABLE:
        raise ImportError("rosx_introspection not available")
    else:
        print('Using rosx_introspection for MCAP parsing...')

    topics_filter = set(topics) if topics else None

    with open(mcap_file, "rb") as f:
        reader = make_reader(f)

        parsers = {}
        topic_data = defaultdict(list)
        message_count = 0
        start_parse_time = time.perf_counter()

        # simple progress tracking

        # process all messages
        for schema, channel, message in reader.iter_messages(
            topics=topics_filter,
            start_time=start_time,
            end_time=end_time
        ):
            # create parser for new channels
            if channel.id not in parsers:
                try:
                    parsers[channel.id] = rosx_introspection.Parser(
                        topic_name="",  # No prefix needed
                        type_name=schema.name,
                        schema=schema.data.decode("utf-8")
                    )
                except Exception:
                    continue  # skip unparseable schemas

            # parse message
            parser = parsers.get(channel.id)
            if not parser:
                continue

            try:
                # parse to msgpack and unpack
                msgpack_bytes = parser.parse_to_msgpack(message.data)
                row_data = {'msg_timestamp': message.log_time}

                # unpack msgpack efficiently
                unpacker = msgpack.Unpacker(io.BytesIO(msgpack_bytes), raw=False)
                map_size = unpacker.read_map_header()

                for _ in range(map_size):
                    key = unpacker.unpack()
                    value = unpacker.unpack()

                    # convert numpy arrays to lists
                    if isinstance(value, np.ndarray):
                        value = value.item() if value.size == 1 else value.tolist()

                    # clean potential cdr string artifacts
                    value = clean_cdr_string(value)

                    row_data[key] = value

                topic_data[channel.topic].append(row_data)
                message_count += 1

                # simple progress reporting every 10,000 messages
                if message_count % 10000 == 0:
                    elapsed_time = time.perf_counter() - start_parse_time
                    messages_per_sec = message_count / elapsed_time if elapsed_time > 0 else 0

                    # compute a simple SWAG ETA based on file position
                    try:
                        current_pos = f.tell()
                        file_size = f.seek(0, 2)
                        f.seek(current_pos)

                        if file_size > 0:
                            progress_pct = (current_pos / file_size) * 100
                            if progress_pct > 10:  # only show ETA after 10% progress
                                remaining_pct = 100 - progress_pct
                                eta_seconds = (elapsed_time * remaining_pct) / progress_pct
                                print(f"Processed {message_count:,} messages ({progress_pct:.0f}%, "
                                      f"estimated time remaining: {eta_seconds:.0f}s)")
                            else:
                                print(f"Processed {message_count:,} messages ({messages_per_sec:.0f} msg/s)")
                        else:
                            print(f"Processed {message_count:,} messages ({messages_per_sec:.0f} msg/s)")
                    except Exception:
                        print(f"Processed {message_count:,} messages ({messages_per_sec:.0f} msg/s)")

            except Exception:
                pass  # skip bad messages

        print(f'Parsed {message_count} messages from {len(topic_data)} topics')
        # convert to dataframes with name mapping
        dataframes = {}
        for topic, rows in topic_data.items():
            if rows:
                df = pd.DataFrame(rows)
                df.set_index('msg_timestamp', drop=False, inplace=True)

                # apply name-based column remapping for backwards compatibility
                df = apply_name_mapping(df)

                if not df.index.is_monotonic_increasing:
                    df.sort_index(inplace=True)
                dataframes[topic] = df

        return dataframes


def create_mega_dataframe(
    topic_dataframes: Dict[str, pd.DataFrame],
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    fillna: bool = True,
    generate_relative_timestamps: bool = True,
) -> pd.DataFrame:
    """
    combine topic dataframes into single dataframe with topic-prefixed columns.

    args:
        topic_dataframes: dict of topic -> dataframe
        fillna: forward fill nan values
        generate_relative_timestamps: add rel_timestamp column

    returns:
        combined dataframe
    """
    if not topic_dataframes:
        return pd.DataFrame()

    # prefix columns with topic names
    processed = []
    for topic, df in topic_dataframes.items():
        if df.empty:
            continue

        df_copy = df.copy()

        # ensure msg_timestamp exists
        if 'msg_timestamp' not in df_copy.columns:
            df_copy['msg_timestamp'] = df_copy.index

        # prefix all columns except msg_timestamp
        rename = {col: f"{topic}.{col}"
                  for col in df_copy.columns
                  if col != 'msg_timestamp'}
        df_copy.rename(columns=rename, inplace=True)

        processed.append(df_copy)

    # combine dataframes for compatibility
    if len(processed) == 1:
        mega_df = processed[0]
    else:
        # reset indices for concatenation
        for df in processed:
            df.reset_index(drop=True, inplace=True)

        # concatenate and group by timestamp
        mega_df = pd.concat(processed, axis=0, sort=False)
        mega_df = mega_df.groupby('msg_timestamp', as_index=False).first()
        mega_df.set_index('msg_timestamp', drop=False, inplace=True)
        mega_df.sort_index(inplace=True)

    # apply time filtering
    if start_time is not None:
        mega_df = mega_df[mega_df.index >= start_time]
    if end_time is not None:
        mega_df = mega_df[mega_df.index <= end_time]

    # add relative timestamps
    if generate_relative_timestamps and not mega_df.empty:
        # NOTE: the legacy parser uses msg_timestamp index directly vs message_start_time from MCAP summary
        # for backwards compatibility, we need to use the same computation.
        # so we can just use index.min() as the start time (first message time)
        message_start_time = mega_df.index.min()
        mega_df['rel_timestamp'] = (mega_df.index - message_start_time) / 1e9

        # set rel_timestamp as the index, matching legacy behavior
        mega_df.set_index('rel_timestamp', drop=False, inplace=True)

    # forward fill NaN values, like before
    if fillna:
        mega_df.ffill(inplace=True)

    return mega_df


def parse_mcap_with_fallback(
    mcap_file_path: str,
    topics: Optional[Iterable[str]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    parse mcap with automatic fallback to legacy parser.
    returns dataframe directly (and not dict of dataframes, which is what the rosx_introspection pkg natively outputs).
    """
    try:
        # try rosx parser first
        parsing_start_time = time.perf_counter()
        topic_dfs = parse_mcap_file(mcap_file_path, topics=topics)
        parsing_end_time = time.perf_counter()
        print(f'rosx_introspection wrapper parsed {len(topic_dfs)} topics successfully.')
        print(f'The parsing took {parsing_end_time - parsing_start_time:.2f} seconds.')
        return create_mega_dataframe(
            topic_dfs,
            fillna=kwargs.get('fillna', True),
            generate_relative_timestamps=kwargs.get('generate_relative_timestamps', True)
        )
    except Exception as e:
        # fall back to legacy parser
        print(f'rosx failed: {e}, using legacy parser')
        from .parser import BagFileParser
        parser = BagFileParser(mcap_file_path)
        return parser.to_dataframe(topics=topics, **kwargs)


# backwards compatibility aliases
parse_mcap_file_with_rosx = parse_mcap_file
