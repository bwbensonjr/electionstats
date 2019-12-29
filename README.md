# electionstats

This module provides an `electionstats.query_elections` function which
returns summaries of Massachusetts elections from the site
<https://electionstats.state.ma.us>. It returns a Pandas `DataFrame`
documented below.

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
| `date`             | `object`  | Election date             |
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

## Run Unit Tests

```python
python -m unittest tests.test_electionstats
```
