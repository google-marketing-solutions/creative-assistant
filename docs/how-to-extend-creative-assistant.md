# How to add extra functionality to Creative Assistant

Creative Assistant is build to be extendable via a system of plugins.

To make a plugin available to Creative Assistant follow the steps below:

1. Create Langhchain tool by inheriting `langchain_core.tools.BaseTool` class.

2. Explose this tool as an entry point for Creative Assistant. Add the following
lines to your `pyproject.toml` file:


```
[project.entry-points.creative_assistant]
your_plugin_name = "your_library_name.your_tools_module_name"
```

3. Install the tool in the same environment as creative assistant.


## Example
All this is better to illustrate with an example.

Suppose you want to create a tool called `my_awesome_tool`.

* You need to create a folder `my_awesome_library` with a file called `tools.py`
* Inside `tools.py` you add tool definition:

  ```
  import langchain_core
  import pydantic


  class MyAwesomeToolInput(pydantic.BaseModel):
    """Input for my awesome tool question."""

    question: str = pydantic.Field(description='question for the tool')


  class MyAwesomeTool(langchain_core.tools.BaseTool):
    name: str = 'my_awesome_tool'
    description: str = 'tool description here, the descriptive the better'
    args_schema: type[pydantic.BaseModel] = MyAwesomeToolInput

    def _run(self, question):
      # Actual work the tool does.
  ```

* Create `pyproject.toml` and add the following info:

  ```
  [build-system]
  requires = ["setuptools >= 61.0"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "my-awesome-library"
  version = "0.0.1"
  dependencies = [
    "langchain_core",
    "pydantic",
  ]
  requires-python = ">=3.8"
  classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python"
  ]

  [project.entry-points.creative_assistant]
  my_awesome_tool = "my_awesome_library.tools"
  ```

* Install `my_awesome_library` to make the tool available.

  ```
  pip install -e .
  ```
