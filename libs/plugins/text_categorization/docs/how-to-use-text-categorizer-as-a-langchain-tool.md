# How to use text-categorizer as a Langchain tool

`text-categorizer` can be exposed as a Langchain tool.

1. Install `text-categorizer` with `pip install text-categorization` command.

2. Import tool with
```
from text_categorization import tools as categorizer_tools
```

3. Initialize tool

```
text_categorizer_tool = categorizer_tools.TextCategorizationResults(
  llm_type='gemini',
  llm_params={'model': 'gemini-1.5-flash'}
)
```

4. Add tool to any Langchain Agent or AgentExecutor.
