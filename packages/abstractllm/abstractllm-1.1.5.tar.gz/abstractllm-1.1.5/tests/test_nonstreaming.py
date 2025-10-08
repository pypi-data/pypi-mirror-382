#!/usr/bin/env python3
import os
os.environ['ABSTRACTLLM_LOG_LEVEL'] = 'DEBUG'

from abstractllm import Session

def read_file(file_path: str):
    """Read a file."""
    with open(file_path) as f:
        return f.read()[:500]  # Just first 500 chars for testing

session = Session(provider="lmstudio", tools=[read_file])

response = session.send(
    "Please read /Users/albou/projects/abstractllm/README.md",
    stream=False
)

print(f"\nFinal response: {response}")
