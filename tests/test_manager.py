import unittest

from bio2bel_interpro.database import database, models


class TestManager(unittest.TestCase):
    def setUp(self):
        self.manager = database.Manager()
        self.manager.write_db()

    def test1(self):
        """basic test for """
        result = self.manager.session.query(models.Interpro).filter(
            models.Interpro.name == 'Ubiquitin/SUMO-activating enzyme E1').one()
        child = self.manager.session.query(models.Interpro).filter(
            models.Interpro.name == 'Ubiquitin-activating enzyme E1').one()
        self.assertEqual(result.accession, 'IPR000011')
        self.assertEqual(len(result.children), 1)
        self.assertIn(child, result.children)

if __name__ == '__main__':
    unittest.main()