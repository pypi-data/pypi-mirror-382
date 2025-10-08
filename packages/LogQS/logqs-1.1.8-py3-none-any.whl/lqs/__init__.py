from importlib.metadata import version

__version__ = version("LogQS")

from lqs.client import RESTClient

LogQS = RESTClient
