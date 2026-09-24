import unittest

from api_hackathon import workshop
from score import calculate


class HackathonKitTests(unittest.TestCase):
    def test_starter_has_room_to_improve(self):
        score, levels, _ = calculate(workshop)
        self.assertLess(score, 100)
        self.assertGreater(score, 0)
        self.assertEqual(levels["L3 Incident diagnosis"], 0)


if __name__ == "__main__":
    unittest.main()
