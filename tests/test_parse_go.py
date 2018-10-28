# -*- coding: utf-8 -*-

"""Tests for the InterPro-GO file parser."""

import unittest

from bio2bel_interpro.parser.interpro_to_go import get_interpro_go_mappings
from tests.constants import TEST_INTERPRO_GO_MAPPINGS_PATH


class TestTreeParser(unittest.TestCase):
    """Methods to test that the parser for the InterPro tree works properly."""

    @classmethod
    def setUpClass(cls):
        """Set up this class with GO mappings."""
        cls.interpro_go_mapping = get_interpro_go_mappings(path=TEST_INTERPRO_GO_MAPPINGS_PATH)

    def test_length(self):
        """Test the number of mappings."""
        self.assertEqual(3, len(self.interpro_go_mapping))
