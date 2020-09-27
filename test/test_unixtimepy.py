#!/usr/bin/env pytest

from utils import get_cmd, run_and_check, run_without_input
from subprocess import check_output

from datetime import datetime
import math
import sys
import time

from types import SimpleNamespace

sys.path.append("../bin")
import unixtime

UNIXTIME = get_cmd("unixtime")

def test_no_args_generates_current_ctime(capsys):
    opts = SimpleNamespace(utc=False, filter=False, args=[])
    start_timestamp = math.floor(time.time())
    unixtime.run(opts)
    end_timestamp = math.ceil(time.time())

    result = int(capsys.readouterr().out.strip())
    assert result >= start_timestamp
    assert result <= end_timestamp

def parse_timestamp_parses_unix():
    parser = unixtime.UnixTimeParser()
    result = parser.parse_digits("1601172064")
    assert result == "2020-09-27 02:01:04 UTC"

def test_parse_timet_parses_java():
    parser = unixtime.UnixTimeParser()
    result = parser.parse_digits("1601172070400")
    assert result == "2020-09-27 02:01:10 UTC"

def test_parse_timestamp_without_utc_returns_localtime():
    parser = unixtime.UnixTimeParser(utc_output=True)
    t1 = "1601172064"

    result = parser.parse_digits(t1)

    expected = time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime(int(t1)))
    assert result == expected

