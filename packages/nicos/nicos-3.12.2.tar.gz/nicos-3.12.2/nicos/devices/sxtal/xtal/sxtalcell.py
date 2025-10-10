# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Single crystal cell, internally stored as nonius rmat.

The RMAT matrix part is a 3x3 matrix with the columns representing the
reciprocal vectors a*, b* and c* in the laboratory coordinate system x,y,z (X
pointing to the source, Z pointing to the Zenith, and Y pointing along the
cross-product Z*X, pointing to the positive theta side of the Kappa goniometer)
at the goniostat zero-position (kappa=0, omega=0, phi=0).

Relation to the TAS UB matrix:
  rmat = UB^T / 2* pi
"""

from collections import namedtuple

import numpy as np

from nicos.devices.sxtal.xtal import symmetry

CellParam = namedtuple('CellParam', ['a', 'b', 'c', 'alpha', 'beta', 'gamma'])


def vecangle(v1, v2):
    lengths = np.linalg.norm(v1) * np.linalg.norm(v2)
    return np.rad2deg(np.arccos(np.clip(np.dot(v1, v2) / lengths, -1.0, 1.0)))


def fillCellParam(a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0):
    if not c:
        c = a
    if not b:
        b = a

    alphar = np.deg2rad(alpha)
    betar = np.deg2rad(beta)
    gammar = np.deg2rad(gamma)
    return CellParam(a, b, c, alphar, betar, gammar)


def recCell(a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0):
    if isinstance(a, CellParam):
        cell = a
    else:
        cell = fillCellParam(a, b, c, alpha, beta, gamma)
    alphas = np.arccos((np.cos(cell.beta) * np.cos(cell.gamma) - np.cos(cell.alpha)) /
                       (np.sin(cell.beta) * np.sin(cell.gamma)))
    betas = np.arccos((np.cos(cell.alpha) * np.cos(cell.gamma) - np.cos(cell.beta)) /
                      (np.sin(cell.alpha) * np.sin(cell.gamma)))
    gammas = np.arccos((np.cos(cell.alpha) * np.cos(cell.beta) - np.cos(cell.gamma)) /
                       (np.sin(cell.alpha) * np.sin(cell.beta)))
    aas = 1. / (cell.a * np.sin(cell.beta) * np.sin(gammas))
    bs = 1. / (cell.b * np.sin(cell.alpha) * np.sin(gammas))
    cs = 1. / (cell.c * np.sin(cell.alpha) * np.sin(betas))
    return CellParam(aas, bs, cs, alphas, betas, gammas)


def matrixfromcell(a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0):
    if isinstance(a, CellParam):
        cell = a
    else:
        cell = fillCellParam(a, b, c, alpha, beta, gamma)
    rc = recCell(cell)
    mat = np.zeros((3, 3), 'd')
    mat[0, 0] = rc.a * np.sin(rc.beta) * np.sin(cell.gamma)
    mat[1, 0] = -rc.a * np.sin(rc.beta) * np.cos(cell.gamma)
    mat[2, 0] = rc.a * np.cos(rc.beta)
    mat[1, 1] = rc.b * np.sin(rc.alpha)
    mat[2, 1] = rc.b * np.cos(rc.alpha)
    mat[2, 2] = rc.c
    return mat


def matfromrcell(astar, bstar=None, cstar=None, alphastar=None, betastar=None,
                 gammastar=None):
    """Make standard-orientation reciprocal cell matrix from reciprocal cell.
    """
    if isinstance(astar, CellParam):
        cell = astar
    else:
        cell = fillCellParam(astar, bstar, cstar, alphastar, betastar, gammastar)
    dcell = recCell(cell)
    mat = np.zeros((3, 3), 'd')
    mat[0, 0] = cell.a * np.sin(cell.beta) * np.sin(dcell.gamma)
    mat[1, 0] = -cell.a * np.sin(cell.beta) * np.cos(dcell.gamma)
    mat[2, 0] = cell.a * np.cos(cell.beta)
    mat[1, 1] = cell.b * np.sin(cell.alpha)
    mat[2, 1] = cell.b * np.cos(cell.alpha)
    mat[2, 2] = cell.c
    # LPI is transpose-inverse of L
    lpi = np.linalg.inv(np.transpose(mat))
    return mat, lpi


def SXTalCellType(val=None):
    """NICOS parameter validator for a single crystal cell.  Input can be:

    * a SXTalCell object
    * a 3x3 UB matrix (array or list)
    * a tuple of (UB matrix, bravais[opt], laue[opt])
    * a list with [a, b, c, alpha, beta, gamma, bravais[opt], laue[opt]]
    * a dict with the following keys:
      a, b[opt], c[opt], alpha[opt], beta[opt], gamma[opt],
      bravais[opt], laue[opt].

    Optional axes a set to the previous axis length,
    optional angles to 90deg, bravais top 'P' if omitted.
    """
    if isinstance(val, SXTalCell):
        return val
    elif isinstance(val, dict):
        return SXTalCell.fromabc(**val)
    elif isinstance(val, np.ndarray) and val.shape == (3, 3):
        return SXTalCell(val.T)
    elif isinstance(val, list) and len(val) == 3 and isinstance(val[0], list):
        return SXTalCell(np.array(val).T)
    elif isinstance(val, tuple) and len(val) <= 3:
        cellarr = np.asarray(val[0])
        if cellarr.shape == (3, 3):
            bravais = val[1] if len(val) > 1 else 'P'
            laue = val[2] if len(val) > 2 else '1'
            return SXTalCell(cellarr.T, bravais, laue)
    elif isinstance(val, (list, tuple)) and len(val) >= 6:
        bravais = val[6] if len(val) > 6 else 'P'
        laue = val[7] if len(val) > 7 else '1'
        return SXTalCell.fromabc(a=val[0], b=val[1], c=val[2],
                                 alpha=val[3], beta=val[4], gamma=val[5],
                                 bravais=bravais, laue=laue)
    raise ValueError('wrong cell specification')


class SXTalCell:

    @classmethod
    def fromabc(cls, a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0,
                bravais='P', laue='1'):
        _mat, lpi = matfromrcell(a, b, c, alpha, beta, gamma)
        return cls(np.transpose(lpi), bravais, laue)

    def __init__(self, matrix, bravais='P', laue='1'):
        self.rmat = np.array(matrix)
        self.bravais = symmetry.Bravais(bravais)
        self.laue = symmetry.Laue(laue)

    def __str__(self):
        return ('Cell: a=%.4f b=%.4f c=%.4f alpha=%.3fdeg beta=%.3fdeg '
                'gamma=%.3fdeg' % self.cellparams())

    def directmatrix(self):
        return np.linalg.inv(self.rmat)

    def cellparams(self):
        dmat = self.directmatrix()

        length = np.linalg.norm(dmat, axis=0)
        scaled = dmat / length

        a, b, c = scaled.T

        if np.all(length):
            alpha = np.rad2deg(np.arccos(np.sum(b * c)))
            beta = np.rad2deg(np.arccos(np.sum(c * a)))
            gamma = np.rad2deg(np.arccos(np.sum(a * b)))
            return CellParam(length[0], length[1], length[2], alpha, beta, gamma)
        else:
            raise RuntimeError('Zero axis length')

    def hkl(self, c):
        """Calculate the HKL indices for the given C vector."""
        return np.dot(np.linalg.inv(self.rmat.T), c)

    def CVector(self, hkl):
        """Calculate a c-vector in 0-goniometer position for a reflection.
        `hkl` is a single reflection (array of 3 elements).
        """
        return np.dot(self.rmat.T, hkl)

    def CMatrix(self, p=None):
        """Find matrix that converts HKL->oriented C vector."""
        if p:
            return np.dot(p.asG().matrix, self.rmat.T)
        else:
            return self.rmat.T

    def Shkl(self, p, reflections, s0):
        """Calculate diffracted vector Shkl for a dataset

        parameters:

            ``'p'``: position of the goniometer
            ``'hkl'``: dataset (array of hkls)
            ``'s0'``: primary beam vector (-1/wl,0,0) for nonius convention

        return value:
            Diffraction vector for each of the reflections in the dataset (3xN array)

        """
        if s0 is None:
            raise RuntimeError('Cannot calculate Shkl without knowing hardware')
        return np.dot(self.CMatrix(p), reflections) + self.s0

    def DirectVector(self, indices):
        """Calculate a direct vector pointing to the named lattice point."""
        return np.dot(np.linalg.inv(self.rmat), indices)

    def Theta(self, hkl, wavelength):
        """Calculate theta for a reflection.

        parameters:

            ``'hkl'``: a single reflection (array of 3 elements)

        return value:
            theta for the reflection
        """
        if wavelength is None:
            raise RuntimeError('Cannot calculate theta without knowing '
                               'hardware or wavelength')
        invd = np.linalg.norm(self.CVector(hkl))
        sintheta = invd * wavelength / 2.0
        return np.rad2deg(np.arcsin(sintheta))

    def dataset(self, invdmin, invdmax, uhmin=-512, uhmax=512, ukmin=-512,
                ukmax=512, ulmin=-512, ulmax=512, uniq=False):
        """Calculate a set of reflections for the given bravais lattice.

        parameters:
            ``'invdmin'`` min reciprocal lattice spacing to measure
            ``'invdmax'`` max reciprocal lattice spacing to measure

            ``'u{h,k,l}{min,max}'`` : limit h,k,l to the specified range
        """

        celmatrix = np.linalg.inv(self.rmat)
        avec, bvec, cvec = celmatrix.T  # pylint: disable=unpacking-non-sequence
        astar, bstar, cstar = self.rmat  # pylint: disable=unpacking-non-sequence
        aaangle = vecangle(avec, astar)
        bbangle = vecangle(bvec, bstar)
        ccangle = vecangle(cvec, cstar)

        (a, b, c, _al, _be, _ga) = self.cellparams()
        maxh = int(a * invdmax / np.cos(aaangle))
        maxh = max(maxh, 512)
        maxk = int(b * invdmax / np.cos(bbangle))
        maxk = max(maxk, 512)
        maxl = int(c * invdmax / np.cos(ccangle))
        maxl = max(maxl, 512)
        minh = -maxh
        mink = -maxk
        minl = -maxl
        # Apply user limits.
        minh = max(minh, uhmin)
        mink = max(mink, ukmin)
        minl = max(minl, ulmin)
        maxh = min(maxh, uhmax)
        maxk = min(maxk, ukmax)
        maxl = min(maxl, ulmax)
        result = None

        # Perform pre-loop calculations
        ahkl = self.hkl(avec)
        ahkl = ahkl / ahkl[0]
        stepused = np.linalg.norm(self.CVector(ahkl))
        cbb = np.cos(bbangle)
        ccc = np.cos(ccangle)
        for curh in range(minh, maxh + 1):
            chkl = curh * ahkl
            usedd = curh * stepused
            leftd = np.sqrt(max(0, invdmax ** 2 - usedd ** 2))
            lmink = max(int(np.ceil(chkl[1] - b * leftd / cbb)), mink)
            lmaxk = min(int(np.floor(chkl[1] + b * leftd / cbb)), maxk)
            lminl = max(int(np.ceil(chkl[2] - c * leftd / ccc)), minl)
            lmaxl = min(int(np.floor(chkl[2] + c * leftd / ccc)), maxl)
            numk = lmaxk - lmink + 1
            numl = lmaxl - lminl + 1
            numzone = numk * numl
            if numzone > 0:
                h = np.ones(numzone, dtype='i4') * curh
                k = np.repeat(range(lmink, lmaxk + 1), np.ones(numk, dtype='i4') * numl)
                if lminl == lmaxl == 0:
                    l = np.zeros([numzone], dtype='i4')
                else:
                    l = np.resize(range(lminl, lmaxl + 1), [numzone])
                zone = np.dstack((h, k, l))[0]
                # Remove bravais-forbidden
                condition = self.bravais.allowed((h, k, l))
                if uniq:
                    condition = np.logical_and(condition, self.laue.uniq((h, k, l)))
                # Now calculate 1/d for the reflections in the zone
                invd = np.transpose(np.inner(self.rmat.T, zone))
                invd = np.linalg.norm(invd, axis=1)
                # See whether 1/d is within limits
                condition = np.logical_and(condition, np.less(invd, invdmax))
                condition = np.logical_and(condition, np.greater(invd, invdmin))
                zone = np.compress(condition, zone, axis=0)
                if result is not None and zone.size:
                    result = np.concatenate((result, zone))
                elif zone.size:
                    result = zone
        return result


def _test():
    cell1 = SXTalCell([[0.2, 0.0, 0], [0, 0.2, 0], [0, 0, 0.2]])
    assert cell1.cellparams() == (5., 5., 5., 90., 90., 90.)
    cv = cell1.CVector((1, 2, 3))
    assert np.allclose(cv, (0.2, 0.4, 0.6))
    hkl = cell1.hkl(cv)
    assert np.allclose(hkl, (1, 2, 3))
    hkl = cell1.hkl((0.4, -0.6, 0.2))
    assert np.allclose(hkl, (2, -3, 1))
    assert cell1.Theta((1, 0, 0), 1.0) == np.rad2deg(np.arcsin(1 / 10.))
    cell2 = SXTalCell.fromabc(5., c=10., gamma=120.)
    assert np.allclose(cell2.cellparams(), (5., 5., 10., 90., 90., 120.))

    v = [0.7757636541238411, 0.10320040939423603, 0.826801026407413]
    a = vecangle(v, v)
    assert not np.isnan(a)
