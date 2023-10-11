A special project, to apply prompts in `Example Prompts SCB FX Demo.txt` to events in `SCB FX Events.docx`

# How it works

First convert the file to excel. Then read the excel with pandas.

# `SCB_output.py`

## Async vs Sync

Async only took **14.5** seconds to finish.
Sync version took **9 mins 30 seconds**. (39 times more)

[Check official page from Langchain for detail](https://python.langchain.com/docs/modules/model_io/models/llms/async_llm)
