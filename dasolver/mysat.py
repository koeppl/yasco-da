from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Any, Callable, Tuple, Type

from pysat.card import CardEnc, IDPool

debug = False


class Literal(Enum):
    true = 1
    false = 2
    auxlit = 3


class LiteralManager:
    # def __init__(self, lits=Literal):
    def __init__(self, lits: Type[Literal] = Literal):
        self.lits = lits
        self.vpool = IDPool()
        self.nvar = defaultdict(int)

    def newid(self, *obj) -> int:
        """
        Adds new object.
        """
        if len(obj) == 0:
            # obj = ("auxlit", self.nvar["auxlit"])
            obj = (self.lits.auxlit, self.nvar[self.lits.auxlit])
        assert obj[0] in self.lits
        assert not self.contains(*obj)
        self.nvar[obj[0]] += 1
        return self.vpool.id(obj)

    def getid(self, *obj) -> int:
        """
        Gets id of the given object
        """
        # print("getid", obj)
        assert self.contains(*obj)
        return self.vpool.obj2id[obj]

    def contains(self, *obj) -> bool:
        return obj in self.vpool.obj2id

    def id2obj(self, id: int):
        return self.vpool.id2obj[id]

    def id2str(self, id: int) -> str:
        return str(self.id2obj(id))

    def top(self) -> int:
        return self.vpool.top


def pysat_or(new_var: Callable[[], int], xs: list[int]) -> Tuple[int, list[list[int]]]:
    nvar = new_var()
    new_clauses = []
    for x in xs:
        new_clauses.append(pysat_if(-nvar, -x))
    new_clause = pysat_if_and_then_or([nvar], xs)
    new_clauses.append(new_clause)
    return nvar, new_clauses


def pysat_and(new_var: Callable[[], int], xs: list[int]) -> Tuple[int, list[list[int]]]:
    nvar = new_var()
    new_clauses = []
    for x in xs:
        new_clauses.append(pysat_if(nvar, x))
    new_clause = pysat_if_and_then_or([-nvar], [-x for x in xs])
    new_clauses.append(new_clause)
    return nvar, new_clauses


# def pysat_atmost(
#     lm: LiteralManager, xs: list[int], bound: int
# ) -> Tuple[int, list[list[int]]]:
#     """
#     Create a literal and clauses such that the number of true literals in `xs` is at most `bound`.
#     """

#     atmost_clauses = CardEnc.atmost(xs, bound=bound, vpool=lm.vpool)

#     xs = []
#     new_clauses = []
#     for clause in atmost_clauses:
#         nvar, clauses = pysat_or(lm.newid, clause)
#         new_clauses.extend(clauses)
#         xs.append(nvar)
#     nvar, clauses = pysat_and(lm.newid, xs)
#     new_clauses.extend(clauses)
#     return nvar, new_clauses


def pysat_atleast_one(xs: list[int]) -> list[int]:
    return xs


# def pysat_exactlyone(lm: LiteralManager, xs: list[int]) -> Tuple[int, list[list[int]]]:
#     new_clauses = pysat_atleast_one(xs)
#     nvar, clauses = pysat_atmost(lm, xs, bound=1)
#     new_clauses.extend(clauses)
#     return pysat_and(lm.newid, new_clauses)


def pysat_exactlyone(lm: LiteralManager, xs: list[int]) -> Tuple[int, list[list[int]]]:
    """
    There must be one positive literal in the given literals.
    """
    ex1_clauses = CardEnc.atmost(xs, bound=1, vpool=lm.vpool)
    ex1_clauses.append(pysat_atleast_one(xs))
    res_var, res_clauses = pysat_name_cnf(lm, ex1_clauses)

    return res_var, res_clauses


def pysat_name_cnf(
    lm: LiteralManager, xs: list[list[int]]
) -> Tuple[int, list[list[int]]]:
    res_clauses = []
    ex1_vars = []
    for clause in xs:
        nvar, or_clauses = pysat_or(lm.newid, clause)
        ex1_vars.append(nvar)
        res_clauses.extend(or_clauses)
    res_var, clauses = pysat_and(lm.newid, ex1_vars)
    res_clauses.extend(clauses)
    return res_var, res_clauses


def pysat_if_and_then_or(xs: list[int], ys: list[int]) -> list[int]:
    return [-x for x in xs] + ys


def pysat_if(x: int, y: int) -> list[int]:
    return [-x, y]


def pysat_iff(x: int, y: int) -> list[list[int]]:
    return [[-x, y], [x, -y]]
