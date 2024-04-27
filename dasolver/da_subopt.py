#!/usr/bin/env python3
""" Compute sub-optimal sized double arrays. """


import argparse
import json
import shutil
import subprocess
import sys
from typing import Tuple

from joblib import Parallel, delayed


def can_solve(
    input_path: str, mat_path: str, timeout: int, size: int
) -> Tuple[int, bool]:
    sat_path = f"{input_path}.sat-size={size}.json"
    cmd = f"timeout {timeout} pipenv run python dasolver/dasolver.py --mat {mat_path} --n_arr {size}  --log_level CRITICAL --output {sat_path}".split()
    try:
        subprocess.check_call(cmd)
        return (size, True)
    except:
        return (size, False)


def calc_subopt(input: str, size_beg: int, size_end: int, timeout: int) -> int:
    mat_path = f"{input}.mat"
    # build matrix
    cmd = f"cargo run --release --bin build_matrix -- --input {input} --output {input}.mat".split()
    subprocess.check_output(cmd)

    sat_path = f"{input}.sat.json"
    ng, ok = size_beg, size_end
    while ok - ng > 1:
        mid = (ok + ng) // 2
        print(f"(ng, mid, ok)={(ng,mid,ok)}")
        cmd = f"timeout {timeout} pipenv run python dasolver/dasolver.py --mat {mat_path} --n_arr {mid}  --log_level INFO --output {sat_path}".split()
        try:
            subprocess.check_call(cmd)
            ok = mid
        except:
            ng = mid
    return ok


def calc_subopt2(
    input: str, size_beg: int, size_end: int, timeout: int, n_proc: int
) -> int:
    mat_path = f"{input}.mat"
    # build matrix
    cmd = f"cargo run --release --bin build_matrix -- --input {input} --output {input}.mat".split()
    subprocess.check_output(cmd)

    # run
    ng, ok = size_beg - 1, size_end
    while (ok - ng) > 1:
        step = max(1, (ok - ng) // (n_proc + 1))
        sizes = []
        for x in range(n_proc):
            y = ng + (x + 1) * step
            if y < ok:
                sizes.append(y)
        print(f"(ng, ok)={(ng, ok)}, sizes={sizes}")
        res = Parallel(n_jobs=n_proc)(
            [delayed(can_solve)(input, mat_path, timeout, size) for size in sizes]
        )
        res.sort()
        oks = [(i, x[0]) for i, x in enumerate(res) if x[1]]
        if len(oks) == 0:
            ng = sizes[-1]
        else:
            (i, size) = oks[0]
            ok = size
            if i > 0:
                ng = sizes[i - 1]

    shutil.copy2(f"{input}.sat-size={ok}.json", args.output)
    return ok


def default_search_range(input_path: str) -> Tuple[int, int]:
    """
    Computes the search range of double arrays.
    It depends on a double array obtained by a greedy algorithm.
    The beginning is set to the number of used elements.
    The endding is set to the array size.
    """
    output_path = f"{input_path}.greedy.json"
    cmd = f"cargo run --release --bin build_da -- --input {input_path} --output {output_path}".split()
    subprocess.check_output(cmd)
    da = json.load(open(output_path, "r"))
    end = len(da["check"])
    beg = sum(1 for x in da["check"] if x != None)
    return (beg, end)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute sub-optimal sized double arrays."
    )
    parser.add_argument("--input", type=str, help="input file path", required=True)
    parser.add_argument("--output", type=str, help="output file path", required=True)
    parser.add_argument("--size_beg", type=int, help="beginning of search range")
    parser.add_argument("--size_end", type=int, help="endding of search range")
    parser.add_argument("--n_proc", type=int, help="number of processors", default=1)
    parser.add_argument(
        "--timeout",
        type=str,
        help="time limit. the prefix must be s/m/h specifying seconds/minutes/hours",
        required=True,
    )
    args = parser.parse_args()

    def parse_timeout(timeout: str) -> int:
        timeout_seconds, unit = int(timeout[:-1]), timeout[-1]
        assert unit in ["s", "m", "h"]
        if unit == "h":
            timeout_seconds *= 3600
        if unit == "m":
            timeout_seconds *= 60
        return timeout_seconds

    try:
        args.timeout = parse_timeout(args.timeout)
    except:
        parser.print_help()
        sys.exit()
    if args.size_beg is None or args.size_end is None:
        beg, end = default_search_range(args.input)
        print(
            f"greedy algorithm creates a double array of density ({beg}/{end}={beg/end:.2f}%)"
        )
        if args.size_beg is None:
            args.size_beg = beg
        if args.size_end is None:
            args.size_end = end

    return args


if __name__ == "__main__":
    args = parse_args()
    res = calc_subopt2(
        args.input, args.size_beg, args.size_end, args.timeout, args.n_proc
    )
    print(
        f"RESULT method=subopt file={args.input} length={res} searchstartlength={args.size_beg} searchendlength={args.size_end} procs={args.n_proc} timeout={args.timeout}"
    )
