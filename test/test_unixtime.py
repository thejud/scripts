#!/usr/bin/env pytest

from utils import get_cmd, run_and_check, run_without_input
from subprocess import check_output

import time
import math

UNIXTIME = get_cmd("unixtime")

def test_001_gets_current_unixtime():
    start = math.floor(time.time())
    result = int(check_output(UNIXTIME).decode('utf-8'))
    end = math.ceil(time.time())
    assert result >= start
    assert result <= end

def test_002_converts_to_utc():
    t1 = "1601023029"
    t2 = "1601023089868"
    expected1 = "2020-09-25 08:37:09 UTC"
    expected2 = "2020-09-25 08:38:09 UTC"
    result = check_output([UNIXTIME, "-u", t1, t2]).decode('utf-8')
    expected = "\n".join([expected1, expected2]) + "\n"

    assert result == expected
   
def test_003_filter_extracts_timestamps_and_leaves_numbers():
    results = run_and_check([UNIXTIME, '--filter'], 'unixtime_003')
    assert results["actual"] == results["expected"]

