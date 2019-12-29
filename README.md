# electionstats

This module provides an `electionstats.query_elections` function which
returns summaries of Massachusetts elections from the site
[](https://electionstats.state.ma.us). It returns a Pandas `DataFrame`
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

    `year_from` : `int`
        The first year for which results should be returned
    `year_to` : `int`
        The last year for which results should be returned
    `office` : `str`
        Which office results to return (e.g., "President", "US House", "State Rep", "State Senate")
    `stage` : `str`
        Which type of election ("General", "Primaries", "Democratic", "Republican")
    `include_no_cand_elecs` : `boolean`, optional
        Whether to include elections with zero candidates (default False)
    `include_specials` : `boolean`, optional
        Whether to include special elections (default False)

## Returns

The function returns a Pandas `DataFrame` with the following fields.



