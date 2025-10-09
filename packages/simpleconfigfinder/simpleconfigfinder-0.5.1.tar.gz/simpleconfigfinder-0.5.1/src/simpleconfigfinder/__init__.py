"""This is a small package with utility functions to find and handle configuration files that are stored upstream from the code."""

from simpleconfigfinder.configfinder import (
    ErrorConfigNotFound as ConfigNotFound,  # add for downward compatibility  # noqa: F401
)
from simpleconfigfinder.configfinder import (
    ErrorConfigNotFound as ErrorConfigNotFound,
)
from simpleconfigfinder.configfinder import (
    combine_dictionaries as combine_dictionaries,
)
from simpleconfigfinder.configfinder import (
    config_finder as config_finder,
)
from simpleconfigfinder.configfinder import (
    config_reader as config_reader,
)
from simpleconfigfinder.configfinder import (
    config_walker as config_walker,
)
from simpleconfigfinder.configfinder import (
    configparser_to_dict as configparser_to_dict,
)
from simpleconfigfinder.configfinder import (
    find_file as find_file,
)
from simpleconfigfinder.configfinder import (
    multi_config_finder as multi_config_finder,
)
