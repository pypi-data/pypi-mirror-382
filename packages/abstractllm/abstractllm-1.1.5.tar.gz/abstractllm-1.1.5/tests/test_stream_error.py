#!/usr/bin/env python3
"""Test script to reproduce the streaming error."""

import sys
import os
import traceback
import logging
from abstractllm import create_llm, Session

# Enable DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Also set environment variable
os.environ['ABSTRACTLLM_LOG_LEVEL'] = 'DEBUG'

# Simple read_file tool
def read_file(file_path: str, start_line: int = 1, end_line: int = -1):
    """Read a file and return its contents."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if end_line < 0:
        end_line = len(lines)
    return ''.join(lines[start_line-1:end_line])

# Create session with tools
session = Session(
    provider="lmstudio",
    tools=[read_file]
)

prompt = "Please read the first 10 lines of /Users/albou/projects/abstractllm/README.md"

print("=" * 80)
print("Testing streaming with tool calls...")
print(f"Prompt: {prompt}")
print("=" * 80 + "\n")

try:
    response = session.send(
        message=prompt,
        stream=True
    )

    for chunk in response:
        if isinstance(chunk, str):
            print(chunk, end="", flush=True)
        elif isinstance(chunk, dict) and chunk.get("type") == "tool_result":
            print(f"\n[Tool executed: {chunk.get('tool_call', {}).get('name', 'unknown')}]", flush=True)

    print("\n\nSuccess!")

except Exception as e:
    print(f"\n\nERROR: {e}")
    print("\nTraceback:")
    traceback.print_exc()
