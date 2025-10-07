from notbadai_ide import api

from .common.llm import call_llm
from .common.utils import add_line_numbers, parse_json


def get_system_prompt() -> str:
    return """
You are an expert code analyst specializing in static code analysis. Your goal is to find syntax errors in code. Carefully analyze the code (with line numbers) and identify the syntax errors.

1. Only identify syntax errors. Do not identify logic errors.

2. Output only in JSON format:
* A list of JSON object. One object per systax error.
* Each object should be like `{'error': 'description of the error', 'line_no': 'line number with the error', 'contents': 'contents of that line'}

3. Do not make up facts or hallucinate.
""".strip()


def get_prompt(code: str) -> str:
    return f"""
# Python code (with line numbers)

```python
{add_line_numbers(code)}
```
""".strip()


def start():
    current_file_content = api.get_current_file().get_content()

    prompt = get_prompt(current_file_content)

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {'role': 'user', 'content': prompt}
    ]

    response = call_llm('devstral',
                        messages,
                        push_to_chat=False,
                        max_tokens=1024,
                        temperature=0.8,
                        top_p=0.8,
                        )

    api.log(f"LLM response:\n {response}")

    errors = parse_json(response)

    res = []
    for error in errors:
        res.append(dict(row_from=error["line_no"], description=error["error"]))

    api.highlight(res)
