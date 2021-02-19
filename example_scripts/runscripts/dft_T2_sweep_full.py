import os
import numpy as np
from params import params

import cued.dipole
from cued.hamiltonian import BiTeResummed
from cued.parameter_loops.sequential import chirp_phasesweep
from cued.utility import mkdir_chdir

def dft():
    C0 = -0.00647156                  # C0
    c2 = 0.0117598                    # k^2 coefficient
    A = 0.0422927                     # Fermi velocity
    r = 0.109031                      # k^3 coefficient
    ksym = 0.0635012                  # k^2 coefficent dampening
    kasym = 0.113773                  # k^3 coeffcient dampening

    dft_system = BiTeResummed(C0=C0, c2=c2, A=A, r=r, ksym=ksym, kasym=kasym)

    return dft_system

def run(system):

    params.gauge = 'length'
    params.BZ_type = 'hexagon'

    params.E0 = 2
    params.w = 25
    params.alpha = 25

    params.e_fermi = 0.0

    stretch_t0 = 2
    # Increase time interval for broader pulses
    if params.alpha > 25:
        stretch_t0 = 2
    if params.alpha > 75:
        stretch_t0 = 3
    if params.alpha > 100:
        stretch_t0 = 5

    params.t0 *= stretch_t0
    params.dt = 0.1

    T2list = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    chirplist = [0.000]
    phaselist = np.linspace(0, np.pi, 20)

    params.Nk1 = 900
    params.Nk2 = 120
    dirname_dist = 'Nk1_{:d}_Nk2_{:d}_nog'.format(params.Nk1, params.Nk2)
    mkdir_chdir(dirname_dist)

    for T2 in T2list:
        # Starts as many python jobs as there are elements in T2list
        pid = os.fork()

        if pid == 0:
            params.T1 = 1000
            params.T2 = T2
            dirname_T = 'T1_' + str(params.T1) + '_T2_' + str(params.T2)
            mkdir_chdir(dirname_T)

            chirp_phasesweep(chirplist, phaselist, system, params)
            return 0

if __name__ == "__main__":
    run(dft())
