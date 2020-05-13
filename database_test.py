import unittest

from Place import Place
from database import Database


class DatabaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.db = Database()
        self.db.reset_user(1)

    def test_adding(self):
        self.assertFalse(self.db.has_user(1))
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.assertTrue(self.db.has_user(1))

    def test_places(self):
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.db.add_place(1, Place("Very Good restaurant", 62.12, 66.14))
        places = self.db.get_places(1)
        self.assertIn(Place("Good restaurant", 65.13, 66.14), places)
        self.assertIn(Place("Very Good restaurant", 62.12, 66.14), places)


if __name__ == '__main__':
    unittest.main()
