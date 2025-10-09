"""
AriAI - A flexible chatbot framework supporting multiple AI providers
"""

from .core import AriAI as _AriAI

# Re-export the class at the top level
AriAI = _AriAI

__version__ = "0.1.0"
__all__ = ["AriAI"]