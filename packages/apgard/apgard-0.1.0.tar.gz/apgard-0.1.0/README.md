# Apgard SDK

Python SDK for consuming AI outputs from Apgard.

## Installation

pip install apgard

## Example

from apgard import ApgardClient

# Initialize client
client = ApgardClient(api_key="your_api_key_here")

# Use the decorator
@client.track_model_output(metadata={"model": "gpt-4"})
def my_ai_function(text: str):
    return "AI response"

result = my_ai_function("Hello")