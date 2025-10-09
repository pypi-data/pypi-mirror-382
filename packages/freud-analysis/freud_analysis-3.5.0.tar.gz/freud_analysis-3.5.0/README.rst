=====
freud
=====

|Citing freud|
|PyPI|
|conda-forge|
|ReadTheDocs|
|Binder|
|GitHub-Stars|

.. |Citing freud| image:: https://img.shields.io/badge/cite-freud-informational.svg
   :target: https://freud.readthedocs.io/en/stable/reference/citing.html
.. |PyPI| image:: https://img.shields.io/pypi/v/freud-analysis.svg
   :target: https://pypi.org/project/freud-analysis/
.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/freud.svg
   :target: https://anaconda.org/conda-forge/freud
.. |ReadTheDocs| image:: https://readthedocs.org/projects/freud/badge/?version=latest
   :target: https://freud.readthedocs.io/en/latest/?badge=latest
.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/glotzerlab/freud-examples/master?filepath=index.ipynb
.. |GitHub-Stars| image:: https://img.shields.io/github/stars/glotzerlab/freud.svg?style=social
   :target: https://github.com/glotzerlab/freud

Overview
========

The **freud** Python library provides a simple, flexible, powerful set of tools
for analyzing trajectories obtained from molecular dynamics or Monte Carlo
simulations. High performance, parallelized C++ is used to compute standard
tools such as radial distribution functions, correlation functions, order
parameters, and clusters, as well as original analysis methods including
potentials of mean force and torque (PMFTs) and local environment matching. The
**freud** library supports
`many input formats <https://freud.readthedocs.io/en/stable/topics/datainputs.html>`__
and outputs `NumPy arrays <https://numpy.org/>`__, enabling integration
with the scientific Python ecosystem for many typical materials science
workflows.

Resources
=========

- `Reference Documentation <https://freud.readthedocs.io/>`__: Examples, tutorials, topic guides, and package Python APIs.
- `Installation Guide <https://freud.readthedocs.io/en/stable/gettingstarted/installation.html>`__: Instructions for installing and compiling **freud**.
- `freud discussion board <https://github.com/glotzerlab/freud/discussions/>`__: Ask the **freud** user community for help.
- `GitHub repository <https://github.com/glotzerlab/freud>`__: Download the **freud** source code.
- `Issue tracker <https://github.com/glotzerlab/freud/issues>`__: Report issues or request features.

Related Tools
=============

- `HOOMD-blue <https://hoomd-blue.readthedocs.io/>`__: Perform MD / MC simulations that can be analyzed with **freud**.
- `signac <https://signac.readthedocs.io/>`__: Manage your workflow with **signac**.

Citation
========

When using **freud** to process data for publication, please `use this citation
<https://freud.readthedocs.io/en/stable/reference/citing.html>`__.


Installation
============

**freud** is available on conda-forge_ for the *linux-64*, *linux-aarch64*, *linux-ppc64le*,
*osx-64*, *osx-arm64* and *win-64* architectures. Install with:

.. code:: bash

   mamba install freud

**freud** is also available on PyPI_:

.. code:: bash

   python3 -m pip install freud-analysis

.. _conda-forge: https://conda-forge.org/
.. _PyPI: https://pypi.org/

If you need more detailed information or wish to install **freud** from source, please refer to the
`Installation Guide <https://freud.readthedocs.io/en/stable/gettingstarted/installation.html>`__ to
compile **freud** from source.


Examples
========

The **freud** library is called using Python scripts. Many core features are
`demonstrated in the freud documentation
<https://freud.readthedocs.io/en/stable/examples.html>`_. The examples come in
the form of Jupyter notebooks, which can also be downloaded from the `freud
examples repository <https://github.com/glotzerlab/freud-examples>`_ or
`launched interactively on Binder
<https://mybinder.org/v2/gh/glotzerlab/freud-examples/master?filepath=index.ipynb>`_.
Below is a sample script that computes the radial distribution function for a
simulation run with `HOOMD-blue <https://hoomd-blue.readthedocs.io/>`__ and
saved into a `GSD file <https://gsd.readthedocs.io/>`_.

.. code:: python

   import freud
   import gsd.hoomd

   # Create a freud compute object (RDF is the canonical example)
   rdf = freud.density.RDF(bins=50, r_max=5)

   # Load a GSD trajectory (see docs for other formats)
   traj = gsd.hoomd.open('trajectory.gsd', 'rb')
   for frame in traj:
       rdf.compute(system=frame, reset=False)

   # Get bin centers, RDF data from attributes
   r = rdf.bin_centers
   y = rdf.rdf


Support and Contribution
========================

Please visit our repository on `GitHub <https://github.com/glotzerlab/freud>`__ for the library source code.
Any issues or bugs may be reported at our `issue tracker <https://github.com/glotzerlab/freud/issues>`__, while questions and discussion can be directed to our `discussion board <https://github.com/glotzerlab/freud/discussions/>`__.
All contributions to **freud** are welcomed via pull requests!
