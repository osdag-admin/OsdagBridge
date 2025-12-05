class SolverAdapter:
    """Unified interface for solvers."""
    def run(self, model):
        raise NotImplementedError
