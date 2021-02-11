from params import params

import sbe.hamiltonian
from sbe.main import sbe_solver

def dirac():
    # Param file adjustments
    # System parameters
    A = 0.19732     # Fermi velocity

    dirac_system = sbe.hamiltonian.BiTe(C0=0, C2=0, A=A, R=0, mz=0)

    return dirac_system
def run(system):

    sbe_solver(system, params)

if __name__ == "__main__":
    run(dirac())