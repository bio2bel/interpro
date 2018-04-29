# -*- coding: utf-8 -*-

"""Tests for the InterPro-GO file parser."""

import unittest

from bio2bel_interpro.parser.interpro_to_go import get_go_mappings
from tests.constants import test_go_path


class TestTreeParser(unittest.TestCase):
    """Methods to test that the parser for the InterPro tree works properly"""

    @classmethod
    def setUpClass(cls):
        cls.df = get_go_mappings(path=test_go_path)
