Bio2BEL InterPro |build| |coverage| |documentation| |zenodo|
============================================================
Converts the InterPro protein families, domains, and other classes to ontological relations in BEL.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bio2bel_interpro`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_interpro>`_ with the
following code in your favorite terminal:

.. code-block:: sh

    $ python3 -m pip install bio2bel_interpro

or from the latest code on `GitHub <https://github.com/bio2bel/interpro>`_ with:

.. code-block:: sh

    $ python3 -m pip install git+https://github.com/bio2bel/interpro.git@master

Setup
-----
InterPro can be downloaded and populated from either the Python REPL or the automatically installed command line
utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import bio2bel_interpro
    >>> interpro_manager = bio2bel_interpro.Manager()
    >>> interpro_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    bio2bel_interpro populate

Programmatic Interface
----------------------
To enrich the proteins in a BEL Graph with their InterPro entries (families, domains, sites, etc.) , use:

>>> from bio2bel_interpro import enrich_proteins
>>> graph = ... # get a BEL graph
>>> enrich_proteins(graph)

.. |build| image:: https://travis-ci.org/bio2bel/interpro.svg?branch=master
    :target: https://travis-ci.org/bio2bel/interpro
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/interpro/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/interpro?branch=master
    :alt: Coverage Status

.. |documentation| image:: http://readthedocs.org/projects/bio2bel-interpro/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/interpro/en/latest/?badge=latest
    :alt: Documentation Status

.. |climate| image:: https://codeclimate.com/github/bio2bel/interpro/badges/gpa.svg
    :target: https://codeclimate.com/github/bio2bel/interpro
    :alt: Code Climate

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bio2bel_interpro.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bio2bel_interpro.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bio2bel_interpro.svg
    :alt: MIT License

.. |zenodo| image:: https://zenodo.org/badge/98345182.svg
    :target: https://zenodo.org/badge/latestdoi/98345182
    :alt: Zenodo DOI
