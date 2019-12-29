import unittest
import electionstats

class ElectionStatsTests(unittest.TestCase):

    def test_presidential(self):
        p00_16 = electionstats.query_elections(2000,
                                               2016,
                                               "President",
                                               "General")
        self.assertEqual(len(p00_16), 5)
        self.assertEqual(p00_16["year"].min(), 2000)
        self.assertEqual(p00_16["year"].max(), 2016)
        # Add more here

    def test_state_rep(self):
        sr2016 = electionstats.query_elections(2016, 2016, "State Rep", "General")
        self.assertEqual(len(sr2016), 160)
        # Add more here

if __name__ == "__main__":
    unittest.main()
