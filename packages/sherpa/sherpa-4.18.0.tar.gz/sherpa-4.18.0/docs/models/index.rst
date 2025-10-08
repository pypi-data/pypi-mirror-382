************************
Creating model instances
************************

The :mod:`sherpa.models` and :mod:`sherpa.astro.models` namespaces
provides a collection of one- and two-dimensional models. There
are also more specialised models, such as those in
:mod:`sherpa.astro.optical`, :mod:`sherpa.astro.xspec`,
:mod:`sherpa.instrument`, and :mod:`sherpa.astro.instrument`.

The following modules are assumed to have been imported for this
section::

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from sherpa.models import basic

Creating a model instance
=========================

Models must be created before there parameter values can
be set. In this case a one-dimensional gaussian using the
:py:class:`~sherpa.models.basic.Gauss1D` class::

    >>> g = basic.Gauss1D()
    >>> print(g)
    gauss1d
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       gauss1d.fwhm thawed           10  1.17549e-38  3.40282e+38
       gauss1d.pos  thawed            0 -3.40282e+38  3.40282e+38
       gauss1d.ampl thawed            1 -3.40282e+38  3.40282e+38

A description of the model is provided by ``help(g)``.

The parameter values have a current value, a valid range
(as given by the minimum and maximum columns in the table above),
and a units field. The units field is a string, describing the
expected units for the parameter; there is currently *no support* for
using `astropy.units
<https://docs.astropy.org/en/stable/units/index.html>`_ to set a
parameter value.  The "Type" column refers to whether the parameter is
fixed, (``frozen``) or can be varied during a fit (``thawed``),
as described below, in the :ref:`params-freeze` section.

Models can be given a name, to help distinguish multiple versions
of the same model type. The default value is the lower-case version
of the class name.

::

    >>> g.name
    'gauss1d'
    >>> h = basic.Gauss1D('other')
    >>> print(h)
    other
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       other.fwhm   thawed           10  1.17549e-38  3.40282e+38
       other.pos    thawed            0 -3.40282e+38  3.40282e+38
       other.ampl   thawed            1 -3.40282e+38  3.40282e+38
    >>> h.name
    'other'

The model classes are expected to derive from the
:py:class:`~sherpa.models.model.ArithmeticModel` class, although
more-complicated cases, such as :doc:`convolution models
<../evaluation/convolution>`, may extend other classes.

.. _model-combine:

Combining models
================

Models can be combined to serve as building blocks for more complex
models; the same building block can be used multiple times.
The easiest way to combine models is by using the standard Python
numerical operators. For instance, a one-dimensional gaussian
plus a flat background - using the
:py:class:`~sherpa.models.basic.Const1D` class - would be
represented by the following model::

    >>> src1 = basic.Gauss1D('src1')
    >>> back = basic.Const1D('back')
    >>> mdl1 = src1 + back
    >>> print(mdl1)
    src1 + back
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       src1.fwhm    thawed           10  1.17549e-38  3.40282e+38
       src1.pos     thawed            0 -3.40282e+38  3.40282e+38
       src1.ampl    thawed            1 -3.40282e+38  3.40282e+38
       back.c0      thawed            1 -3.40282e+38  3.40282e+38

Now consider fitting a second dataset where it is known that the background
is two times higher than the first::

    >>> src2 = basic.Gauss1D('src2')
    >>> mdl2 = src2 + 2 * back
    >>> print(mdl2)
    src2 + 2.0 * back
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       src2.fwhm    thawed           10  1.17549e-38  3.40282e+38
       src2.pos     thawed            0 -3.40282e+38  3.40282e+38
       src2.ampl    thawed            1 -3.40282e+38  3.40282e+38
       back.c0      thawed            1 -3.40282e+38  3.40282e+38

The two models can then be fit separately or simultaneously. In this
example the two source models (the Gaussian component) were completely
separate, but they could have been identical - in which case
``mdl2 = src1 + 2 * back`` would have been used instead - or
:ref:`parameter linking <params-link>` could be used to constrain the
models. An example of the use of linking would be to force the two
FWHM (full-width half-maximum)
parameters to be the same but to let the position and amplitude
values vary independently.

More information including more complex, but more powerful ways to combine models
is available in the
:doc:`combining models <../evaluation/combine>`
and
:doc:`convolution <../evaluation/convolution>`
documentation.

Changing a parameter
====================

The parameters of a model - those numeric variables that control the
shape of the model, and that can be varied during a fit -
can be accessed as attributes, both to read or change
the current settings. The
:py:attr:`~sherpa.models.parameter.Parameter.val` attribute
contains the current value::

    >>> print(h.fwhm)
    val         = 10.0
    min         = 1.17549435082e-38
    max         = 3.40282346639e+38
    units       =
    frozen      = False
    link        = None
    default_val = 10.0
    default_min = 1.17549435082e-38
    default_max = 3.40282346639e+38
    >>> print(h.fwhm.val)
    10.0
    >>> print(h.fwhm.min)
    1.1754943508222875e-38
    >>> h.fwhm.val = 15
    >>> print(h.fwhm)
    val         = 15.0
    min         = 1.17549435082e-38
    max         = 3.40282346639e+38
    units       =
    frozen      = False
    link        = None
    default_val = 15.0
    default_min = 1.17549435082e-38
    default_max = 3.40282346639e+38

Assigning a value to a parameter directly (i.e. without using the
``val`` attribute) also works::

    >>> h.fwhm = 12
    >>> print(h.fwhm)
    val         = 12.0
    min         = 1.17549435082e-38
    max         = 3.40282346639e+38
    units       =
    frozen      = False
    link        = None
    default_val = 12.0
    default_min = 1.17549435082e-38
    default_max = 3.40282346639e+38

.. _params-limits:

The soft and hard limits of a parameter
=======================================

Each parameter has two sets of limits, which are referred to as
"soft" and "hard". The soft limits are shown when the model
is displayed, and refer to the
:py:attr:`~sherpa.models.parameter.Parameter.min`
and
:py:attr:`~sherpa.models.parameter.Parameter.max`
attributes for the parameter, whereas the hard limits are
given by the
:py:attr:`~sherpa.models.parameter.Parameter.hard_min`
and
:py:attr:`~sherpa.models.parameter.Parameter.hard_max`
(which are not displayed, and can not be changed).

    >>> print(h)
    other
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       other.fwhm   thawed           12  1.17549e-38  3.40282e+38
       other.pos    thawed            0 -3.40282e+38  3.40282e+38
       other.ampl   thawed            1 -3.40282e+38  3.40282e+38
    >>> print(h.fwhm)
    val         = 12.0
    min         = 1.17549435082e-38
    max         = 3.40282346639e+38
    units       =
    frozen      = False
    link        = None
    default_val = 12.0
    default_min = 1.17549435082e-38
    default_max = 3.40282346639e+38

These limits act to bound the acceptable parameter range; this
is often because certain values are physically impossible, such
as having a negative value for the full-width-half-maxium value
of a Gaussian, but can also be used to ensure that the fit is
restricted to a meaningful part of the search space. The hard
limits are set by the model class, and represent the full
valid range of the parameter, whereas the soft limits can be
changed by the user, although they often default to the same
values as the hard limits.

Setting a parameter to a value outside its soft limits will
raise a :py:exc:`~sherpa.utils.err.ParameterErr` exception.

During a fit the parameter values are bound by the soft limits,
and a screen message will be displayed if an attempt to move
outside this range was made. During error analysis the parameter
values are allowed outside the soft limits, as long as they remain
inside the hard limits. This may help with determining uncertainties
for parameters that are close to the soft limits.

.. _params-guess:

Guessing a parameter's value from the data
==========================================

Sherpa models have a
:py:meth:`~sherpa.models.model.Model.guess`
method which is used to seed the parameters (or
parameter) with values and
:ref:`soft-limit ranges <params-limits>`
which match the data.
The idea is to move the parameters to values appropriate
for the data, which can avoid un-needed computation by
the optimiser.

The existing ``guess`` routines are very basic - such as
picking the index of the largest value in the data for
the peak location - and do not always account for the
full complexity of the model expression, so care should
be taken when using this functionality.

The arguments depend on the model type, since both the
independent and dependent axes may be used, but the
:py:meth:`~sherpa.data.Data.to_guess` method of
a data object will return the correct data (assuming the
dimensionality and type match)::

    >>> mdl.guess(*data.to_guess())  # doctest: +SKIP

Note that the soft limits can be changed, as in this example
which ensures the position of the gaussian falls within the
grid of points (since this is the common situation; if the source
is meant to lie outside the data range then the limits will
need to be increased manually)::

    >>> from sherpa.data import Data2D
    >>> from sherpa.models import basic
    >>> yg, xg = np.mgrid[4000:4050:10, 3000:3070:10]
    >>> r2 = (xg - 3024.2)**2 + (yg - 4011.7)**2
    >>> zg = 2400 * np.exp(-r2 / 1978.2)
    >>> d2d = Data2D('example', xg.flatten(), yg.flatten(), zg.flatten(),
    ...              shape=zg.shape)
    >>> mdl = basic.Gauss2D('mdl')
    >>> print(mdl)
    mdl
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       mdl.fwhm     thawed           10  1.17549e-38  3.40282e+38
       mdl.xpos     thawed            0 -3.40282e+38  3.40282e+38
       mdl.ypos     thawed            0 -3.40282e+38  3.40282e+38
       mdl.ellip    frozen            0            0        0.999
       mdl.theta    frozen            0     -6.28319      6.28319    radians
       mdl.ampl     thawed            1 -3.40282e+38  3.40282e+38
    >>> mdl.guess(*d2d.to_guess())
    >>> print(mdl)
    mdl
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       mdl.fwhm     thawed           60         0.06        60000
       mdl.xpos     thawed         3020         3000         3060
       mdl.ypos     thawed         4010         4000         4040
       mdl.ellip    frozen            0            0        0.999
       mdl.theta    frozen            0     -6.28319      6.28319    radians
       mdl.ampl     thawed      2375.22      2.37522  2.37522e+06

.. _params-freeze:

Freezing and Thawing parameters
===============================

Not all model parameters should be varied during a fit: perhaps
the data quality is not sufficient to constrain all the parameters,
it is already known, the parameter is highly correlated with
another, or perhaps the parameter value controls a behavior of the
model that should not vary during a fit (such as the interpolation
scheme to use). The :py:attr:`~sherpa.models.parameter.Parameter.frozen`
attribute controls whether a fit
should vary that parameter or not; it can be changed directly,
as shown below::

    >>> h.fwhm.frozen
    False
    >>> h.fwhm.frozen = True

or via the :py:meth:`~sherpa.models.parameter.Parameter.freeze`
and :py:meth:`~sherpa.models.parameter.Parameter.thaw`
methods for the parameter.

::

    >>> h.fwhm.thaw()
    >>> h.fwhm.frozen
    False

There are times when a model parameter should *never* be varied
during a fit. In this case the
:py:attr:`~sherpa.models.parameter.Parameter.alwaysfrozen`
attribute will be set to ``True`` (this particular
parameter is read-only).

.. _params-link:

Linking parameters
==================

There are times when it is useful for one parameter to be
related to another: this can be equality, such as saying that
the width of two model components are the same, or a functional
form, such as saying that the position of one component is a
certain distance away from another component. This concept
is referred to as linking parameter values. The second case
includes the first - where the functional relationship is equality -
but it is treated separately here as it is a common operation.
Linking parameters also reduces the number of free parameters in a fit.

The following examples use the same two model components::

    >>> g1 = basic.Gauss1D('g1')
    >>> g2 = basic.Gauss1D('g2')

Linking parameter values requires referring to the parameter, rather
than via the :py:attr:`~sherpa.models.parameter.Parameter.val` attribute.
The :py:attr:`~sherpa.models.parameter.Parameter.link` attribute
is set to the link value (and is ``None`` for parameters that are
not linked).

Equality
--------

After the following, the two gaussian components have the same
width::

    >>> print(g2.fwhm.val)
    10.0
    >>> g2.fwhm = g1.fwhm
    >>> g1.fwhm = 1024
    >>> print(g2.fwhm.val)
    1024.0
    >>> g1.fwhm.link is None
    True
    >>> g2.fwhm.link
    <Parameter 'fwhm' of model 'g1'>

When displaying the model, the value and link expression are included::

    >>> print(g2)
    g2
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       g2.fwhm      linked         1024            expr: g1.fwhm
       g2.pos       thawed            0 -3.40282e+38  3.40282e+38
       g2.ampl      thawed            1 -3.40282e+38  3.40282e+38

Functional relationship
-----------------------

The link can accept anything that evaluates to a value,
such as adding a constant.

::

    >>> g2.pos = g1.pos + 8234
    >>> g1.pos = 1200
    >>> print(g2.pos.val)
    9434.0

The :py:class:`~sherpa.models.parameter.CompositeParameter` class
controls how parameters are combined. In this case the result
is a :py:class:`~sherpa.models.parameter.BinaryOpParameter` object.

Including another parameter
---------------------------

It is possible to include other parameters in a link expression,
which can lead to further constraints on the fit. For example,
we can fit using the sigma value instead of the FWHM of a
gaussian::

    >>> sigma = basic.Scale1D('sigma')
    >>> sigma.c0 = 10
    >>> print(sigma)
    sigma
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       sigma.c0     thawed           10 -3.40282e+38  3.40282e+38
    >>> g1.fwhm = 2 * np.sqrt(2 * np.log(2)) * sigma.c0

which creates

::

    >>> print(g1)
    g1
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       g1.fwhm      linked      23.5482 expr: 2.3548200450309493 * sigma.c0
       g1.pos       thawed         1200 -3.40282e+38  3.40282e+38
       g1.ampl      thawed            1 -3.40282e+38  3.40282e+38

and, because ``g2.fwhm`` is still linked to ``g1.fwhm``

::

    >>> print(g2)
    g2
       Param        Type          Value          Min          Max      Units
       -----        ----          -----          ---          ---      -----
       g2.fwhm      linked      23.5482            expr: g1.fwhm
       g2.pos       linked         9434      expr: g1.pos + 8234
       g2.ampl      thawed            1 -3.40282e+38  3.40282e+38

.. note::

   Prior to Sherpa 4.16.1 you had to explicitly include any linked
   parameters into the model expression - e.g. by saying::

       >>> mdl = g1 + g2 * 0 * sigma

   where the ``sigma`` component is multiplied by zero to ensure it
   does not directly add to the model. This step is **no longer**
   needed, so you can just fit the model directly.

       >>> mdl = g1 + g2

Complex functional relationships
--------------------------------

Any `numpy universal function ("ufunc") <https://numpy.org/doc/stable/reference/ufuncs.html#ufuncs>`_
can be used in the linking expression, for example::

    >>> import numpy as np
    >>> g2.ampl = np.cos(g1.ampl)

This includes many commonly used mathematical and trigonometric functions
such as log, exp, sin, cos, which allows building quite complex parameter
linkage. Only the numpy versions work here, **not** the functions from the
built-in ``math`` module, so use `numpy.exp` instead of `math.exp`.
Many more complex functions are available in
`scipy.special <https://docs.scipy.org/doc/scipy/reference/special.html>`_;
any arbitrary Python function can be turned into a ufunc with
`numpy.frompyfunc <https://numpy.org/doc/stable/reference/generated/numpy.frompyfunc.html#numpy.frompyfunc>`_
and the interface is also available for
`C extensions <https://numpy.org/doc/stable/user/c-info.ufunc-tutorial.html#creating-a-new-universal-function>`_.
However, if such complex expressions are required to link model parameters
together, it might be better to write a
:ref:`dedicated user model <usermodel>` that describes the data with the
appropriate parameters in the first place.

Not every possible link function makes sense
--------------------------------------------

With this flexibility, it is possible to define links that make no sense,
for example taking the logical not of a parameter that represents a mass or
turning values of parameters into arrays (Sherpa optimisers can only deal
with scalar parameters.) In practice, such mistakes
are easy to spot when displaying a model; because Sherpa is meant to be
a general and flexible modelling application that works with (almost)
arbitrary user-defined models, the code puts as few restrictions
as possible on the functions used for linking parameters.

.. _parameter_reset:

Resetting parameter values
==========================

.. todo::

   Needs work, including discussing the
   :py:attr:`~sherpa.models.parameter.Parameter.default_val` attribute?

The
:py:meth:`~sherpa.models.parameter.Parameter.reset`
method of a parameter will change the parameter settings (which
includes the status of the thawed flag and allowed ranges,
as well as the value) to the values they had the last time
the parameter was *explicitly* set. That is, it does not restore
the initial values used when the model was created, but the
last values the user set.

The model class has its own
:py:meth:`~sherpa.models.model.Model.reset`
method which calls reset on the thawed parameters. This can be used to
:ref:`change the starting point of a fit <change_fit_starting_point>`
to see how robust the optimiser is by:

* explicitly setting parameter values (or using the default values)
* fit the data
* call reset
* change one or more parameters
* refit


Inspecting models and parameters
================================

.. note::

   Access to model parameters has been extended in 4.16.1 by
   adding the ``lpars`` attribute and the ``get_thawed_pars`` method.

Models, whether a single component or composite, contain a
:py:attr:`~sherpa.models.model.Model.pars` attribute which is a tuple
of all the parameters for that model, and the
:py:attr:`~sherpa.models.model.Model.lpars` attribute, which contains
any linked parameters in the model which are not a direct member of
the source expression. These two can be used to programmatically query
or change the parameter values.

The :py:attr:`~sherpa.models.model.Model.get_thawed_pars` routine
provides access to all the thawed parameters of a model expression,
including any linked parameters.  There are a number of attributes
that provide access to this data, such as:
:py:attr:`~sherpa.models.model.Model.thawedpars`, which gives the
current value; and the
:py:attr:`~sherpa.models.model.Model.thawedparmins` and
:py:attr:`~sherpa.models.model.Model.thawedparmaxes`, which give the
soft limits of these parameters.

::

    >>> g1 = basic.Gauss1D('g1')
    >>> g2 = basic.Gauss1D('g2')
    >>> g2.fwhm = g1.fwhm
    >>> sep = basic.Scale1D('sep')
    >>> g2.pos = 10 + sep.c0
    >>> sep.c0.min = 0
    >>> mdl = g1 + g2
    >>> g1.pars
    (<Parameter 'fwhm' of model 'g1'>, <Parameter 'pos' of model 'g1'>, <Parameter 'ampl' of model 'g1'>)
    >>> g1.lpars
    ()
    >>> g2.pars
    (<Parameter 'fwhm' of model 'g2'>, <Parameter 'pos' of model 'g2'>, <Parameter 'ampl' of model 'g2'>)
    >>> g2.lpars
    (<Parameter 'fwhm' of model 'g1'>, <Parameter 'c0' of model 'sep'>)
    >>> for idx, par in enumerate(mdl.pars, 1):
    ...     print(idx, par.fullname)
    1 g1.fwhm
    2 g1.pos
    3 g1.ampl
    4 g2.fwhm
    5 g2.pos
    6 g2.ampl
    >>> mdl.lpars
    (<Parameter 'c0' of model 'sep'>,)
    >>> for idx, par in enumerate(mdl.get_thawed_pars(), 1):
    ...     print(idx, par.fullname)
    1 g1.fwhm
    2 g1.pos
    3 g1.ampl
    4 g2.ampl
    5 sep.c0

We can think of a complex model as a tree of components, where the leaves are
the individual components and nodes are composite models (e.g.
a `sherpa.models.model.BinaryOpModel` that adds to model components together).
There are several ways to access the components of a model, by model name
(the list will have one entry if the model name is unique, or more if it
appears more than once)::

    >>> mdl.get_components_by_name('g2')
    [<Gauss1D model instance 'g2'>]

or by type::

    >>> mdl.get_components_by_class(basic.Gauss1D)
    [<Gauss1D model instance 'g1'>, <Gauss1D model instance 'g2'>]

Alternatively, you can obtain a list of all components with::

    >>> mdl.get_parts(include_composites=False)
    [<Gauss1D model instance 'g1'>, <Gauss1D model instance 'g2'>]

where the ``include_composites`` argument controls whether
composite models are included in the list or only the leaves.
As a convenience, for example for working interactively in a notebook,
the same functionality is available as attribute access,
which can shorten the notation. Here, if the result is a single model,
it will be returned directly, while a list of models is returned if more
than one component matches::

    >>> mdl['g2']
    <Gauss1D model instance 'g2'>
    >>> mdl[basic.Gauss1D]
    [<Gauss1D model instance 'g1'>, <Gauss1D model instance 'g2'>]

This allows a very compressed syntax to change the parameters of a single
component, for example ``mdl['g2'].ampl = 5``.

Models can also be iterated over to access the individual components -
but note that this may include composite models.

    >>> for cpt in iter(mdl):
    ...     print(cpt.name, type(cpt))
    g1 + g2 <class 'sherpa.models.model.BinaryOpModel'>
    g1 <class 'sherpa.models.basic.Gauss1D'>
    g2 <class 'sherpa.models.basic.Gauss1D'>
    >>> for cpt in iter(g1 + 2 * g2):
    ...     print(cpt.name, type(cpt))
    g1 + 2.0 * g2 <class 'sherpa.models.model.BinaryOpModel'>
    g1 <class 'sherpa.models.basic.Gauss1D'>
    2.0 * g2 <class 'sherpa.models.model.BinaryOpModel'>
    2.0 <class 'sherpa.models.model.ArithmeticConstantModel'>
    g2 <class 'sherpa.models.basic.Gauss1D'>

When analysing composite models, note that the
:py:attr:`~sherpa.models.model.Model.pars` attribute will contain
repeated copies of model parameters if the model appears multiple
times. The repeat values are actually links to the original version::

    >>> scale = basic.Scale1D("scale")
    >>> b1 = basic.Box1D("box1")
    >>> b2 = basic.Box1D("box2")
    >>> mdl = scale * b1 + scale * b2
    >>> scale.c0 = 5
    >>> b1.xhi = 10
    >>> b2.xlow = -1
    >>> for idx, par in enumerate(mdl.pars, 1):
    ...     print(f"{idx} {par.modelname:5s} {par.name:6s} {par.val}  {par.link is not None}")
    ...
    1 scale c0       5.0  False
    2 box1  xlow     0.0  False
    3 box1  xhi     10.0  False
    4 box1  ampl     1.0  False
    5 scale c0       5.0  True
    6 box2  xlow    -1.0  False
    7 box2  xhi      1.0  False
    8 box2  ampl     1.0  False
    >>> mdl.pars[4] == mdl.pars[0]
    False
