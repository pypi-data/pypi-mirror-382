"""MCAP Bag Parser - Parse MCAP rosbags into pandas dataframes."""

__version__ = '0.2.0'
__all__ = []

# import legacy parser
try:
    from .parser import BagFileParser
    __all__.append('BagFileParser')
except ImportError:
    BagFileParser = None

# pull in adapter funcs
try:
    from .rosx_mcap_adapter import (
        parse_mcap_file,
        create_mega_dataframe,
        parse_mcap_with_fallback,
        ROSX_AVAILABLE
    )
    __all__.extend([
        'parse_mcap_file',
        'create_mega_dataframe',
        'parse_mcap_with_fallback',
        'ROSX_AVAILABLE'
    ])
except ImportError:
    parse_mcap_file = None
    create_mega_dataframe = None
    parse_mcap_with_fallback = None
    ROSX_AVAILABLE = False
