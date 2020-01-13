# electionstats

This module provides an `electionstats.query_elections` function which
returns summaries of Massachusetts elections from the site
<https://electionstats.state.ma.us>. It returns a Pandas `DataFrame`
documented below. There is an additional `electionstats.read_election`
that takes an `election_id` from `query_elections` and reads the
precinct-level or municipality-level results, based on the
`precincts_include` argument.

```python
electionstats.OFFICES = [
    "President",
    "US House",
    "US Senate",
    "State Rep",
    "State Senate",
    ]

electionstats.STAGES = [
    "General",
    "Primaries",
    "Democratic",
    "Republican",
    ]

electionstats.query_elections(year_from,
                              year_to,
                              office,
                              stage,
                              include_no_cand_elecs=False,
                              include_specials=False)
```

## Parameters

- `year_from` : `int` - The first year for which results should be returned
- `year_to` : `int` - The last year for which results should be returned
- `office` : `str` - The office results to be returned (e.g., "President", "US House", "State Rep", "State Senate")
- `stage` : `str` - The type of election to consider ("General", "Primaries", "Democratic", "Republican")
- `include_no_cand_elecs` : `boolean`, optional - Whether to include elections with zero candidates (default `False`)
- `include_specials` : `boolean`, optional -  Whether to include special elections (default `False`)

## Returns

The function returns a Pandas `DataFrame` with the following fields.

| column           | type    | description      |
|:-----------------|:--------|:-----------------|
| `election_id`      | `object`  | Unique election ID from electionstats website      |
| `year`             | `int64`   | Year of election             |
| `date`             | `datetime64[ns]`  | Election date             |
| `office`           | `object`  | Office of election (e.g., President, State Representative)           |
| `district`         | `object`  | District of election (e.g., United States, 31st Middlesex)         |
| `is_special`       | `bool`    | Whether the election is special election       |
| `party_primary`    | `object`  | `None` if not primary, otherwise party of primary    |
| `dem_candidate`    | `object`  | Democratic candidate or `None`    |
| `gop_candidate`    | `object`  | GOP candidate or `None`    |
| `other_candidates` | `object`  | Comma-separated list of 3rd party or Unenrolled candidates |
| `dem_votes`        | `float64` | Number of Democratic votes or `NaN`        |
| `gop_votes`        | `float64` | Number of GOP votes or `NaN`        |
| `total_votes`      | `int64`   | Total number of votes cast      |
| `other_votes`      | `int64`   | Number of 3rd party or Unenrolled votes or `NaN`      |
| `blank_votes`      | `int64`   | Number of blank ballots      |
| `num_candidates`   | `int64`   | Total number of candidates in election   |
| `winner`           | `object`  | Name of winning candidate           |
| `winner_votes`     | `int64`   | Number of votes received by winning candidate     |
| `winner_pct`       | `float64` | Percent of votes, based on `total_votes`       |
| `winning_party`    | `object`  | Party of winning candidate    |
| `candidates`       | `object`  | A dictionary containing detailed info on each candidate       |
| `dem_percent`      | `float64` | Two-party Democratic vote percent (Dem/(Dem+GOP))      |
| `incumbent`        | `object`  | Name of incumbent (might not be running)        |
| `prev_party`       | `object`  | Party of incumbent       |
| `open_race`        | `bool`    | `True` if incumbent is not running, `False` otherwise        |
| `incumbent_party`  | `object`  | Party of incumbent or `None` if open race  |
| `incumbent_status` | `object`  | `Dem_Incumbent`, `GOP_Incumbent`, or `No_Incumbent` if open race |

```python
electionstats.read_election(election_id, precincts_include)
```

## Parameters

- `election_id` : `int` - The unique ID for an election as returned by `query_elections`
- `precincts_include` : `bool` - If `True`, return precinct-level results, otherwise municipality-level

## Returns

The function returns a Pandas `DataFrame` with the following fields.

| column | type | description |
|:-----------------|:--------|:-----------------|
| `City/Town` | `object` | The municipality of the result |
| `Ward` | `object` | The electionw ward of the result or `-` if no ward |
| `Pct` | `object` | The precinct of the result |
| *Candidate1* | `int` | The number of votes for *Candidate1* |
| *...* | `int` | Addition candidate vote columns |
| `All Others` | `int` | Number of votes for unnamed candidates |
| `Blanks` | `int` | Number of blank non-votes |
| `Total Votes Cast` | `int` | The total number of ballots cast |

## Examples

```
>>> import electionstats
>>> sr2016 = electionstats.query_elections(2016, 2016, "State Rep", "General")
>>> len(sr2016)
160
>>> sr2016.sample().iloc[0]
election_id                                                    130361
year                                                             2016
date                                                       2016-11-08
office                                           State Representative
district                                               3rd Barnstable
is_special                                                      False
party_primary                                                    None
dem_candidate                                      Matthew C. Patrick
gop_candidate                                         David T. Vieira
other_candidates                                                     
dem_votes                                                       11317
gop_votes                                                       12739
total_votes                                                     25607
other_votes                                                        11
blank_votes                                                      1540
num_candidates                                                      2
winner                                                David T. Vieira
winner_votes                                                    12739
winner_pct                                                   0.497481
winning_party                                              Republican
candidates          [{'id': '62662', 'votesmart_id': '54354', 'slu...
dem_percent                                                  0.470444
incumbent                                             David T. Vieira
prev_party                                                 Republican
open_race                                                       False
incumbent_party                                            Republican
incumbent_status                                        GOP_Incumbent
Name: 97, dtype: object
>>> sr2016_pcts = electionstats.read_election(sr2016["election_id"])
>>> sr2016_pcts.sample().iloc[0]
City/Town            Pepperell
Ward                         -
Pct                          1
Clinton/ Kaine             965
Trump/ Pence              1053
Johnson/ Weld              170
Stein/ Baraka               23
Mcmullin/ Johnson            7
Kotlikoff/ Leamer            0
Feegbeh/ O'Brien             0
Moorehead/ Lilly             0
Schoenke/ Mitchel            0
All Others                  45
No Preference                0
Blanks                      36
Total Votes Cast          2299
Name: 1503, dtype: object
```

## Run Unit Tests

```python
python -m unittest tests.test_electionstats
```
