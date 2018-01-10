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

def validate_solution(solution):
    tempfile = "__tmp__.txt"
    for fin, fout in get_test_files():
        with open(fin) as testin, open(tempfile, "w") as tmp:
            print("Running test {}".format(fout[-6:-4]))
            try:
                proc = subprocess.Popen(["python", solution], stdin=testin, stdout=tmp)
                proc.communicate(timeout=2)
            except:
                proc.kill()
                print("\tTimed out")
            else:
                proc = subprocess.Popen(["diff", fout, tempfile])
                proc.communicate()
    os.remove(tempfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Codeforces scraper.')
    parser.add_argument('scriptfile', help='Name of script file to test')
    args = parser.parse_args()
    scriptfile = args.scriptfile
    validate_solution(scriptfile)
