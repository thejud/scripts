#!/usr/bin/env pytest

from utils import get_cmd, run_and_check

JX = get_cmd("jx")

def test_001_column_cut_pads_output():
    results = run_and_check([JX, "c", "a"], "jx_001")
    assert results["actual"] == results["expected"]

def test_002_no_args_keeps_headers():
    """previously headers were skipped. Not sure why"""
    results = run_and_check([JX], "jx_002")
    assert results["actual"] == results["expected"]

def test_003_no_headers_arg():
    results = run_and_check([JX, '-H', 'a', 'c' ], "jx_003")
    assert results["actual"] == results["expected"]

def test_004_multiline_object():
    results = run_and_check([JX, '-D'], "jx_004")
    assert results["actual"] == results["expected"]

def test_005_smart_disabled():
    results = run_and_check([JX, '--smart', 'items'], "jx_005")
    assert results["actual"] == results["expected"]

def test_006_no_padding_last_field():
    results = run_and_check([JX], "jx_006")
    assert results["actual"] == results["expected"]

def test_007_flatten_withalternate_joiner():
    """referencing sub-objects with non-default joiner"""
    results = run_and_check([JX, '-F', '-j.', 'a.c', 'a.b'], "jx_007")
    assert results["actual"] == results["expected"]

def test_008_flatten_with_default_joiner():
    """referencing sub-objects with default joiner"""
    results = run_and_check([JX, '-F', 'a_c', 'a_b'], "jx_008")
    assert results["actual"] == results["expected"]

def test_009_flatten_with_array_indexing():
    results = run_and_check([JX, '-F', 'a_c', 'a_d_0'], "jx_009")
    assert results["actual"] == results["expected"]

def test_010_autodetect_arrays():
    results = run_and_check([JX,], "jx_010")
    assert results["actual"] == results["expected"]
