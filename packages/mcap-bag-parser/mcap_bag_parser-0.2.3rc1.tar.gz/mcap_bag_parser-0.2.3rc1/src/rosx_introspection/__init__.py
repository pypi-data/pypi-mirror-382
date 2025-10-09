# import from the pre-built extension (the nanobind module name is 'rosx_introspection')
try:
    from .rosx_introspection import Parser
    __version__ = '2.0.0'
    __all__ = ['Parser', 'parse_ros_message']
except ImportError as e:
    raise ImportError(f"failed to import rosx_introspection extension: {e}")
