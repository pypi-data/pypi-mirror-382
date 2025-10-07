# __init__.py
import importlib
from typing import TYPE_CHECKING

# all class/functions available
_module_to_names = {
    'single_char_client': ['SingleCharScreenShareClient', 'SingleCharUIClient'],
    'single_char_server': ['SingleCharScreenShareServer'],
}

# make a map from the list: a lookup to import specific files for needed tools, avoiding full library load.
_lazy_mapping = {}
for module_name, symbols in _module_to_names.items():
    for symbol in symbols:
        _lazy_mapping[symbol] = module_name

# all class/functions available when do import freeai_utils
__all__ = sorted(_lazy_mapping.keys())

def __getattr__(name: str):
    if name in _lazy_mapping:
        # Import only the module that contains the requested symbol
        module = importlib.import_module(f"{__name__}.{_lazy_mapping[name]}")
        value = getattr(module, name)
        globals()[name] = value  # Cache in namespace for future calls
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return __all__

#for IDEs suggestions
if TYPE_CHECKING:
    from single_char_client import SingleCharScreenShareClient, SingleCharUIClient
    from single_char_server import SingleCharScreenShareServer