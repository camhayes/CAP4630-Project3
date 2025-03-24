from pysat.formula import CNF
from pysat.solvers import Solver

class CNFSolver:
    def __init__(self, clauses):
        self.clauses = clauses
    
    cnf = CNF(from_clauses=clauses)

    with Solver(bootstrap_with=cnf) as solver:
        print(solver.solve())
        print(solver.get_model())