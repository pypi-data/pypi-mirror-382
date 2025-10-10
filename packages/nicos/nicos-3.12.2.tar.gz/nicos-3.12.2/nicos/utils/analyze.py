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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

import numpy as np


def estimateFWHM(xs, ys):
    """Calculate an estimate of FWHM.

    Returns a tuple ``(fwhm, xpeak, ymax, ymin)``:

    * fwhm - full width half maximum
    * xpeak - x value at y = ymax
    * ymax - maximum y-value
    * ymin - minimum y-value
    """
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    numpoints = len(xs)

    ymin = ys.min()
    jmax = ys.argmax()
    ymax = ys[jmax]

    # Locate left and right point from the peak center where the y-value is
    # larger than the half maximum value (offset by ymin)
    y_halfmax = ymin + 0.5*(ymax - ymin)

    i1 = 0
    for index, yval in enumerate(ys[jmax-1::-1]):
        if yval <= y_halfmax:
            i1 = jmax - index
            break

    i2 = numpoints - 1
    for index, yval in enumerate(ys[jmax+1:]):
        if yval <= y_halfmax:
            i2 = jmax + 1 + index
            break

    # if not an exact match, use average
    if ys[i1] == y_halfmax or i1 == 0:
        x_hpeak_l = xs[i1]
    else:
        x_hpeak_l = (y_halfmax - ys[i1 - 1]) / (ys[i1] - ys[i1 - 1]) * \
            (xs[i1] - xs[i1 - 1]) + xs[i1 - 1]
    if ys[i2] == y_halfmax or i2 == numpoints - 1:
        x_hpeak_r = xs[i2]
    else:
        x_hpeak_r = (y_halfmax - ys[i2 - 1]) / (ys[i2] - ys[i2 - 1]) * \
            (xs[i2] - xs[i2 - 1]) + xs[i2 - 1]

    fwhm = abs(x_hpeak_l - x_hpeak_r)
    if fwhm == 0 or np.isinf(fwhm):
        # It's unlikely we have a dataset that can be fitted with a Gaussian
        # nevertheless, having no FWHM is awkward, guess something
        fwhm = 5 * abs(xs[1] - xs[0])

    # locate maximum location
    xpeak = xs[jmax]
    return (fwhm, xpeak, ymax, ymin)
