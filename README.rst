Bio2BEL InterPro |build| |coverage| |docs|
==========================================
Converts InterPro to BEL

Installation
------------
This code can be installed with :code:`pip3 install git+https://github.com/bio2bel/interpro.git`

Creating a Local Copy of the Namespace
--------------------------------------
A BEL namespace can be generated with :code:`python3 -m bio2bel_interpro write -o ~/Downloads/interpro.belns`

Deploying to Artifactory
------------------------
A BEL namespace can be generated and automatically deployed to Artifactory with
:code:`python3 -m bio2bel_interpro deploy`. However, this is taken care of with Travis CI at
https://travis-ci.org/bio2bel/interpro

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

.. |docs| image:: http://readthedocs.org/projects/bio2bel-interpro/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/interpro/en/latest/?badge=latest
    :alt: Documentation Status
