#!/usr/bin/env python

import fileinput
import os.path

for line in fileinput.input():
	base = os.path.basename(line.strip())
	ext = os.path.splitext(base)[1]
	if len(ext) > 0:
		print(ext)
