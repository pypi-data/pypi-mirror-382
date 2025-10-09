# Config Finder
Finds a configuration file (e.g. pyproject.toml) and returns some sub-configuration by only using python standard libraries.


Supported formats:

* [TOML](https://en.wikipedia.org/wiki/TOML)
* [JSON](https://en.wikipedia.org/wiki/JSON)
* [INI](https://en.wikipedia.org/wiki/INI_file)
* [YAML](https://en.wikipedia.org/wiki/YAML) (see [Documentation](https://fabfabi.github.io/simpleconfigfinder/) how to enable)


## Use Case
When defining machine learning projects and handling the project configuration by e.g. a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) (e.g. with [Astral UV](https://docs.astral.sh/uv/) or  [Poetry](https://python-poetry.org/)) you can utilize the configuration files to define and store important variables.

Instead of defining global variables in your code or using [dotenv](https://pypi.org/project/python-dotenv/), a configuration file such as the pyproject.toml can be used for those values.

## Example
Instead of defining global variables, just define these parameters in the pyproject.toml

    [tool.some_tool]
    key1 = "some_value_1"
    key2 = "some_value_2"

    [tool.some_tool.default_config]
    important_key = "some_value"

    [tool.some_tool.special_config]
    important_key = "another_value"



To get the key for your `default_config` just call

```python
find_configuration("pyproject.toml", ["tool", "some_tool", "default_config", "important_key"])
```

    "some_value"

and respectively for your `special_config` use

```python
find_configuration("pyproject.toml", ["tool", "some_tool", "special_config", "important_key"])
```

    "another_value"

Or you could get one full set of the configuration as dictionary via

```python
find_configuration("pyproject.toml", ["tool", "some_tool", "special_config"])
```

    { "important_key" : "another_value" }


[Link to full documentation](https://fabfabi.github.io/simpleconfigfinder/)