interpro to BEL
===============

Converts interpro protein families to BEL namespace

Installation
------------
This code can be installed with :code:`pip3 install git+https://github.com/bio2bel/interpro.git`


Creating a Local Copy of the Namespace
--------------------------------------
A BEL namespace can be generated with :code:`python3 -m bio2bel_interpro write -o ~/Downloads/interpro.belns`

Deploying to Artifactory
------------------------
A BEL namespace can be generated and automatically deployed to Artifactory with
:code:`python3 -m bio2bel_interpro arty`. However, this is taken care of with Travis CI at
https://travis-ci.org/bio2bel/interpro