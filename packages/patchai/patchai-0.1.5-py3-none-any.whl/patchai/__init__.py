"""
PatchAI - AI-powered structured file editor with diff visualization.

Simple example:
    >>> from patchai import PatchAI
    >>> editor = PatchAI("data.json")
    >>> editor.edit("Fix all typos")
    >>> editor.save("fixed.json")

With image reference:
    >>> editor = PatchAI("data.json", image_path="document.jpg")
    >>> editor.edit("Compare with image and correct OCR errors")
    >>> editor.save("corrected.json")

YAML support:
    >>> editor = PatchAI("config.yaml", format="yaml")
    >>> editor.edit("Update database host to localhost")
    >>> editor.save("config.yaml")

Jupyter notebook UI:
    >>> from patchai.jupyter import create_jupyter_editor
    >>> editor = create_jupyter_editor("data.json", image_path="doc.jpg")
    # Beautiful interactive UI appears!
"""

from .editor import PatchAI
from .diff import print_diff, generate_unified_diff, print_summary

__version__ = "0.1.5"
__all__ = ["PatchAI", "print_diff", "generate_unified_diff", "print_summary"]

# Jupyter UI is optional - only import if requested
try:
    from .jupyter import JupyterEditor, create_jupyter_editor
    __all__.extend(["JupyterEditor", "create_jupyter_editor"])
except ImportError:
    pass  # ipywidgets not installed