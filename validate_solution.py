#!/usr/bin/python3

import os
import subprocess
import argparse

def get_test_files():
    test_dir = "tests"
    input_dir = os.path.join(test_dir, "input")
    output_dir = os.path.join(test_dir, "output")
    for input_fn in os.listdir(input_dir):
        output_fn = "output" + input_fn[-6:]
        yield (
            os.path.join(input_dir, input_fn),
            os.path.join(output_dir, output_fn)
        )

def execute_script_test(solution, testin, testout, timeout):
    ext = solution.split(".")[-1]
    try:
        if ext == "py":
            proc = subprocess.Popen(["python", solution], stdin=testin, stdout=testout)
            proc.communicate(timeout=timeout)
            proc.wait()
            if proc.returncode != 0:
                print("----Error: Return code='{}'".format(proc.returncode))
                return False
        elif ext == "cpp":
            subprocess.Popen(["g++", "-std=c++11", solution]).communicate()
            proc = subprocess.Popen(["./a.out"], stdin=testin, stdout=testout)
            proc.communicate(timeout=timeout)
            proc.wait()
            subprocess.Popen(["rm", "a.out"]).communicate()
            if proc.returncode != 0:
                print("----Error: Return code='{}'".format(proc.returncode))
                return False
        else:
            proc = subprocess.Popen(["cat", "unrecognized solution: '.{}'".format(ext)])
            proc.communicate()
            return False
        return True
    except:
        proc.kill()
        print("\tTimed out")
        return False


def validate_solution(solution, timeout):
    tempfile = "__tmp__.txt"
    for fin, fout in get_test_files():
        with open(fin) as testin, open(tempfile, "w") as tmp:
            print("Running test {}".format(fout[-6:-4]))
            if execute_script_test(solution, testin, tmp, timeout):
                subprocess.Popen(["diff", fout, tempfile]).communicate()
    os.remove(tempfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script validator.')
    parser.add_argument('scriptfile', help='Name of script file to test')
    parser.add_argument('-timeout', "-t", help='Time limit for solutions', default=2)
    args = parser.parse_args()
    scriptfile = args.scriptfile
    timeout = float(args.timeout)
    validate_solution(scriptfile, timeout)
