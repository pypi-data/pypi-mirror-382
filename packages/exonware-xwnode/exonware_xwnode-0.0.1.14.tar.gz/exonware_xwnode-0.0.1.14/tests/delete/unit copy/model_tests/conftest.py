"""
Model tests specific configuration and fixtures.
"""

import pytest
from pathlib import Path
import sys

# Import parent conftest fixtures
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import *  # Import all parent fixtures 