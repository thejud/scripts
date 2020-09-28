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

def test_no_args_generates_current_epoch(capsys):
    opts = SimpleNamespace(utc=False, filter=False, args=[])
    start_timestamp = math.floor(time.time())
    unixtime.run(opts)
    end_timestamp = math.ceil(time.time())

    result = int(capsys.readouterr().out.strip())
    assert result >= start_timestamp
    assert result <= end_timestamp

def test_noargs_with_millis_gives_millis_since_epoch(capsys):
    opts = SimpleNamespace(utc=False, filter=False, args=[])

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

def test_epoch_to_date_to_epoch():
    parser = unixtime.UnixTimeParser()
    t1 = "1601172064"
    result = parser.parse_date(parser.parse_digits(t1))

    assert result == t1

def test_parse_date_parses_ctime():
    parser = unixtime.UnixTimeParser()
    ctime = 'Sun Sep 27 11:55:28 2020'
    dt = datetime.strptime(ctime, '%a %b %d %H:%M:%S %Y')
    epoch = int(dt.timestamp())

    result = parser.parse_date(ctime)

    assert result == str(epoch)

def test_filter_line_converts_embedded_epoch():
    parser = unixtime.UnixTimeParser()
    ds = datetime.utcnow()
    epoch = int(ds.timestamp())
    line = "This is a %s test" % (epoch)

    result = parser.filter_line(line)

    date_string = parser.parse_digits(str(epoch))
    expected  = "This is a %s test" % (date_string)
    assert result == expected

def test_filter_line_converts_full_datestring():
    parser = unixtime.UnixTimeParser()
    line = " 2020-09-26T19:44:00-0000 \n"

    result = parser.filter_line(line)

    expected = " 1601149440 \n"
    assert result == expected 


def test_filter_input(capsys):
    opts = SimpleNamespace(utc=True, filter=True, args=[])

    result = int(capsys.readouterr().out.strip())
    assert result >= start_timestamp
    assert result <= end_timestamp
