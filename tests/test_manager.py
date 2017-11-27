# -*- coding: utf-8 -*-

import logging
import os
import tempfile
import unittest

from bio2bel_interpro.manager import Manager

log = logging.getLogger(__name__)


class TestManager(unittest.TestCase):
    def setUp(self):
        """Creates a manager with a temporary database and imports the database."""
        self.fd, self.path = tempfile.mkstemp()
        self.connection = 'sqlite:///' + self.path
        log.info('Test generated connection string %s', self.connection)

        self.manager = Manager(connection=self.connection)

        self.manager.populate()

    def tearDown(self):
        """Closes the connection in the manager and deletes the temporary database"""
        self.manager.session.close()
        os.close(self.fd)
        os.remove(self.path)

    def test1(self):
        """basic test for """
        result = self.manager.get_family_by_name('Ubiquitin/SUMO-activating enzyme E1')
        self.assertIsNotNone(result)

        child = self.manager.get_family_by_name('Ubiquitin-activating enzyme E1')
        self.assertIsNotNone(child)

        self.assertEqual(result.interpro_id, 'IPR000011')
        self.assertEqual(len(result.children), 1)
        self.assertIn(child, result.children)


if __name__ == '__main__':
    unittest.main()
