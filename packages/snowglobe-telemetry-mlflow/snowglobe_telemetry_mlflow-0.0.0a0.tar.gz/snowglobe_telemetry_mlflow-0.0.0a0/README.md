# Snowlgobe Telemetry Instrumentation for MLflow

Instrument your Snowglobe connected app with MLflow and start collecting insightful traces when you run Simulations in Snowglobe.  Read more about MLflow's tracing capability for GenAI Apps [here](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/).

## Installation

```
pip install snowglobe-telemetry-mlflow
```

If using uv, set the `--prerelease=allow` flag
```
uv pip install --prerelease=allow snowglobe-telemetry-mlflow
```


## Add the MLflowInstrumentor to your agent file

Reminder: Each agent wrapper file resides in the root directory of your project, and is named after the agent (e.g. `My Agent Name` becomes `my_agent_name.py`).

```python
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
from openai import OpenAI
import os

### Add these two lines to your agent file and watch context rich traces come in!
from snowglobe.telemetry.mlflow import MLflowInstrumentor
MLflowInstrumentor().instrument()


client = OpenAI(api_key=os.getenv("SNOWGLOBE_API_KEY"))

def completion_fn(request: CompletionRequest) -> CompletionFunctionOutputs:
    """
    Process a scenario request from Snowglobe.
    
    This function is called by the Snowglobe client to process requests. It should return a
    CompletionFunctionOutputs object with the response content.

    Example CompletionRequest:
    CompletionRequest(
        messages=[
            SnowglobeMessage(role="user", content="Hello, how are you?", snowglobe_data=None),
        ]
    )

    Example CompletionFunctionOutputs:
    CompletionFunctionOutputs(response="This is a string response from your application")
    
    Args:
        request (CompletionRequest): The request object containing the messages.

    Returns:
        CompletionFunctionOutputs: The response object with the generated content.
    """

    # Process the request using the messages. Example:
    messages = request.to_openai_messages()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return CompletionFunctionOutputs(response=response.choices[0].message.content)
```



## Enhancing Snowglobe Connect SDK's Traces with Autologging
You can turn on mlflow autologging in your app to add additional context to the traces the Snowglobe Connect SDK captures.  In your agent wrapper file, simply call the appropriate autolog method for the LLM provider you're using.  The below example shows how to enable this for OpenAI:
```py
import mlflow

mlflow.openai.autolog()
```