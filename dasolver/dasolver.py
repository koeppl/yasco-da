#!/usr/bin/env python3

import argparse
import json
import sys
from enum import Enum, auto
from logging import CRITICAL, DEBUG, INFO, Formatter, StreamHandler, getLogger
from os import uname
from typing import List, Optional, Tuple

from mysat import Literal, LiteralManager, pysat_exactlyone, pysat_if
from pysat.card import CardEnc
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.solvers import Solver

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
FORMAT = "[%(lineno)s - %(funcName)10s() ] %(message)s"
formatter = Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)


class DALiteral(Enum):
    true = Literal.true
    false = Literal.false
    auxlit = Literal.auxlit
    base = auto()
    check = auto()
    used = auto()


class DALiteralManager(LiteralManager):
    def __init__(self, mat: List[List[Tuple[int, int]]], n_arr):
        self.mat = mat
        self.n_nodes = len(mat)
        self.n_arr = n_arr
        self.n_chars = n_chars
        self.child_labels = [
            sorted([c for c, _ in mat[nid]]) for nid in range(self.n_nodes)
        ]
        self.lits = DALiteral
        self.verifyf = {
            self.lits.base: self.verify_base,
            self.lits.check: self.verify_check,
            self.lits.used: self.verify_used,
        }
        super().__init__(self.lits)  # type: ignore
        self.init()

    def max_char(self, nid: int) -> int:
        return 0 if len(self.child_labels[nid]) == 0 else self.child_labels[nid][-1]

    def verify_base(self, *obj):
        assert len(obj) == 3
        # obj represents that the base value of node i is j.
        ident, nid, pos = obj
        assert ident == self.lits.base
        assert 0 <= nid < self.n_nodes
        assert 0 <= pos < self.n_arr

    def verify_check(self, *obj):
        assert len(obj) == 3
        # obj represents that the parent of the node at pos is parent_id
        ident, parent_id, pos = obj
        assert ident == self.lits.check
        assert 0 <= parent_id < self.n_nodes
        assert 0 <= pos < self.n_arr

    def verify_used(self, *obj):
        assert len(obj) == 2
        # obj represents that check[pos] is unused.
        ident, pos = obj
        assert ident == self.lits.used
        assert 0 <= pos < self.n_arr

    def internal_nodes(self) -> List[int]:
        return [nid for nid in range(self.n_nodes) if len(self.mat[nid]) > 0]

    def enum_base_keys(self) -> List[Tuple[DALiteral, int, int]]:
        return [
            (self.lits.base, nid, pos)
            for nid in self.internal_nodes()
            for pos in range(self.n_arr - self.max_char(nid))
        ]

    def enum_base_values(self):
        return [self.getid(*key) for key in self.enum_base_keys()]

    def enum_base_items(self):
        return [(key, self.getid(*key)) for key in self.enum_base_keys()]

    def init(self):
        for key in self.enum_base_keys():
            self.newid(*key)


root = 0
n_chars = 256


def da_solver(
    mat: List[List[Tuple[int, int]]], n_arr
) -> Tuple[DALiteralManager, List[List[int]]]:
    """
    mat[i] = [(char, node id)..]
    """
    n_nodes = len(mat)
    assert len(mat) > 0
    assert n_chars > 0
    logger.info(f"n_arr={n_arr}, n_nodes={n_nodes}, n_chars={n_chars}")
    clauses = []
    # register literals
    logger.info("register literals")
    lm = DALiteralManager(mat, n_arr)

    child_labels = [sorted([c for c, _ in mat[nid]]) for nid in range(n_nodes)]

    def max_char(nid: int) -> int:
        return 0 if len(child_labels[nid]) == 0 else child_labels[nid][-1]

    # check
    for nid in range(n_nodes):
        for pos in range(n_arr):
            lm.newid(lm.lits.check, nid, pos)

    # unused
    for pos in range(n_arr):
        lm.newid(lm.lits.used, pos)

    # constraints
    logger.info("register constraints")
    # relation between base values and check values
    for (_, nid, pos) in lm.enum_base_keys():
        lit_base = lm.getid(lm.lits.base, nid, pos)
        for (c, child_id) in mat[nid]:
            if mat[nid] == root:
                continue
            lit_check = lm.getid(lm.lits.check, nid, pos + c)
            clauses.append(pysat_if(lit_base, lit_check))

    # every nodes have a single base value.
    for nid in set(nid for (_, nid, pos) in lm.enum_base_keys()):
        lit, _clauses = pysat_exactlyone(
            lm,
            [lm.getid(lm.lits.base, nid, pos) for pos in range(n_arr - max_char(nid))],
        )
        clauses.extend(_clauses)
        clauses.append([lit])

    # check values at each position are at most one.
    for pos in range(n_arr):
        checks = [lm.getid(lm.lits.check, nid, pos) for nid in range(n_nodes)]
        clauses.extend(CardEnc.atmost(checks, bound=1, vpool=lm.vpool))

    # define unused literals
    for nid in range(n_nodes):
        for pos in range(n_arr):
            # for c in range(n_chars):
            check = lm.getid(lm.lits.check, nid, pos)
            used = lm.getid(lm.lits.used, pos)
            clauses.append(pysat_if(check, used))
    for pos in range(1, n_arr):
        used0 = lm.getid(lm.lits.used, pos)
        used1 = lm.getid(lm.lits.used, pos - 1)
        clauses.append(pysat_if(used0, used1))

    # assumption
    # root's base value is stored at 0
    clauses.append([lm.getid(lm.lits.base, 0, 0)])
    return lm, clauses


def solve(mat: List[List[Tuple[int, int]]], n_arr: int, minimize: bool):
    n_nodes = len(mat)
    child_labels = [sorted([c for c, _ in mat[nid]]) for nid in range(n_nodes)]

    def max_char(nid: int) -> int:
        return 0 if len(child_labels[nid]) == 0 else child_labels[nid][-1]

    lm, cnf = da_solver(mat, n_arr)
    logger.info("solver runs")
    if minimize:
        # objective
        # maximized the number of unused positions.
        wcnf = WCNF()
        wcnf.extend(cnf)
        cnf = wcnf
        for child_idx in range(n_arr):
            lit = lm.getid(lm.lits.used, child_idx)
            cnf.append([-lit], weight=1)
        logger.info(
            f"#literals = {lm.top()}, # hard clauses={len(cnf.hard)}, # of soft clauses={len(cnf.soft)}"
        )
        rc2 = RC2(cnf, verbose=3)
        sol = rc2.compute()
    else:
        logger.info(f"#literals = {lm.top()}, # hard clauses={len(cnf)}")
        solver = Solver()
        solver.append_formula(cnf)
        solver.solve()
        sol = solver.get_model()
    assert sol

    # extracts baes and check arrays.
    sol = set(sol)
    nid2base = dict(
        (nid, base) for (lit, nid, base), val in lm.enum_base_items() if val in sol
    )
    checks = dict(
        (pos, nid)
        for nid in range(n_nodes)
        for pos in range(n_arr)
        if lm.getid(lm.lits.check, nid, pos) in sol
    )

    barr: list[Optional[int]] = [None for _ in range(n_arr)]
    carr: list[Optional[int]] = [None for _ in range(n_arr)]

    n_arr = 0
    # root
    nid2idx = dict()
    nid2idx[0] = 0
    barr[0] = nid2base[0]
    for nid in lm.internal_nodes():
        par_idx = nid2idx[nid]
        barr[par_idx] = nid2base[nid]
        par_base = nid2base[nid]
        for (c, child_id) in mat[nid]:
            child_idx = par_base + c
            assert barr[par_base + c] == None
            assert carr[par_base + c] == None
            carr[par_base + c] = par_idx
            nid2idx[child_id] = par_base + c
            n_arr = max(n_arr, par_base + c)

    da = {"n_arr": n_arr, "root": nid2base[0], "base": barr, "check": carr}
    da = {"base": barr, "check": carr}
    return da


def read_matrix(path) -> List[List[Tuple[int, int]]]:
    return json.load(open(path, "rb"))["mat"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute layout optimized double arrays."
    )
    parser.add_argument("--mat", type=str, help="input trie matrix")
    parser.add_argument("--output", type=str, help="output json path")
    parser.add_argument("--n_arr", type=int, help="maximum size of array")
    parser.add_argument("--minimize", help="minimize the suze", action="store_true")
    parser.add_argument(
        "--log_level", type=str, help="log level, DEBUG/INFO/CRITICAL", default="INFO"
    )
    args = parser.parse_args()
    if args.mat is None or args.n_arr is None:
        parser.print_help()
        sys.exit()

    return args


if __name__ == "__main__":
    args = parse_args()
    if args.log_level == "DEBUG":
        logger.setLevel(DEBUG)
    elif args.log_level == "INFO":
        logger.setLevel(INFO)
    elif args.log_level == "CRITICAL":
        logger.setLevel(CRITICAL)
    mat = read_matrix(args.mat)
    da = solve(mat, args.n_arr, args.minimize)
    json.dump(da, open(args.output, "w"))
