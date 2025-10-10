"""
#exonware/xwnode/src/exonware/xwnode/common/utils/__init__.py

Utils module for xwnode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.15
"""

# Import and export main components
from pathlib import Path
import importlib

# Auto-discover and import all modules
_current_dir = Path(__file__).parent
for _file in _current_dir.glob('*.py'):
    if _file.name != '__init__.py' and not _file.name.startswith('_'):
        _module_name = _file.stem
        try:
            globals()[_module_name] = importlib.import_module(f'.{_module_name}', package=__name__)
        except ImportError:
            pass

__all__ = []
