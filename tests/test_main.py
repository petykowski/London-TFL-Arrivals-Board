import unittest
import start

class TestStringMethods(unittest.TestCase):

    def test_due(self):
        self.assertEqual(start.format_time_component(30), 'due')

    def test_one_min(self):
        self.assertEqual(start.format_time_component(60), '1 min')

    def test_more_than_one_min(self):
        self.assertEqual(start.format_time_component(90), '2 mins')

if __name__ == '__main__':
    unittest.main()