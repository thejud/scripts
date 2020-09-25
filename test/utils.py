from os.path import abspath, dirname, join
from subprocess import check_output

def get_cmd(cmd):
    path = abspath(join(dirname(__file__), '..', 'bin', cmd))
    return path

def run_and_check(args, file_id):
    infile = join("data", file_id + ".in")
    data = open(infile).read()
    print(f"command: {args}")
    print(f"input: ({infile})\n{data}")

    expected_file = join("data", file_id + ".expected")
    expected = open(expected_file).read()
    print(f"expected: ({expected_file})\n{expected}")

    result = check_output(args, input=data.encode())
    actual = result.decode('utf-8')
    return {"expected": expected, "actual": actual}

"""no input, only output"""
def run_without_input(args, file_id):
    print(f"command: {args}")

    expected_file = join("data", file_id + ".expected")
    expected = open(expected_file).read()
    print(f"expected: ({expected_file})\n{expected}")

    result = check_output(args)
    actual = result.decode('utf-8')
    return {"expected": expected, "actual": actual}

