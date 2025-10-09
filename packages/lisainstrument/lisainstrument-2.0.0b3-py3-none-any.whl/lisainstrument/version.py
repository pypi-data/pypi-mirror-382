"""Module to manage version information"""

import importlib

# Note: setting __version__ with `poetry dynamic-versioning` plugin seems broken

try:
    metadata = importlib.metadata.metadata("lisainstrument").json
    __author__ = metadata["author"]
    __email__ = metadata["author_email"]
    __version__ = str(metadata["version"])
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
