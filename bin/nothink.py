#!/usr/bin/env python3
"""
Removes all text enclosed within <think>...</think> tags from the input.
e.g. qwen llm models

Reads input from stdin or files provided as arguments and outputs the cleaned text.

Usage:
    python nothink.py [file1 file2 ...]
    cat input.txt | python nothink.py
"""


import fileinput
import re

response = "".join(fileinput.input())

print(re.sub(r"<think>.*?</think>\n?", "", response, flags=re.DOTALL))
