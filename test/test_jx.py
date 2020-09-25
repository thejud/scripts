#!/usr/bin/env pytest

from utils import get_cmd, run_and_check

JX = get_cmd("jx")

def test_001_column_cut_pads_output():
    results = run_and_check([JX, "c", "a"], "jx_001")
    assert results["actual"] == results["expected"]

def test_002_no_args_skips_headers():
    results = run_and_check([JX], "jx_002")
    assert results["actual"] == results["expected"]

def test_003_no_headers_arg():
    results = run_and_check([JX, '-H', 'a', 'c' ], "jx_003")
    assert results["actual"] == results["expected"]
