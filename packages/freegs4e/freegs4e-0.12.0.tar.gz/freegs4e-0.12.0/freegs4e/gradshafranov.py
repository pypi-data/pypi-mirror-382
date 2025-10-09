"""
Contains various classes and functions related to the elliptic operator 
of the Grad-Shafranov equation. 

Copyright 2016 Ben Dudson, University of York. Email: benjamin.dudson@york.ac.uk

This file is part of FreeGS4E.

FreeGS4E is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FreeGS4E is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with FreeGS4E.  If not, see <http://www.gnu.org/licenses/>.

"""

from numpy import clip, pi, sqrt, zeros
from scipy.sparse import eye, lil_matrix

# elliptic integrals of first and second kind (K and E)
from scipy.special import ellipe, ellipk

# magnetic permeability of free space
mu0 = 4e-7 * pi


class GSElliptic:
    """
    Class representing the elliptc operator within the Grad-Shafranov
    equation:

        Δ^* = d^2/dR^2 + d^2/dZ^2 - (1/R)*d/dR

        where:
         -  R is the radial coordinate.
         -  Z is the vertical coordinate.

    """

    def __init__(self, Rmin):
        """
        Initializes the class.

        Parameters
        ----------
        Rmin : float
            Minimum major radius [m].

        """

        self.Rmin = Rmin

    def __call__(self, psi, dR, dZ):
        """
        Apply the elliptic operator to the flux function such that:

            (Δ^*) * ψ.

        Computes to second-order accuracy.

        Parameters
        ----------
        psi : np.array
            The total poloidal flux at each (R,Z) grid point [Webers/2pi].
        dR : float
            Radial grid size [m].
        dZ : float
            Vertical grid size [m].

        Returns
        -------
        np.array
            The operator applied to the total poloidal flux.
        """

        # number of radial and vertical grid points
        nx = psi.shape[0]
        ny = psi.shape[1]

        # to store output
        b = zeros([nx, ny])

        # pre-compute constants
        invdR2 = 1.0 / dR**2
        invdZ2 = 1.0 / dZ**2

        # compute the operator (can be vectorised)
        for x in range(1, nx - 1):
            R = self.Rmin + dR * x  # Major radius of this point
            for y in range(1, ny - 1):
                # Loop over points in the domain
                b[x, y] = (
                    psi[x, y - 1] * invdZ2
                    + (invdR2 + 1.0 / (2.0 * R * dR)) * psi[x - 1, y]
                    - 2.0 * (invdR2 + invdZ2) * psi[x, y]
                    + (invdR2 - 1.0 / (2.0 * R * dR)) * psi[x + 1, y]
                    + psi[x, y + 1] * invdZ2
                )
        return b

    def diag(self, dR, dZ):
        """
        Computes:

            -2 * ( (1/dR^2) + (1/dZ^2) ).

        Parameters
        ----------
        dR : float
            Radial grid size [m].
        dZ : float
            Vertical grid size [m].

        Returns
        -------
        float
            The value above.
        """
        return -2.0 / dR**2 - 2.0 / dZ**2


class GSsparse:
    """
    Class representing the elliptc operator within the Grad-Shafranov
    equation:

        Δ^* = d^2/dR^2 + d^2/dZ^2 - (1/R)*d/dR

        where:
         -  R is the radial coordinate.
         -  Z is the vertical coordinate.

    This class calculates the sparse version to second-order accuracy.

    """

    def __init__(self, Rmin, Rmax, Zmin, Zmax):
        """
        Initializes the class.

        Parameters
        ----------
        Rmin : float
            Minimum major radius [m].
        Rmax : float
            Maximum major radius [m].
        Zmin : float
            Minimum height [m].
        Zmax : float
            Maximum height [m].

        """

        # set parameters
        self.Rmin = Rmin
        self.Rmax = Rmax
        self.Zmin = Zmin
        self.Zmax = Zmax

    def __call__(self, nx, ny):
        """
        Generates the sparse elliptic operator Δ^* for a given number of
        grid points. Computes to second-order accuracy.

        Parameters
        ----------
        nx : int
            Number of radial grid points (must be of form 2^n + 1, n=0,1,2,3,4,5,...).
        ny : int
            Number of vertical grid points (must be of form 2^n + 1, n=0,1,2,3,4,5,...).

        Returns
        -------
        np.array
            The operator matrix.
        """

        # calculate grid spacing
        dR = (self.Rmax - self.Rmin) / (nx - 1)
        dZ = (self.Zmax - self.Zmin) / (ny - 1)

        # total number of points
        N = nx * ny

        # create a linked list sparse matrix
        A = eye(N, format="lil")

        # pre-compute constants
        invdR2 = 1.0 / dR**2
        invdZ2 = 1.0 / dZ**2

        # generate the operator values (can be optimsied)
        for x in range(1, nx - 1):
            R = self.Rmin + dR * x  # Major radius of this point
            for y in range(1, ny - 1):
                # Loop over points in the domain
                row = x * ny + y

                # y-1
                A[row, row - 1] = invdZ2

                # x-1
                A[row, row - ny] = invdR2 + 1.0 / (2.0 * R * dR)

                # diagonal
                A[row, row] = -2.0 * (invdR2 + invdZ2)

                # x+1
                A[row, row + ny] = invdR2 - 1.0 / (2.0 * R * dR)

                # y+1
                A[row, row + 1] = invdZ2

        # convert to Compressed Sparse Row (CSR) format
        return A.tocsr()


class GSsparse4thOrder:
    """
    Class representing the elliptc operator within the Grad-Shafranov
    equation:

        Δ^* = d^2/dR^2 + d^2/dZ^2 - (1/R)*d/dR

        where:
         -  R is the radial coordinate.
         -  Z is the vertical coordinate.

    This class calculates the sparse version to fourth-order accuracy.

    """

    # Coefficients for first derivatives
    # (index offset, weight)

    centred_1st = [
        (-2, 1.0 / 12),
        (-1, -8.0 / 12),
        (1, 8.0 / 12),
        (2, -1.0 / 12),
    ]

    offset_1st = [
        (-1, -3.0 / 12),
        (0, -10.0 / 12),
        (1, 18.0 / 12),
        (2, -6.0 / 12),
        (3, 1.0 / 12),
    ]

    # Coefficients for second derivatives
    # (index offset, weight)
    centred_2nd = [
        (-2, -1.0 / 12),
        (-1, 16.0 / 12),
        (0, -30.0 / 12),
        (1, 16.0 / 12),
        (2, -1.0 / 12),
    ]

    offset_2nd = [
        (-1, 10.0 / 12),
        (0, -15.0 / 12),
        (1, -4.0 / 12),
        (2, 14.0 / 12),
        (3, -6.0 / 12),
        (4, 1.0 / 12),
    ]

    def __init__(self, Rmin, Rmax, Zmin, Zmax):
        """
        Initializes the class.

        Parameters
        ----------
        Rmin : float
            Minimum major radius [m].
        Rmax : float
            Maximum major radius [m].
        Zmin : float
            Minimum height [m].
        Zmax : float
            Maximum height [m].

        """

        # set parameters
        self.Rmin = Rmin
        self.Rmax = Rmax
        self.Zmin = Zmin
        self.Zmax = Zmax

    def __call__(self, nx, ny):
        """
        Generates the sparse elliptic operator Δ^* for a given number of
        grid points. Computes to fourth-order accuracy.

        Parameters
        ----------
        nx : int
            Number of radial grid points (must be of form 2^n + 1, n=0,1,2,3,4,5,...).
        ny : int
            Number of vertical grid points (must be of form 2^n + 1, n=0,1,2,3,4,5,...).

        Returns
        -------
        np.array
            The operator matrix.
        """

        # calculate grid spacing
        dR = (self.Rmax - self.Rmin) / (nx - 1)
        dZ = (self.Zmax - self.Zmin) / (ny - 1)

        # total number of points, including boundaries
        N = nx * ny

        # create a linked list sparse matrix
        A = lil_matrix((N, N))

        # calculate constants
        invdR2 = 1.0 / dR**2
        invdZ2 = 1.0 / dZ**2

        # calculate entries (can be vectorised)
        for x in range(1, nx - 1):
            R = self.Rmin + dR * x  # Major radius of this point
            for y in range(1, ny - 1):
                row = x * ny + y

                # d^2 / dZ^2
                if y == 1:
                    # One-sided derivatives in Z
                    for offset, weight in self.offset_2nd:
                        A[row, row + offset] += weight * invdZ2
                elif y == ny - 2:
                    # One-sided, reversed direction.
                    # Note that for second derivatives the sign of the weights doesn't change
                    for offset, weight in self.offset_2nd:
                        A[row, row - offset] += weight * invdZ2
                else:
                    # Central differencing
                    for offset, weight in self.centred_2nd:
                        A[row, row + offset] += weight * invdZ2

                # d^2 / dR^2 - (1/R) d/dR

                if x == 1:
                    for offset, weight in self.offset_2nd:
                        A[row, row + offset * ny] += weight * invdR2

                    for offset, weight in self.offset_1st:
                        A[row, row + offset * ny] -= weight / (R * dR)

                elif x == nx - 2:
                    for offset, weight in self.offset_2nd:
                        A[row, row - offset * ny] += weight * invdR2

                    for offset, weight in self.offset_1st:
                        A[row, row - offset * ny] += weight / (R * dR)
                else:
                    for offset, weight in self.centred_2nd:
                        A[row, row + offset * ny] += weight * invdR2

                    for offset, weight in self.centred_1st:
                        A[row, row + offset * ny] -= weight / (R * dR)

        # set boundary rows
        for x in range(nx):
            for y in [0, ny - 1]:
                row = x * ny + y
                A[row, row] = 1.0
        for x in [0, nx - 1]:
            for y in range(ny):
                row = x * ny + y
                A[row, row] = 1.0

        # convert to Compressed Sparse Row (CSR) format
        return A.tocsr()


def Greens(Rc, Zc, R, Z):
    """
    Calculate poloidal flux at (R,Z) due to a single unit of current at
    (Rc,Zc) using Greens function for the elliptic operator above. Greens
    function is given by:

        G(R, Z; Rc, Zc) = (μ0 / (2π)) * sqrt(R * Rc) * ((2 - k^2) * K(k^2) - 2 * E(k^2)) / k

    where:
     - k^2 = 4 R Rc / ((R + Rc)^2 + (Z - Zc)^2)
     - k = sqrt(k^2)

    and K(k^2) and E(k^2) are the complete elliptic integrals of the first
    and second kind.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].

    Returns
    -------
    float
        Value of the poloidal flux at (R,Z).
    """

    # calculate k^2
    k2 = 4.0 * R * Rc / ((R + Rc) ** 2 + (Z - Zc) ** 2)

    # clip to between 0 and 1 to avoid nans e.g. when coil is on grid point
    k2 = clip(k2, 1e-10, 1.0 - 1e-10)
    k = sqrt(k2)

    # note definition of ellipk, ellipe in scipy is K(k^2), E(k^2)
    return (
        (mu0 / (2.0 * pi))
        * sqrt(R * Rc)
        * ((2.0 - k2) * ellipk(k2) - 2.0 * ellipe(k2))
        / k
    )


def GreensBz(Rc, Zc, R, Z, eps=1e-4):
    """
    Calculate vertical magnetic field at (R,Z) due to a single unit of current at
    (Rc,Zc) using Greens function for the elliptic operator above.

        Bz(R,Z) = (1/R) d psi/dR,

    where psi is found with the Greens function finite difference.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the radial direction [m].

    Returns
    -------
    float
        Value of the vertical magnetic field at (R,Z) [T].
    """

    return (Greens(Rc, Zc, R + eps, Z) - Greens(Rc, Zc, R - eps, Z)) / (
        2.0 * eps * R
    )


def GreensBr(Rc, Zc, R, Z, eps=1e-4):
    """
    Calculate radial magnetic field at (R,Z) due to a single unit of current at
    (Rc,Zc) using Greens function for the elliptic operator above.

        Br(R,Z) = -(1/R) d psi/dZ,

    where psi is found with the Greens function finite difference.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the radial direction [m].

    Returns
    -------
    float
        Value of the radial magnetic field at (R,Z) [T].
    """

    return (Greens(Rc, Zc, R, Z - eps) - Greens(Rc, Zc, R, Z + eps)) / (
        2.0 * eps * R
    )


def GreensdBzdr(Rc, Zc, R, Z, eps=2e-3):
    """
    Calculate radial derivative of vertical magnetic field at (R,Z) due to a
    single unit of current at (Rc,Zc) using Greens function for the
    elliptic operator above:

        dBz/dR (R,Z) = (Bz(R + eps, Z) - Bz(R - eps, Z))/ 2 * eps.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the radial direction [m].

    Returns
    -------
    float
        Value of the derivative at (R,Z) [T/m].
    """

    return (GreensBz(Rc, Zc, R + eps, Z) - GreensBz(Rc, Zc, R - eps, Z)) / (
        2.0 * eps
    )


def GreensdBrdz(Rc, Zc, R, Z, eps=2e-3):
    """
    Calculate vertical derivative of radial magnetic field at (R,Z) due to a
    single unit of current at (Rc,Zc) using Greens function for the
    elliptic operator above:

        dBr/dZ (R,Z) = (Br(R, Z + eps) - Br(R, Z - eps))/ 2 * eps.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the vertical direction [m].

    Returns
    -------
    float
        Value of the derivative at (R,Z) [T/m].
    """

    return (GreensBr(Rc, Zc, R, Z + eps) - GreensBr(Rc, Zc, R, Z - eps)) / (
        2.0 * eps
    )
    # return GreensdBzdr(Rc, Zc, R, Z, eps)


def GreensdBzdz(Rc, Zc, R, Z, eps=2e-3):
    """
    Calculate vertical derivative of vertical magnetic field at (R,Z) due to a
    single unit of current at (Rc,Zc) using Greens function for the
    elliptic operator above:

        dBz/dZ (R,Z) = (Bz(R, Z + eps) - Bz(R, Z - eps))/ 2 * eps.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the vertical direction [m].

    Returns
    -------
    float
        Value of the derivative at (R,Z) [T/m].
    """

    return (GreensBz(Rc, Zc, R, Z + eps) - GreensBz(Rc, Zc, R, Z - eps)) / (
        2.0 * eps
    )


def GreensdBrdr(Rc, Zc, R, Z, eps=2e-3):
    """
    Calculate radial derivative of radial magnetic field at (R,Z) due to a
    single unit of current at (Rc,Zc) using Greens function for the
    elliptic operator above:

        dBr/dR (R,Z) = (Br(R + eps, Z) - Br(R + pes, Z))/ 2 * eps.

    Parameters
    ----------
    Rc : float
        Radial position where current is located [m].
    Zc : float
        Vertical position where current is located [m].
    R : float
        Radial position where poloidal flux is to be calcualted [m].
    Z : float
        Vertical position where poloidal flux is to be calcualted [m].
    eps : float
        Small step size for numerical differentiation in the radial direction [m].

    Returns
    -------
    float
        Value of the derivative at (R,Z) [T/m].
    """

    return (GreensBr(Rc, Zc, R + eps, Z) - GreensBr(Rc, Zc, R - eps, Z)) / (
        2.0 * eps
    )
