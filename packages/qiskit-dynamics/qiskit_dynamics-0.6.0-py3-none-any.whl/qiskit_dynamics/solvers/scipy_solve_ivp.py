# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=invalid-name

"""
Wrapper for calling scipy.integrate.solve_ivp.
"""

from typing import Callable, Union, Optional

import numpy as np
from scipy.integrate import solve_ivp, OdeSolver
from scipy.integrate._ivp.ivp import OdeResult

from qiskit import QiskitError
from qiskit_dynamics.arraylias import ArrayLike

# Supported scipy ODE methods
COMPLEX_METHODS = ["RK45", "RK23", "BDF", "DOP853"]
REAL_METHODS = ["LSODA", "Radau"]
SOLVE_IVP_METHODS = COMPLEX_METHODS + REAL_METHODS


def scipy_solve_ivp(
    rhs: Callable,
    t_span: ArrayLike,
    y0: ArrayLike,
    method: Union[str, OdeSolver],
    t_eval: Optional[ArrayLike] = None,
    **kwargs,
):
    """Routine for calling `scipy.integrate.solve_ivp`.

    Args:
        rhs: Callable of the form :math:`f(t, y)`.
        t_span: Interval to solve over.
        y0: Initial state.
        method: Solver method.
        t_eval: Points at which to evaluate the solution.
        **kwargs: Optional arguments to be passed to ``solve_ivp``.

    Returns:
        OdeResult: results object

    Raises:
        QiskitError: If unsupported kwarg present.
    """

    if kwargs.get("dense_output", False) is True:
        raise QiskitError("dense_output not supported for solve_ivp.")

    y_shape = y0.shape

    # flatten y0 and rhs
    y0 = y0.flatten()
    rhs = flat_rhs(rhs, y_shape)

    # Check if solver is real only
    # TODO: Also check if model or y0 are complex
    #       if they are both real we don't need to embed.
    embed_real = method in REAL_METHODS
    if embed_real:
        rhs = real_rhs(rhs)
        y0 = c2r(y0)

    results = solve_ivp(rhs, t_span=t_span, y0=y0.data, t_eval=t_eval, method=method, **kwargs)
    if embed_real:
        results.y = r2c(results.y)

    # convert to the standardized results format
    # solve_ivp returns the states as a 2d array with columns being the states
    results.y = results.y.transpose()
    results.y = np.array([y.reshape(y_shape) for y in results.y])

    return OdeResult(**dict(results))


def flat_rhs(rhs, shape):
    """Convert an RHS with arbitrary state shape into one that is 1d."""

    def _flat_rhs(t, y):
        return rhs(t, y.reshape(shape)).flatten()

    return _flat_rhs


def real_rhs(rhs):
    """Convert complex RHS to real RHS function"""

    def _real_rhs(t, y):
        return c2r(rhs(t, r2c(y)))

    return _real_rhs


def c2r(arr):
    """Convert complex array to a real array"""
    return np.concatenate([np.real(arr), np.imag(arr)])


def r2c(arr):
    """Convert a real array to a complex array"""
    size = arr.shape[0] // 2
    return arr[:size] + 1j * arr[size:]
