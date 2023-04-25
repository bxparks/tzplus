import unittest
from check_data import Entry
from check_data import has_cycle


class TestHashCycle(unittest.TestCase):
    """Unit test for the has_cycle() function for links."""

    def test_zones(self) -> None:
        zones = {
            'a': Entry(None, 'Zone'),
            'b': Entry(None, 'Zone'),
        }
        self.assertFalse(has_cycle('a', zones))
        self.assertFalse(has_cycle('b', zones))

    def test_links_no_cycle(self) -> None:
        links = {
            'a': Entry('aa', 'Link'),
            'b': Entry('a', 'Link'),
            'c': Entry('a', 'Link'),
        }
        self.assertFalse(has_cycle('a', links))
        self.assertFalse(has_cycle('b', links))
        self.assertFalse(has_cycle('c', links))

    def test_links_cycle_1(self) -> None:
        # 1-step cycle
        links = {
            'a': Entry('a', 'Link'),
        }
        self.assertTrue(has_cycle('a', links))

    def test_links_cycle_2(self) -> None:
        # 2-step cycle
        links = {
            'a': Entry('b', 'Link'),
            'b': Entry('a', 'Link'),
        }

        self.assertTrue(has_cycle('a', links))
        self.assertTrue(has_cycle('b', links))

    def test_links_cycle_3(self) -> None:
        # 3-step cycle
        links = {
            'a': Entry('b', 'Link'),
            'b': Entry('c', 'Link'),
            'c': Entry('a', 'Link'),
        }

        self.assertTrue(has_cycle('a', links))
        self.assertTrue(has_cycle('b', links))
        self.assertTrue(has_cycle('c', links))
