import unittest
import electionstats
import pandas as pd

class ElectionStatsTests(unittest.TestCase):

    def test_presidential(self):
        p00_16 = electionstats.query_elections(2000,
                                               2016,
                                               "President",
                                               "General")
        self.assertEqual(len(p00_16), 5)
        self.assertEqual(p00_16["year"].min(), 2000)
        self.assertEqual(p00_16["year"].max(), 2016)
        self.assertIsInstance(p00_16.sample().iloc[0]["date"], pd.Timestamp)
        # Add more here
        p16 = p00_16[p00_16["year"] == 2016].iloc[0]
        p16_pcts = electionstats.read_election(p16["election_id"])
        self.assertEqual(len(p16_pcts), 2174)
        p12 = p00_16[p00_16["year"] == 2012].iloc[0]
        p12_pcts = electionstats.read_election(p12["election_id"])
        self.assertEqual(len(p12_pcts), 2174)
        p08 = p00_16[p00_16["year"] == 2008].iloc[0]
        p08_pcts = electionstats.read_election(p08["election_id"])
        self.assertEqual(len(p08_pcts), 2172)

    def test_state_rep(self):
        sr2016 = electionstats.query_elections(2016, 2016, "State Rep", "General")
        self.assertEqual(len(sr2016), 160)
        # Add more here

    def test_gov_council(self):
        gc2018 = electionstats.query_elections(2018, 2018, "Gov Council", "General")
        self.assertEqual(len(gc2018), 8)

if __name__ == "__main__":
    unittest.main()
