#!/usr/bin/env python
"""
convert python data strunctures into json
Useful if you have some debugging output
"""

import json
import fileinput

lines = "".join(fileinput.input())
print(json.dumps(eval(lines)))

