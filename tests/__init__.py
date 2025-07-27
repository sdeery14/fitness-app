"""
Test configuration and utilities.
"""
import pytest
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from fitness_app.utils import setup_logging

# Setup logging for tests
setup_logging(level="INFO")
