#
#  Copyright (C) 2011, 2015, 2016, 2019-2021, 2023, 2025
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

import logging
from typing import Literal

import numpy as np

from sherpa.estmethods import Covariance, Confidence
from sherpa.fit import Fit
from sherpa.utils import NoNewAttributesAfterInit, random
from sherpa.utils.err import EstErr
from sherpa.utils.parallel import parallel_map
from sherpa.utils.types import ArrayType

warning = logging.getLogger("sherpa").warning


__all__ = ('multivariate_t', 'multivariate_cauchy',
           'normal_sample', 'uniform_sample', 't_sample',
           'ParameterScaleVector', 'ParameterScaleMatrix',
           'UniformParameterSampleFromScaleVector',
           'NormalParameterSampleFromScaleVector',
           'NormalParameterSampleFromScaleMatrix',
           'StudentTParameterSampleFromScaleMatrix',
           'NormalSampleFromScaleMatrix', 'NormalSampleFromScaleVector',
           'UniformSampleFromScaleVector', 'StudentTSampleFromScaleMatrix',
           )


def multivariate_t(mean: ArrayType,
                   cov: np.ndarray,
                   df: int,
                   size: tuple[int, ...] | None = None,
                   rng: random.RandomType | None = None
                   ) -> np.ndarray:
    """Draw random deviates from a multivariate Student's T distribution.

    Such a distribution is specified by its mean covariance matrix,
    and degrees of freedom.  These parameters are analogous to the
    mean (average or "center"), variance (standard deviation, or
    "width," squared), and the degrees of freedom of the
    one-dimensional t distribution.

    .. versionchanged:: 4.16.0
       The rng parameter was added.

    Parameters
    ----------
    mean : 1-D array_like, length N
        Mean of the N-dimensional distribution
    cov : 2-D array_like, shape (N, N)
        Covariate matrix of the distribution.  Must be symmetric and
        positive semi-definite for "physically meaningful" results.
    df : int
        Degrees of freedom of the distribution
    size : tuple of ints, optional
        Given a shape of, for example, ``(m,n,k)``, ``m*n*k`` samples are
        generated, and packed in an `m`-by-`n`-by-`k` arrangement.  Because
        each sample is `N`-dimensional, the output shape is ``(m,n,k,N)``.
        If no shape is specified, a single (`N`-D) sample is returned.
    rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
        Determines how random numbers are created. If set to None then
        the routines from `numpy.random` are used, and so can be
        controlled by calling `numpy.random.seed`.

    Returns
    -------
    out : ndarray
        The drawn samples, of shape *size*, if that was provided.  If not,
        the shape is ``(N,)``.

        In other words, each entry ``out[i,j,...,:]`` is an N-dimensional
        value drawn from the distribution.

    Is this right?  This needs to be checked!  A reference to the literature
    the better

    """
    dff = float(df)
    mean = np.asarray(mean)

    normal = random.multivariate_normal(rng, np.zeros_like(mean), cov,
                                        size=size)
    x = np.sqrt(random.chisquare(rng, dff, size=size) / dff)
    np.divide(normal, x[np.newaxis].T, normal)
    np.add(mean, normal, normal)
    x = normal
    return x


# TODO: should this pass the size value through to multivariate_t?
#
def multivariate_cauchy(mean: ArrayType,
                        cov: np.ndarray,
                        size: tuple[int, ...] | None = None,
                        rng: random.RandomType | None = None
                        ) -> np.ndarray:
    """
    This needs to be checked too! A reference to the literature the better

    .. versionchanged:: 4.16.0
       The rng parameter was added.

    """
    return multivariate_t(mean, cov, 1, size=None, rng=rng)


class ParameterScale(NoNewAttributesAfterInit):
    """Create the scaling used to generate parameters.

    The scaling generally refers to an error value (defaulting
    to one sigma) for each parameter.

    """

    # The sigma value to use
    sigma: float = 1

    def get_scales(self,
                   fit: Fit,
                   myscales: np.ndarray | None = None
                   ) -> np.ndarray:
        """Return the samples.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
            This defines the thawed parameters that are used to
            generate the samples, along with any possible error
            analysis.
        myscales : numpy array or None, optional
            The scales to use. If None then they are
            calculated from the fit.

        Returns
        -------
        scales : numpy array
            The scales array (npar elements, matching the free
            parameters in fit). It may be multi-dimensional.

        """
        raise NotImplementedError


class ParameterScaleVector(ParameterScale):
    """Uncorrelated errors for the parameters.

    """

    def get_scales(self,
                   fit: Fit,
                   myscales: np.ndarray | None = None
                   ) -> np.ndarray:
        """Return the samples.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
            This defines the thawed parameters that are used to
            generate the samples, along with any possible error
            analysis.
        myscales : numpy array or None, optional
            The scales to use: a one-dimensional array of the standard
            deviation for each parameter (so there is no correlation
            between the parameters). If None then they are calculated
            from the fit, using the object's sigma attribute to scale
            the results.

        Returns
        -------
        scales : numpy array
            One-dimensional array with npar elements, where npar is
            the number of free parameters in the fit. The values are
            the standard deviations for the free parameters, scaled by
            the sigma value (or the input values if myscales is not
            None).

        """

        scales = []
        thawedpars = fit.model.get_thawed_pars()
        npar = len(thawedpars)

        if myscales is None:

            oldestmethod = fit.estmethod

            covar = Covariance()
            covar.config['sigma'] = self.sigma
            fit.estmethod = covar

            try:
                r = fit.est_errors()
            finally:
                fit.estmethod = oldestmethod

            for par, val, lo, hi in zip(thawedpars, r.parvals, r.parmins, r.parmaxes):
                scale = None
                if lo is not None and hi is not None:
                    scale = abs(lo)
                else:
                    warning("Covariance failed for '%s', trying Confidence...",
                            par.fullname)

                    conf = Confidence()
                    conf.config['sigma'] = self.sigma
                    fit.estmethod = conf
                    try:
                        t = fit.est_errors(parlist=(par,))

                        # QUS: could this not be
                        #
                        #   if parmin is not None:
                        #      use abs(parmin)
                        #   elif parmax is not None
                        #      use abs(parmax)
                        #   else
                        #      ...
                        #
                        # It would potentially change the results from
                        # some analyses.
                        #
                        if t.parmaxes[0] is not None:
                            if t.parmins[0] is not None:
                                scale = abs(t.parmins[0])
                            else:
                                scale = abs(t.parmaxes[0])

                        else:
                            warning('%g sigma bounds for parameter '
                                    '%s could not be found, using '
                                    'soft limit minimum',
                                    self.sigma, par.fullname)
                            if 0.0 == abs(par.min):
                                scale = 1.0e-16
                            else:
                                scale = abs(par.min)

                    finally:
                        fit.estmethod = oldestmethod

                scales.append(scale)

        elif np.iterable(myscales):
            scales = abs(np.asarray(myscales))
            if len(scales) != npar:
                raise TypeError("scales option must be iterable of "
                                f"length {npar}")

        else:
            raise TypeError("scales option must be iterable of "
                            f"length {npar}")

        return np.asarray(scales)


class ParameterScaleMatrix(ParameterScale):
    """Correlated errors for the parameters.

    """

    def get_scales(self,
                   fit: Fit,
                   myscales: np.ndarray | None = None
                   ) -> np.ndarray:
        """Return the samples.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
            This defines the thawed parameters that are used to
            generate the samples, along with any possible error
            analysis.
        myscales : numpy array or None, optional
            The scales to use: the two-dimensional covariance matrix
            for the parameters.  If None then they are calculated from
            the fit, using the object's sigma attribute to scale the
            results.

        Returns
        -------
        scales : numpy array
            Two-dimensional square array of side npar, where npar is
            the number of free parameters in the fit. The values are
            the covariance matrix for the free parameters, scaled by
            the sigma value (or the input values if myscales is not
            None).

        """

        if myscales is None:
            oldestmethod = fit.estmethod
            covar = Covariance()
            covar.config['sigma'] = self.sigma
            fit.estmethod = covar

            try:
                r = fit.est_errors()
            finally:
                fit.estmethod = oldestmethod

            cov = r.extra_output
            if cov is None:
                raise EstErr('nocov')

            # Scale the covariance matrix by the square of the
            # sigma value (which is expected to be 1, although it
            # can be changed).
            #
            cov = self.sigma**2 * cov

        else:
            # NOTE: the self.sigma value is not used when the scales
            # are manually sent in (it is up to the user to send in
            # the expected scaled covariance matrix).
            #
            npar = len(fit.model.thawedpars)
            msg = f'scales must be a numpy array of size ({npar},{npar})'

            if not isinstance(myscales, np.ndarray):
                raise EstErr(msg)

            if (npar, npar) != myscales.shape:
                raise EstErr(msg)

            cov = np.asarray(myscales)

        # Investigate spectral decomposition to avoid requirement that
        # the cov be semi-positive definite.  Nevermind, NumPy already
        # uses SVD to generate deviates from a multivariate normal.
        # An alternative is to use Cholesky decomposition, but it
        # assumes that the matrix is semi-positive definite.
        #
        if np.min(np.linalg.eigvalsh(cov)) <= 0:
            raise TypeError("The covariance matrix is not positive definite")

        return cov


ClipValue = Literal["none"] | Literal["hard"] | Literal["soft"]


class ParameterSample(NoNewAttributesAfterInit):
    """Create a set of parameter samples.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   num: int = 1,
                   rng: random.RandomType | None = None
                   ) -> np.ndarray:
        """Return the samples.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        num : int, optional
           The number of samples to return.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.

        Returns
        -------
        samples : 2D numpy array
           The array is num by npar size, where npar is the number of
           free parameters in the fit argument.

        """
        raise NotImplementedError

    def clip(self,
             fit: Fit,
             samples: np.ndarray,
             clip: ClipValue = 'none'
             ) -> np.ndarray:
        """Clip the samples if out of bounds.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
            Contains the thawed parameters used to generate the
            samples.
        samples : 2D numpy array
            The samples array, stored as a n by npar matrix. This
            array is changed in place.
        clip : {'none', 'hard', 'soft'} optional
            How should the values be clipped? The default ('none') has no
            clipping. The other methods restrict the values to lie within
            the hard or soft limits of the parameters.

        Returns
        -------
        clipped : 1D numpy array
            A 1D boolean array indicating whether any sample in a row
            was clipped. Note that the input samples array will have
            been updated if any element in clipped is True.

        """

        niter = samples.shape[0]
        clipped = np.zeros(niter, dtype=bool)
        if clip == 'none':
            return clipped

        # Values are clipped to lie within mins/maxs (inclusive)
        #
        if clip == 'hard':
            mins = fit.model.thawedparhardmins
            maxs = fit.model.thawedparhardmaxes
        elif clip == 'soft':
            mins = fit.model.thawedparmins
            maxs = fit.model.thawedparmaxes
        else:
            raise ValueError(f'invalid clip argument: sent {clip}')

        for pvals, pmin, pmax in zip(samples.T, mins, maxs):
            porig = pvals.copy()

            # do the clipping in place
            np.clip(pvals, pmin, pmax, out=pvals)

            # update the clipped array (which is True if a
            # value on the row has been clipped).
            #
            clipped |= (pvals != porig)

        return clipped


class ParameterSampleFromScaleVector(ParameterSample):
    """Samples drawn from uncorrelated parameters.
    """

    def __init__(self) -> None:
        self.scale = ParameterScaleVector()
        super().__init__()


class ParameterSampleFromScaleMatrix(ParameterSample):
    """Samples drawn from correlated parameters.
    """

    def __init__(self) -> None:
        self.scale = ParameterScaleMatrix()
        super().__init__()


class UniformParameterSampleFromScaleVector(ParameterSampleFromScaleVector):
    """Use a uniform distribution to sample parameters.

    The parameters are drawn from a uniform distribution which is set
    to `factor` times the parameter error (the lower bound is included
    but the upper bound is not).
    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   factor: float = 4,
                   num: int = 1,
                   rng: random.RandomType | None = None
                   ) -> np.ndarray:
        """Return the parameter samples.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        factor : number, optional
           The half-width of the uniform distribution is factor times
           the one-sigma error.
        num : int, optional
           The number of samples to return.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.

        Returns
        -------
        samples : 2D numpy array
           The array is num by npar size, where npar is the number of
           free parameters in the fit argument.

        """
        vals = np.array(fit.model.thawedpars)
        scales = self.scale.get_scales(fit)
        size = int(num)
        samples = [random.uniform(rng,
                                  val - factor * abs(scale),
                                  val + factor * abs(scale),
                                  size=size)
                   for val, scale in zip(vals, scales)]
        return np.asarray(samples).T


class NormalParameterSampleFromScaleVector(ParameterSampleFromScaleVector):
    """Use a normal distribution to sample parameters (uncorrelated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and do not include any correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   myscales: np.ndarray | None = None,
                   num: int = 1,
                   rng: random.RandomType | None = None
                   ) -> np.ndarray:
        """Return the parameter samples.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        myscales : 1D numpy array or None, optional
           The standard deviation values for the free parameters in
           the fit. If None then the values are calculated from the
           fit and scaled by the sigma value of the scale object.
        num : int, optional
           The number of samples to return.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.

        Returns
        -------
        samples : 2D numpy array
            The array is num by npar size, where npar is the number of
            free parameters in the fit argument.

        """
        vals = np.array(fit.model.thawedpars)
        scales = self.scale.get_scales(fit, myscales=myscales)
        size = int(num)

        samples = [random.normal(rng, loc=val, scale=scale, size=size)
                   for val, scale in zip(vals, scales)]
        return np.asarray(samples).T


class NormalParameterSampleFromScaleMatrix(ParameterSampleFromScaleMatrix):
    """Use a normal distribution to sample parameters (correlated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and include the correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly as a covariance matrix.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   mycov: np.ndarray | None = None,
                   num: int = 1,
                   rng: random.RandomType | None = None
                   ) -> np.ndarray:
        """Return the parameter samples.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        mycov : 2D numpy array or None, optional
           The covariance matrix for the free parameters in the
           fit. If None then the values are calculated from the fit
           and scaled by the sigma value of the scale object.
        num : int, optional
           The number of samples to return.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.

        Returns
        -------
        samples : 2D numpy array
            The array is num by npar size, where npar is the number of
            free parameters in the fit argument.

        """
        vals = np.array(fit.model.thawedpars)
        cov = self.scale.get_scales(fit, myscales=mycov)
        return random.multivariate_normal(rng, mean=vals, cov=cov,
                                          size=int(num))


class StudentTParameterSampleFromScaleMatrix(ParameterSampleFromScaleMatrix):
    """Use a student's t-distribution to sample parameters (correlated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and include the correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly as a covariance matrix.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   dof: int,
                   num: int = 1,
                   rng: random.RandomType | None = None,
                   ) -> np.ndarray:
        """Return the parameter samples.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        dof : int
           The degrees of freedom of the distribution.
        num : int, optional
           The number of samples to return.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.

        Returns
        -------
        samples : 2D numpy array
           The array is num by npar size, where npar is the number of
           free parameters in the fit argument.

        """
        vals = np.array(fit.model.thawedpars)
        cov = self.scale.get_scales(fit)
        return multivariate_t(vals, cov=cov, df=dof, size=int(num),
                              rng=rng)


class Evaluate:
    """
    Callable class for _sample_stat multiprocessing call
    This class used to be a nested function, which can't be pickled and results in
    python3 failing to execute the code.

    Note that this does not guarantee to reset the model
    parameters after being run.
    """

    def __init__(self, fit: Fit) -> None:
        self.fit = fit

    def __call__(self, sample: np.ndarray) -> float:
        self.fit.model.thawedpars = sample
        return self.fit.calc_stat()


def _sample_stat(fit: Fit,
                 samples: np.ndarray,
                 clipped: np.ndarray,
                 *,
                 numcores: int | None = None,
                 cache: bool = True
                 ) -> np.ndarray:
    """Calculate the statistic for each set of samples.

    Parameters
    ----------
    fit : sherpa.fit.Fit instance
        This defines the thawed parameters that are used to generate
        the samples, along with any possible error analysis.
    samples : 2D numpy array
        The samples array, stored as a npar by niter matrix.
    clipped : numpy array
        Whether the parameter row included clipped parameters (1) or
        not (0).
    numcores : int or None, optional
        Should the calculation be done on multiple CPUs?  The default
        (None) is to rely on the parallel.numcores setting of the
        configuration file.
    cache : bool, optional
        Should the model cache be used?

    Returns
    -------
    vals : 2D numpy array
        A copy of the samples input with an extra row added to its
        start, giving the statistic value for that row, and at the
        end, containing the clipped array.

    """

    oldvals = fit.model.thawedpars

    # QUS: does the cache really help when run in parallel?
    try:
        fit.model.startup(cache=cache)
        stats = np.asarray(parallel_map(Evaluate(fit), samples, numcores))
    finally:
        fit.model.teardown()
        fit.model.thawedpars = oldvals

    return np.concatenate([stats[:, np.newaxis],
                           samples,
                           clipped[:, np.newaxis]
                           ], axis=1)


# Note:
#
# NormalParameterSampleFromScaleXXX does not take a clip argument,
# since this is handled explicitly by the called (e.g. in #866 where
# explicit calls to .clip are made for the flux code in sherpa.astro.flux).
# However, since the clipping needs to be done *before* calculating the
# sample values (or, it makes sense to do so), clip has been added to
# the get_sample call here. This is less-than ideal.
#
class NormalSampleFromScaleMatrix(NormalParameterSampleFromScaleMatrix):
    """Use a normal distribution to sample statistic and parameters (correlated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and include the correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly as a covariance matrix.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   num: int = 1,
                   numcores: int | None = None,
                   rng: random.RandomType | None = None,
                   clip: ClipValue = "none"
                   ) -> np.ndarray:
        """Return the statistic and parameter samples.

        .. versionchanged:: 4.18.0
           The clip argument has been added, and the return value now
           has an extra column, indicating if the row was clipped.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        num : int, optional
           The number of samples to return.
        numcores : int or None, optional
           Should the calculation be done on multiple CPUs?
           The default (None) is to rely on the parallel.numcores
           setting of the configuration file.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.
        clip : {'hard', 'soft', 'none'}, optional
           What clipping strategy should be applied to the sampled
           parameters. The default ('none') applies no clipping,
           'hard' uses the hard parameter limits, and 'soft' the soft
           limits.

        Returns
        -------
        samples : 2D numpy array
           The array is num by (npar + 2) size, where npar is the
           number of free parameters in the fit argument. The first
           element in each row is the statistic value, the remaining
           are the parameter values, and then the last column
           indicates whether any parameters were clipped.

        """

        # Knowledge of whether a row has been clipped is dropped
        samples = super().get_sample(fit, num=num, rng=rng)
        clipped = self.clip(fit, samples, clip=clip)
        return _sample_stat(fit, samples, clipped, numcores=numcores)


class NormalSampleFromScaleVector(NormalParameterSampleFromScaleVector):
    """Use a normal distribution to sample statistic and parameters (uncorrelated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and do not include any correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly as a covariance matrix.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   num: int = 1,
                   numcores: int | None = None,
                   rng: random.RandomType | None = None,
                   clip: ClipValue = "none"
                   ) -> np.ndarray:
        """Return the statistic and parameter samples.

        .. versionchanged:: 4.18.0
           The clip argument has been added, and the return value now
           has an extra column, indicating if the row was clipped.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        num : int, optional
           The number of samples to return.
        numcores : int or None, optional
           Should the calculation be done on multiple CPUs?
           The default (None) is to rely on the parallel.numcores
           setting of the configuration file.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.
        clip : {'hard', 'soft', 'none'}, optional
           What clipping strategy should be applied to the sampled
           parameters. The default ('none') applies no clipping,
           'hard' uses the hard parameter limits, and 'soft' the soft
           limits.

        Returns
        -------
        samples : 2D numpy array
           The array is num by (npar + 2) size, where npar is the
           number of free parameters in the fit argument. The first
           element in each row is the statistic value, the remaining
           are the parameter values, and then the last column
           indicates whether any parameters were clipped.

        """

        # Knowledge of whether a row has been clipped is dropped
        samples = super().get_sample(fit, num=num, rng=rng)
        clipped = self.clip(fit, samples, clip=clip)
        return _sample_stat(fit, samples, clipped, numcores=numcores)


class UniformSampleFromScaleVector(UniformParameterSampleFromScaleVector):
    """Use a uniform distribution to sample statistic and parameters.

    The parameters are drawn from a uniform distribution which is set
    to `factor` times the parameter error (the lower bound is included
    but the upper bound is not).
    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   num: int = 1,
                   factor: float = 4,
                   numcores: int | None = None,
                   rng: random.RandomType | None = None,
                   clip: ClipValue = "none"
                   ) -> np.ndarray:
        """Return the statistic and parameter samples.

        .. versionchanged:: 4.18.0
           The clip argument has been added, and the return value now
           has an extra column, indicating if the row was clipped.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        num : int, optional
           The number of samples to return.
        factor : number, optional
           The half-width of the uniform distribution is factor times
           the one-sigma error.
        numcores : int or None, optional
           Should the calculation be done on multiple CPUs?
           The default (None) is to rely on the parallel.numcores
           setting of the configuration file.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.
        clip : {'hard', 'soft', 'none'}, optional
           What clipping strategy should be applied to the sampled
           parameters. The default ('none') applies no clipping,
           'hard' uses the hard parameter limits, and 'soft' the soft
           limits.

        Returns
        -------
        samples : 2D numpy array
           The array is num by (npar + 2) size, where npar is the
           number of free parameters in the fit argument. The first
           element in each row is the statistic value, the remaining
           are the parameter values, and then the last column
           indicates whether any parameters were clipped.

        """
        samples = super().get_sample(fit, factor=factor, num=num,
                                     rng=rng)
        clipped = self.clip(fit, samples, clip=clip)
        return _sample_stat(fit, samples, clipped, numcores=numcores)


class StudentTSampleFromScaleMatrix(StudentTParameterSampleFromScaleMatrix):
    """Use a student's t-distribution to sample statistic and parameters (correlated),

    The parameters are drawn from a normal distribution based on the
    parameter errors, and include the correlations between the
    parameters. The errors will be generated from the fit object or
    specified directly as a covariance matrix.

    """

    def get_sample(self,
                   fit: Fit,
                   *,
                   num: int = 1,
                   dof: int = 2,
                   numcores: int | None = None,
                   rng: random.RandomType | None = None,
                   clip: ClipValue = "none"
                   ) -> np.ndarray:
        """Return the statistic and parameter samples.

        .. versionchanged:: 4.18.0
           The clip argument has been added, and the return value now
           has an extra column, indicating if the row was clipped.

        .. versionchanged:: 4.16.0
           All arguments but the first one must be passed as a keyword
           argument. The rng parameter was added.

        Parameters
        ----------
        fit : sherpa.fit.Fit instance
           This defines the thawed parameters that are used to generate
           the samples, along with any possible error analysis.
        num : int, optional
           The number of samples to return.
        dof : int
           The degrees of freedom of the distribution.
        numcores : int or None, optional
           Should the calculation be done on multiple CPUs?
           The default (None) is to rely on the parallel.numcores
           setting of the configuration file.
        rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
           Determines how random numbers are created. If set to None
           then the routines from `numpy.random` are used, and so can
           be controlled by calling `numpy.random.seed`.
        clip : {'hard', 'soft', 'none'}, optional
           What clipping strategy should be applied to the sampled
           parameters. The default ('none') applies no clipping,
           'hard' uses the hard parameter limits, and 'soft' the soft
           limits.

        Returns
        -------
        samples : 2D numpy array
           The array is num by (npar + 2) size, where npar is the
           number of free parameters in the fit argument. The first
           element in each row is the statistic value, the remaining
           are the parameter values, and then the last column
           indicates whether any parameters were clipped.

        """
        samples = super().get_sample(fit, dof=dof, num=num, rng=rng)
        clipped = self.clip(fit, samples, clip=clip)
        return _sample_stat(fit, samples, clipped, numcores=numcores)



def normal_sample(fit: Fit,
                  num: int = 1,
                  scale: float = 1,
                  correlate: bool = True,
                  numcores: int | None = None,
                  rng: random.RandomType | None = None,
                  clip: ClipValue = "none"
                  ) -> np.ndarray:
    """Sample the fit statistic by taking the parameter values
    from a normal distribution.

    For each iteration (sample), change the thawed parameters by
    drawing values from a uni- or multi-variate normal (Gaussian)
    distribution, and calculate the fit statistic.

    .. versionchanged:: 4.18.0
       The sigma parameter has been renamed to scale, and the code has
       been updated so that changing it will change the sampled
       values. The clip parameter has been added, and the return value
       contains an extra column indicating whether a parameter in the
       row was clipped.

    .. versionchanged:: 4.16.0
       The rng parameter was added.

    Parameters
    ----------
    fit :
       The fit results.
    num : int, optional
       The number of samples to use (default is `1`).
    scale : number, optional
       Scale factor applied to the sigma values from the fit before
       sampling the normal distribution.
    correlate : bool, optional
       Should a multi-variate normal be used, with parameters
       set by the covariance matrix (`True`) or should a
       uni-variate normal be used (`False`)?
    numcores : optional
       The number of CPU cores to use. The default is to use all
       the cores on the machine.
    rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
       Determines how random numbers are created. If set to None then
       the routines from `numpy.random` are used, and so can be
       controlled by calling `numpy.random.seed`.
    clip : {'hard', 'soft', 'none'}, optional
       What clipping strategy should be applied to the sampled
       parameters. The default ('none') applies no clipping, 'hard'
       uses the hard parameter limits, and 'soft' the soft limits.

    Returns
    -------
    samples
       A NumPy array table with the first column representing the
       statistic, the later columns the parameters used, and the last
       column indicating whether any parameter in the row was clipped.

    See Also
    --------
    t_sample : Sample from the Student's t-distribution.
    uniform_sample : Sample from a uniform distribution.

    Notes
    -----

    It is expected that the model has already been fit to the data.

    All thawed model parameters are sampled from the Gaussian
    distribution. The mean is set as the current parameter values. The
    variance is calculated from the covariance matrix of the fit
    multiplied by scale * scale. When correlate is False the diagonal
    of the matrix is used, so the parameters are uncorrelated. When
    correlate is True the full matrix is used, allowing for
    correlations between the parameters.

    """
    if correlate:
        sampler = NormalSampleFromScaleMatrix()
    else:
        sampler = NormalSampleFromScaleVector()

    sampler.scale.sigma = scale
    return sampler.get_sample(fit, num=num, numcores=numcores,
                              rng=rng, clip=clip)


def uniform_sample(fit: Fit,
                   num: int = 1,
                   factor: float = 4,
                   numcores: int | None = None,
                   rng: random.RandomType | None = None,
                   clip: ClipValue = "none"
                   ) -> np.ndarray:
    """Sample the fit statistic by taking the parameter values
    from an uniform distribution.

    For each iteration (sample), change the thawed parameters by
    drawing values from a uniform distribution, and calculate the
    fit statistic.

    .. versionchanged:: 4.18.0
       The sigma parameter has been renamed to scale, and the code has
       been updated so that changing it will change the sampled
       values. The clip parameter has been added, and the return value
       contains an extra column indicating whether a parameter in the
       row was clipped.

    .. versionchanged:: 4.16.0
       The rng parameter was added.

    Parameters
    ----------
    fit :
       The fit results.
    num : int, optional
       The number of samples to use (default is `1`).
    factor : number, optional
       Multiplier to expand the scale parameter (default is `4`).
    numcores : optional
       The number of CPU cores to use. The default is to use all
       the cores on the machine.
    rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
       Determines how random numbers are created. If set to None then
       the routines from `numpy.random` are used, and so can be
       controlled by calling `numpy.random.seed`.
    clip : {'hard', 'soft', 'none'}, optional
       What clipping strategy should be applied to the sampled
       parameters. The default ('none') applies no clipping, 'hard'
       uses the hard parameter limits, and 'soft' the soft limits.

    Returns
    -------
    samples :
       A NumPy array table with the first column representing the
       statistic, the later columns the parameters used, and the last
       column indicating whether any parameter in the row was clipped.

    See Also
    --------
    normal_sample : Sample from a normal distribution.
    t_sample : Sample from the Student's t-distribution.

    """
    sampler = UniformSampleFromScaleVector()
    # The factor and sigma arguments have the same effect, so fix
    # sigma at 1.
    sampler.scale.sigma = 1
    return sampler.get_sample(fit, num=num, factor=factor,
                              numcores=numcores, rng=rng,
                              clip=clip)


def t_sample(fit: Fit,
             num: int = 1,
             dof: int = 2,
             numcores: int | None = None,
             rng: random.RandomType | None = None,
             clip: ClipValue = "none"
             ) -> np.ndarray:
    """Sample the fit statistic by taking the parameter values from
    a Student's t-distribution.

    For each iteration (sample), change the thawed parameters
    by drawing values from a Student's t-distribution, and
    calculate the fit statistic.

    .. versionchanged:: 4.18.0
       The sigma parameter has been renamed to scale, and the code has
       been updated so that changing it will change the sampled
       values. The clip parameter has been added, and the return value
       contains an extra column indicating whether a parameter in the
       row was clipped.

    .. versionchanged:: 4.16.0
       The rng parameter was added.

    Parameters
    ----------
    fit :
       The fit results.
    num : int, optional
       The number of samples to use (default is `1`).
    dof : optional
       The number of degrees of freedom to use (the default
       is to use the number from the current fit).
    numcores : optional
       The number of CPU cores to use. The default is to use all
       the cores on the machine.
    rng : numpy.random.Generator, numpy.random.RandomState, or None, optional
       Determines how random numbers are created. If set to None then
       the routines from `numpy.random` are used, and so can be
       controlled by calling `numpy.random.seed`.
    clip : {'hard', 'soft', 'none'}, optional
       What clipping strategy should be applied to the sampled
       parameters. The default ('none') applies no clipping, 'hard'
       uses the hard parameter limits, and 'soft' the soft limits.

    Returns
    -------
    samples :
       A NumPy array table with the first column representing the
       statistic, the later columns the parameters used, and the last
       column indicating whether any parameter in the row was clipped.

    See Also
    --------
    normal_sample : Sample from the normal distribution.
    uniform_sample : Sample from a uniform distribution.

    """
    sampler = StudentTSampleFromScaleMatrix()
    return sampler.get_sample(fit, num=num, dof=dof,
                              numcores=numcores, rng=rng, clip=clip)
