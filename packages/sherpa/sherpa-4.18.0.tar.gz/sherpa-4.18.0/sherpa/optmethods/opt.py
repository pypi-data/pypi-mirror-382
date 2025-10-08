#
#  Copyright (C) 2019-2021, 2023-2025
#  Smithsonian Astrophysical Observatory
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import operator

import numpy as np

from sherpa.utils import Knuth_close, FuncCounter
from sherpa.utils.parallel import SupportsQueue, \
    multi, context, run_tasks
from sherpa.utils.random import RandomType, uniform
from sherpa.utils.types import ArrayType


__all__ = ('Opt', 'MyNcores', 'SimplexRandom', 'SimplexNoStep',
           'SimplexStep')


FUNC_MAX = float(np.finfo(np.float64).max)

# Some code assumes the first argument is an ndarray, but is this always
# the case? For now assume that the data is always sent as an ndarray.
#
# sherpa.stats.StatCallback converts a StatFunc into an OptimizerFunc.
#
OptimizerFunc = Callable[[np.ndarray], float]

@dataclass(kw_only=True)
class OptOutput:
    """Represent the data sent around by the optimizers.

    .. versionadded:: 4.18.0

    """

    nfev: int
    """The number of function evaluations."""

    statval: float
    """The statistic value."""

    pars: np.ndarray
    """The parameter values."""


# WorkerFunc could be done as a Protocol, but the argument names are
# not consistent, and it also requires **kwargs, which has not been
# handled well by pyright. Concatenate could be used to at least
# indicate the extra arguments but that requires Python 3.11 (as
# Concatenate in Python 3.10 can not end with an ellipsis).
#
WorkerFunc = Callable[[OptimizerFunc,
                       np.ndarray,
                       np.ndarray,
                       np.ndarray,
                       float,
                       int | None
                       ],
                      OptOutput]


class MyNcores:
    """Support distributed processing."""

    def __init__(self) -> None:
        if multi is False:
            raise TypeError("multicores not available")

    def calc(self,
             funcs: Sequence[WorkerFunc],
             numcores: int,  # TODO: this is currently unused
             fcn: OptimizerFunc,
             x: np.ndarray,
             xmin: np.ndarray,
             xmax: np.ndarray,
             tol: float,
             maxnfev: int | None
             ) -> list[OptOutput]:
        """Apply each function to the arguments, running in parallel."""

        # Safety check
        nfuncs = len(funcs)
        if nfuncs == 0:
            raise TypeError("funcs can not be empty")

        for func in funcs:
            if not callable(func):
                raise TypeError(f"input func '{repr(func)}' is not callable")

        # See sherpa.utils.parallel for the logic used here.
        # At this point we can assume that context is not None,
        # since multi is True.
        #
        # Should this shard by numcores?
        #
        assert context is not None
        manager = context.Manager()
        out_q = manager.Queue()
        err_q = manager.Queue()
        procs = [context.Process(target=self.my_worker,
                                 args=(func, ii, out_q, err_q,
                                       fcn, x, xmin, xmax, tol, maxnfev)
                                 )
                 for ii, func in enumerate(funcs)]

        return run_tasks(procs, err_q, out_q)

    def my_worker(self,
                  opt: WorkerFunc,
                  idval: int,
                  out_q: SupportsQueue[tuple[int, list[OptOutput]]],
                  err_q: SupportsQueue[Exception],
                  fcn: OptimizerFunc,
                  x: np.ndarray,
                  xmin: np.ndarray,
                  xmax: np.ndarray,
                  tol: float,
                  maxnfev: int | None
                  ) -> None:
        raise NotImplementedError("my_worker has not been implemented")


class InfinitePotential:
    """Ensure the parameter values stay within bounds.

    The idea is that if sent a value outside the parameter limits we
    return "infinity" (here defined to be the maximum value we'd
    expect rather than inf, to avoid causing problems to the
    optimizer).

    .. versionadded:: 4.18.0

    See Also
    --------
    sherpa.optmethods.optfcts.InfinitePotential

    Notes
    -----

    Two differences to the optfcts version:
      - the func argument return type is different
      - the bounds here check that they lie within
            minval <= pars <= maxval
        and there is no check for NaN values

    """

    __slots__ = ("func", "minval", "maxval")

    def __init__(self,
                 func: OptimizerFunc,
                 minval: np.ndarray,
                 maxval: np.ndarray
                 ) -> None:
        self.func = func
        self.minval = minval
        self.maxval = maxval

    def __call__(self, x: np.ndarray) -> float:
        if np.any(x < self.minval) or np.any(x > self.maxval):
            return FUNC_MAX

        return self.func(x)


class Opt:
    """Base optimisation class.

    .. versionchanged:: 4.18.0
       The `func_bounds` field has been removed.

    .. versionchanged:: 4.17.0
       The class structure has been changed (e.g. `nfev` is now a
       scalar and not a single-element list).

    """

    def __init__(self,
                 func: OptimizerFunc,
                 xmin: ArrayType,
                 xmax: ArrayType
                 ) -> None:
        self.xmin = np.asarray(xmin)
        self.xmax = np.asarray(xmax)
        self.npar = len(self.xmin)
        if len(self.xmax) != self.npar:
            raise ValueError("xmin and xmax must be the same size")

        # The function counter - that is FuncCounter(func) - should
        # only be evaluated after checking whether the parameter
        # values are valid - which is handled by self.func_bounds.
        # That is,
        #
        #    self.func = self.func_bounds(FuncCounter(func), ...)
        #
        # rather than
        #
        #    self.func = FuncCounter(self.func_bounds(func, ...))
        #
        # which would count proposed parameter values which were out
        # of bounds.
        #
        self.func_count = FuncCounter(func)
        self.func = InfinitePotential(self.func_count, self.xmin,
                                      self.xmax)

    # The sub-classes have different arguments, but do have maxnfev
    # and ftol as common values.
    #
    def __call__(self,
                 maxnfev: int,
                 ftol: float,
                 *args,
                 **kwargs) -> OptOutput:
        raise NotImplementedError

    @property
    def nfev(self) -> int:
        """How many evaluations of the function have been made?

        This does not count proposed values which were outside the
        parameter limits.

        """
        return self.func_count.nfev


# The simplex field is a npop by (npar + 1) array, where each row
# contains the parameter values and then the corresponding statistic
# value for that set of parameters.
#
# The __get/setitem__ calls allow the object to index into the "pars +
# statistic array" by number (the pop argument).
#
class SimplexBase:

    def __init__(self,
                 func: OptimizerFunc,
                 npop: int,
                 xpar: ArrayType,
                 xmin: ArrayType,
                 xmax: ArrayType,
                 step: np.ndarray | None,
                 seed: int | None,
                 factor: float | None,
                 rng: RandomType | None = None
                 ) -> None:
        self.func = func
        self.xmin = np.asanyarray(xmin)
        self.xmax = np.asanyarray(xmax)
        self.npar = len(xpar)
        self.rng = rng

        self.simplex = self.init(npop=npop, xpar=np.asarray(xpar),
                                 step=step, seed=seed, factor=factor)

    def __getitem__(self, index):
        return self.simplex[index]

    def __setitem__(self, index, val) -> None:
        self.simplex[index] = val

    def calc_centroid(self) -> np.ndarray:
        return np.mean(self.simplex[:-1, :], 0)

    def check_convergence(self,
                          ftol: float,
                          method: int
                          ) -> bool:

        def are_func_vals_close_enough() -> bool:
            smallest_fct_val = self.simplex[0, -1]
            largest_fct_val = self.simplex[-1, -1]
            return Knuth_close(smallest_fct_val, largest_fct_val,
                               ftol)

        def is_fct_stddev_small_enough() -> bool:
            fval_std = np.std([col[-1] for col in self.simplex])
            # Force float comparison to avoid type checker warnings, both for
            # the arguments to the comparison and the return value.
            return float(fval_std) < float(ftol)

        def is_max_length_small_enough() -> bool:
            """

               max  || x  - x  || <= tol max(1.0, || x ||)
                        i    0                         0

            where 1 <= i <= n"""

            max_xi_x0 = -1.0
            x0 = self.simplex[0, :-1]

            npar_plus_1 = len(x0) + 1
            for ii in range(1, npar_plus_1):
                xi = self.simplex[ii, :-1]
                xi_x0 = xi - x0
                max_xi_x0 = max(max_xi_x0, np.dot(xi_x0, xi_x0))

            # force float conversion to avoid type checker warnings
            return max_xi_x0 <= float(ftol) * max(1.0, np.dot(x0, x0))

        if 0 == method:
            if is_max_length_small_enough():
                return True
        elif 2 == method:
            if not is_max_length_small_enough():
                return False
            stddev = is_fct_stddev_small_enough()
            fctval = are_func_vals_close_enough()
            return stddev and fctval
        else:
            if not is_max_length_small_enough():
                return False
            stddev = is_fct_stddev_small_enough()
            fctval = are_func_vals_close_enough()
            return stddev or fctval

        return False

        # TODO: what is this code meant to be doing as it is unreachable?
        #
        # It has therefore been commented out.
        #
        # num = 2.0 * abs(self.simplex[0, -1] - self.simplex[-1, -1])
        # denom = abs(self.simplex[0, -1]) + abs(self.simplex[-1, -1]) + 1.0
        # if num / denom > ftol:
        #     return False
        #
        # func_vals = [col[-1] for col in self.simplex]
        # if np.std(func_vals) > ftol:
        #     return False
        #
        # return True

    def eval_simplex(self,
                     npop: int,
                     simplex: np.ndarray
                     ) -> np.ndarray:
        for ii in range(npop):
            simplex[ii][-1] = self.func(simplex[ii][:-1])
        return self.sort_me(simplex)

    def init(self,
             npop: int,
             xpar: np.ndarray,
             step: np.ndarray | None,
             seed: int | None,
             factor: float | None
             ) -> np.ndarray:
        raise NotImplementedError("init has not been implemented")

    def init_random_simplex(self,
                            xpar: np.ndarray,
                            simplex: np.ndarray,
                            start: int,
                            npop: int,
                            seed: int | None,
                            factor: float | None
                            ) -> np.ndarray:
        # Set the seed when there is no RNG set, otherwise the RNG
        # determines the state.
        #
        if self.rng is None:
            np.random.seed(seed)

        # This could be done before changing the seed, but code may
        # require the current behavior.
        #
        if start >= npop:
            return simplex

        # At this point it is assumed the caller has set factor.
        #
        assert factor is not None, "caller did not set factor"
        deltas = factor * np.abs(np.asarray(xpar))
        xmins = np.maximum(self.xmin, xpar - deltas)
        xmaxs = np.minimum(self.xmax, xpar + deltas)
        for ii in range(start, npop):
            simplex[ii][:-1] = uniform(self.rng, xmins, xmaxs)

        return simplex

    def move_vertex(self,
                    centroid: np.ndarray,
                    coef: float
                    ) -> np.ndarray:
        vertex = (1.0 + coef) * centroid - coef * self.simplex[self.npar]
        vertex[-1] = self.func(vertex[:-1])
        return vertex

    def shrink(self, shrink_coef: float) -> None:

        self.simplex[1:] = self.simplex[0] + \
            shrink_coef * (self.simplex[1:] - self.simplex[0])

        for simplex in self.simplex[1:]:
            simplex[-1] = self.func(simplex[:-1])

    @staticmethod
    def sort_me(simp: np.ndarray
                ) -> np.ndarray:
        """Reorder the simplex by the statistic value (low to high)"""
        myshape = simp.shape
        tmp = np.array(sorted(simp, key=operator.itemgetter(-1)))
        tmp.reshape(myshape)
        return tmp

    def sort(self) -> None:
        self.simplex = self.sort_me(self.simplex)


class SimplexNoStep(SimplexBase):

    def init(self,
             npop: int,
             xpar: np.ndarray,
             step: np.ndarray | None,
             seed: int | None,
             factor: float | None
             ) -> np.ndarray:
        npar1 = self.npar + 1
        simplex = np.empty((npop, npar1))
        simplex[0][:-1] = np.copy(xpar)
        for ii in range(self.npar):
            tmp = np.copy(xpar)
            if 0.0 == tmp[ii]:
                tmp[ii] = 2.5e-4
            else:
                tmp[ii] *= 1.05
            simplex[ii+1][:-1] = tmp[:]

        simplex = self.init_random_simplex(xpar, simplex, start=npar1,
                                           npop=npop, seed=seed,
                                           factor=factor)
        return self.eval_simplex(npop, simplex)


class SimplexStep(SimplexBase):

    def init(self,
             npop: int,
             xpar: np.ndarray,
             step: np.ndarray | None,
             seed: int | None,
             factor: float | None
             ) -> np.ndarray:

        # This should raise an error, but as it is low-level code, just
        # use an assert.
        assert step is not None

        npar1 = self.npar + 1
        simplex = np.empty((npop, npar1))
        simplex[0][:-1] = np.copy(xpar)
        for ii in range(self.npar):
            tmp = xpar[ii] + step[ii]
            simplex[ii + 1][:-1] = tmp

        simplex = self.init_random_simplex(xpar, simplex, start=npar1,
                                           npop=npop, seed=seed, factor=factor)
        return self.eval_simplex(npop, simplex)


class SimplexRandom(SimplexBase):

    def init(self,
             npop: int,
             xpar: np.ndarray,
             step: np.ndarray | None,
             seed: int | None,
             factor: float | None
             ) -> np.ndarray:
        npar1 = self.npar + 1
        simplex = np.empty((npop, npar1))
        simplex[0][:-1] = np.copy(xpar)

        simplex = self.init_random_simplex(xpar, simplex, start=1,
                                           npop=npop, seed=seed,
                                           factor=factor)
        return self.eval_simplex(npop, simplex)
