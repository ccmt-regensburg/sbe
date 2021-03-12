from params import params

import cued.hamiltonian
from cued.main import sbe_solver

def dirac():
    A  = 0.1974      # Fermi velocity
    mz = 0.01837     # prefactor of sigma_z in Hamiltonian

    dirac_system = cued.hamiltonian.BiTe(C0=0, C2=0, A=A, R=0, mz=mz, gidx=1)

    return dirac_system

def run(system):

    sbe_solver(system, params)

    return 0

if __name__ == "__main__":
    run(dirac())
