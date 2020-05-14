import unittest

from Place import Place
from Stage import Stage
from database import Database


class DatabaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.db = Database()
        self.db.reset_user(1)
        self.db.reset_user(2)

    def test_adding(self):
        self.assertFalse(self.db.has_user(1))
        self.db.set_user_stage(1, Stage.START)
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.assertTrue(self.db.has_user(1))

    def test_places(self):
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.db.add_place(1, Place("Very Good restaurant", 62.12, 66.14))
        places = self.db.get_places(1)
        self.assertIn(Place("Good restaurant", 65.13, 66.14), places)
        self.assertIn(Place("Very Good restaurant", 62.12, 66.14), places)
        self.assertEqual(self.db.get_place_by_name(1, "Good restaurant"),
                         Place("Good restaurant", 65.13, 66.14))

    def test_removing_user(self):
        self.db.set_user_stage(1, Stage.START)
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.db.add_place(1, Place("Very Good restaurant", 62.12, 66.14))
        self.assertTrue(self.db.has_user(1))
        self.db.reset_user(1)
        self.assertFalse(self.db.has_user(1))

    def test_removing_place(self):
        self.db.add_place(1, Place("Good restaurant", 65.13, 66.14))
        self.db.add_place(1, Place("Very Good restaurant", 62.12, 66.14))
        self.db.add_place(2, Place("Very Good restaurant", 62.12, 66.14))
        self.db.remove_place(1, Place("Very Good restaurant", 62.12, 66.14))
        places = self.db.get_places(1)
        self.assertIn(Place("Good restaurant", 65.13, 66.14), places)
        self.assertNotIn(Place("Very Good restaurant", 62.12, 66.14), places)
        self.assertIn(Place("Very Good restaurant", 62.12, 66.14), self.db.get_places(2))

    def test_staging(self):
        self.db.set_user_stage(1, Stage.START)
        self.db.set_user_stage(2, Stage.START)
        self.assertEqual(self.db.get_user_stage(1), Stage.START)
        self.assertEqual(self.db.get_user_stage(1), Stage.START)
        self.db.set_user_stage(1, Stage.ADDING_PLACE_NAME)
        self.assertEqual(self.db.get_user_stage(1), Stage.ADDING_PLACE_NAME)
        self.assertEqual(self.db.get_user_stage(2), Stage.START)
        self.db.set_user_stage(1, Stage.ADDING_PLACE_LOCATION)
        self.assertEqual(self.db.get_user_stage(1), Stage.ADDING_PLACE_LOCATION)

    def test_staging_names(self):
        self.db.set_staged_place_name(1, "My favourite restaurant")
        self.assertEqual(self.db.get_staged_place_name(1), "My favourite restaurant")
        self.db.set_staged_place_name(2, "My very favourite restaurant")
        self.assertEqual(self.db.get_staged_place_name(2), "My very favourite restaurant")
        self.assertEqual(self.db.get_staged_place_name(1), "My favourite restaurant")
        self.db.clean_staged_place_name(1)
        self.assertEqual(self.db.get_staged_place_name(2), "My very favourite restaurant")
        self.assertIsNone(self.db.get_staged_place_name(1))


if __name__ == '__main__':
    unittest.main()
