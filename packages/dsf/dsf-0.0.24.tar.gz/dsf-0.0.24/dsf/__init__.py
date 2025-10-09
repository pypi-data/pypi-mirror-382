from ._version import __version__
from .datasets import load, datasets, dataset_table
from .hybrid_nb import HybridNB

__all__ = ["load", "datasets", "dataset_table"]

__doc__ = f"""
DSF package: Example datasets for Python users

Available datasets:
{dataset_table()}

# Load a dataset from the DSF package as a pandas DataFrame

>>> import dsf
>>> df = dsf.load('<dataset_name>')  # Load a dataset as a pandas DataFrame
>>> dsf.version()  # DSF version {__version__}