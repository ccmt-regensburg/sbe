import sympy as sp
import numpy as np

from hfsbe.brillouin import evaluate_energy as evalene
from hfsbe.utility import list_to_numpy_functions


class TwoBandSystem():
    so = sp.Matrix([[1, 0], [0, 1]])
    sx = sp.Matrix([[0, 1], [1, 0]])
    sy = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sz = sp.Matrix([[1, 0], [0, -1]])

    kx = sp.Symbol('kx')
    ky = sp.Symbol('ky')

    def __init__(self, ho, hx, hy, hz):
        """
        Generates the symbolic Hamiltonian, wave functions and
        energies.

        Parameters
        ----------
        ho, hx, hy, hz : Symbol
            Wheter to additionally return energy and wave function derivatives
        """

        self.ho = ho
        self.hx = hx
        self.hy = hy
        self.hz = hz

        self.e = self.__energies()
        self.ederiv = self.__ederiv(self.e)
        self.h = self.__hamiltonian()
        self.U, self.U_h, self.U_no_norm, self.U_h_no_norm = \
            self.__wave_function()

        self.ef = list_to_numpy_functions(self.e)
        self.ederivf = list_to_numpy_functions(self.ederiv)

    def __hamiltonian(self):
        return self.ho*self.so + self.hx*self.sx + self.hy*self.sy \
            + self.hz*self.sz

    def __wave_function(self):
        esoc = sp.sqrt(self.hx**2 + self.hy**2 + self.hz**2)
        wfv = sp.Matrix([-self.hx + sp.I*self.hy, self.hz + esoc])
        wfc = sp.Matrix([self.hz + esoc, self.hx + sp.I*self.hy])
        wfv_h = sp.Matrix([-self.hx - sp.I*self.hy, self.hz + esoc])
        wfc_h = sp.Matrix([self.hz + esoc, self.hx - sp.I*self.hy])

        norm = sp.sqrt(2*(esoc + self.hz)*esoc)

        U = (wfv/norm).row_join(wfc/norm)
        U_h = (wfv_h/norm).T.col_join((wfc_h/norm).T)

        U_no_norm = (wfv).row_join(wfc)
        U_h_no_norm = (wfv_h).T.col_join(wfc_h.T)

        return U, U_h, U_no_norm, U_h_no_norm

    def __energies(self):
        esoc = sp.sqrt(self.hx**2 + self.hy**2 + self.hz**2)
        return self.ho - esoc, self.ho + esoc

    def __ederiv(self, energies):
        """
        Calculate the derivative of the energy bands. Order is
        de[0]/dkx, de[0]/dky, de[1]/dkx, de[1]/dky
        """
        ed = []
        for e in energies:
            ed.append(sp.diff(e, self.kx))
            ed.append(sp.diff(e, self.ky))
        return ed

    def eigensystem(self):
        """
        Generic form of Hamiltonian, energies and wave functions in a two band
        Hamiltonian.

        Returns
        -------
        h : Symbol
            Hamiltonian of the system
        e : list of Symbol
            Valence and conduction band energies; in this order
        [U, U_h] : list of Symbol
            Valence and conduction band wave function; in this order
        ederiv : list of Symbol
            List of energy derivatives
        """

        return self.h, self.e, [self.U, self.U_h], self.ederiv

    def evaluate(self, kx, ky, b1=None, b2=None,
                 hamiltonian_radius=None, eps=10e-10, **fkwargs):

        # Evaluate all kpoints without BZ
        if (b1 is None or b2 is None):
            return self.ef[0](kx=kx, ky=ky, **fkwargs), \
                self.ef[1](kx=kx, ky=ky, **fkwargs)

        if (hamiltonian_radius is None):
            hamr = None
        else:
            hamr = hamiltonian_radius
            # Transform hamr from percentage to length
            minlen = np.min((np.linalg.norm(b1),
                             np.linalg.norm(b2)))
            hamr *= minlen/2

        # Add a BZ and throw error if kx, ky is outside
        evalence = evalene(self.ef[0], kx, ky, b1, b2,
                           hamr=hamr, eps=eps,
                           **fkwargs)
        econduct = evalene(self.ef[1], kx, ky, b1, b2,
                           hamr=hamr, eps=eps,
                           **fkwargs)

        return evalence, econduct


class Haldane(TwoBandSystem):
    """
    Haldane model
    """
    def __init__(self):
        t1 = sp.Symbol('t1')
        t2 = sp.Symbol('t2')
        m = sp.Symbol('m')
        phi = sp.Symbol('phi')

        a1 = self.kx
        a2 = -1/2 * self.kx + sp.sqrt(3)/2 * self.ky
        a3 = -1/2 * self.kx - sp.sqrt(3)/2 * self.ky

        b1 = sp.sqrt(3) * self.ky
        b2 = -3/2 * self.kx - sp.sqrt(3)/2 * self.ky
        b3 = 3/2 * self.kx - sp.sqrt(3)/2 * self.ky

        ho = 2*t2*sp.cos(phi)*(sp.cos(b1)+sp.cos(b2)+sp.cos(b3))
        hx = t1*(sp.cos(a1)+sp.cos(a2)+sp.cos(a3))
        hy = t1*(sp.sin(a1)+sp.sin(a2)+sp.sin(a3))
        hz = m - 2*t2*sp.sin(phi)*(sp.sin(b1)+sp.sin(b2)+sp.sin(b3))

        super().__init__(ho, hx, hy, hz)


class Bite(TwoBandSystem):
    """
    Bismuth Telluride topological insulator model
    """
    def __init__(self, C0=sp.Symbol('C0'), C2=sp.Symbol('C2'),
                 A=sp.Symbol('A'), R=sp.Symbol('R')):
        ho = C0 + C2*(self.kx**2 + self.ky**2)
        hx = A*self.ky
        hy = -A*self.kx
        hz = 2*R*(self.kx**3 - 3*self.kx*self.ky**2)

        super().__init__(ho, hx, hy, hz)


class Graphene(TwoBandSystem):
    """
    Graphene model
    """
    def __init__(self, t=sp.Symbol('t')):
        a1 = self.kx
        a2 = -1/2 * self.kx + sp.sqrt(3)/2 * self.ky
        a3 = -1/2 * self.kx - sp.sqrt(3)/2 * self.ky

        ho = 0
        hx = t*(sp.cos(a1)+sp.cos(a2)+sp.cos(a3))
        hy = t*(sp.sin(a1)+sp.sin(a2)+sp.sin(a3))
        hz = 0

        super().__init__(ho, hx, hy, hz)


class Qwz(TwoBandSystem):
    """
    Qi-Wu-Zhang model of a 2D Chern insulator
    """
    def __init__(self, order=sp.oo):
        n = order+1
        m = sp.Symbol('m')

        ho = 0
        if order == sp.oo:
            hx = sp.sin(self.kx)
            hy = sp.sin(self.ky)
            hz = m - sp.cos(self.kx) - sp.cos(self.ky)
        else:
            hx = sp.sin(self.kx).series(n=n).removeO()
            hy = sp.sin(self.ky).series(n=n).removeO()
            hz = m - sp.cos(self.kx).series(n=n).removeO()\
                - sp.cos(self.ky).series(n=n).removeO()

        super().__init__(ho, hx, hy, hz)


class Dirac(TwoBandSystem):
    """
    Generic Dirac cone Hamiltonian
    """
    def __init__(self, m=sp.Symbol('m')):

        ho = 0
        hx = self.kx
        hy = self.ky
        hz = m

        super().__init__(ho, hx, hy, hz)
