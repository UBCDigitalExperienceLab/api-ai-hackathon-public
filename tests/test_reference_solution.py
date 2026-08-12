import unittest

from api_hackathon import reference_solution, workshop
from score import calculate


class HackathonKitTests(unittest.TestCase):
    def test_reference_solution_scores_100(self):
        score, levels = calculate(reference_solution)
        self.assertEqual(score, 100)
        self.assertEqual(
            levels,
            {
                "L1 Contract review": 20,
                "L2 Test design": 25,
                "L3 Safety + incident": 30,
                "L4 Migration": 25,
            },
        )

    def test_starter_has_room_to_improve(self):
        score, _ = calculate(workshop)
        self.assertLess(score, 100)
        self.assertGreater(score, 0)


if __name__ == "__main__":
    unittest.main()
