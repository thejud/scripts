#!/usr/bin/env pytest

import utils
from utils import get_cmd, run_and_check, run_without_input

LOGN = get_cmd("logn")

def test_default_base_10():
    results = run_and_check([LOGN], 'logn_001')
    assert results["actual"] == results["expected"]

def test_base2():
    results = run_and_check([LOGN, '-2'], 'logn_002')
    assert results["actual"] == results["expected"]

def test_natural_log():
    results = run_and_check([LOGN, '-e'], 'logn_003')
    assert results["actual"] == results["expected"]

def test_other_base():
    results = run_and_check([LOGN, '-b', '3'], 'logn_004')
    assert results["actual"] == results["expected"]

def test_read_from_file():
    infile = utils.get_input_file('logn_001')
    results = run_without_input([LOGN, infile], 'logn_001')
    assert results["actual"] == results["expected"]
