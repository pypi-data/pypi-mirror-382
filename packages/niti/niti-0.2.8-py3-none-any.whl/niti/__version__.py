"""Version information for niti."""

try:
    from niti._version import version as __version__
except ImportError:
    # Fallback for development/editable installs without git
    __version__ = "0.2.6"