# -*- coding: utf-8 -*-

import logging
import os
import tempfile
import unittest

from bio2bel_interpro.manager import Manager

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
test_tree_path = os.path.join(dir_path, 'test.txt')


class TemporaryFileMixin(unittest.TestCase):
    def setUp(self):
        """Creates a temporary file for the duration of the test"""
        self.fd, self.path = tempfile.mkstemp()
        self.connection = 'sqlite:///' + self.path
        log.info('Test generated connection: %s', self.connection)

    def tearDown(self):
        """Removes the temporary file"""
        os.close(self.fd)
        os.remove(self.path)


class TemporaryManagerMixin(TemporaryFileMixin):
    def setUp(self):
        """Creates a manager with a temporary database and imports the database."""
        super(TemporaryFileMixin, self).setUp()

        self.manager = Manager(connection=self.connection)
        self.manager.populate(
            family_entries_url=None,
            tree_url=test_tree_path
        )

    def tearDown(self):
        """Closes the connection in the manager and deletes the temporary database"""
        self.manager.session.close()
        super(TemporaryFileMixin, self).tearDown()
