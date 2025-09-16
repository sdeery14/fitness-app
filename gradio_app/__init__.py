"""
Gradio App - Web interface for the fitness agent.
"""

try:
    from .app import create_app
    __all__ = ['create_app']
except ImportError as e:
    print(f"Warning: gradio_app import failed: {e}")
    __all__ = []
