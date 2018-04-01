# -*- coding: utf-8 -*-

"""This module builds a :mod:`Flask` application for interacting with the underlying database. When installing,
use the web extra like:

.. source-code:: sh

    pip install bio2bel_interpro[web]
"""

from bio2bel_interpro.manager import Manager

if __name__ == '__main__':
    manager = Manager()
    interpro_app = manager.get_flask_admin_app()
    interpro_app.run(debug=True, host='0.0.0.0', port=5000)
