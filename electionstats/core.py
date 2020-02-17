"""Download Massachusetts election results from electionstats.state.ma.us"""

import pandas as pd
import requests

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    }

BASE_URL = "http://electionstats.state.ma.us/elections/"
SEARCH_URL = (BASE_URL +
              "search/year_from:{year_from}/year_to:{year_to}/office_id:{office_id}/stage:{stage}")
ELECTION_URL = BASE_URL + "view/{election_id}/"
DOWNLOAD_URL = BASE_URL + "download/{election_id}/precincts_include:{precincts_include}/"

OFFICE_ID = {
    "President": 1,
    "US House": 5,
    "US Senate": 6,
    "State Rep": 8,
    "State Senate": 9,
    "Gov Council": 529,
    }

OFFICES = list(OFFICE_ID.keys())

ELECTION_FREQ = {
    OFFICE_ID["President"]: 4,
    OFFICE_ID["US House"]: 2,
    OFFICE_ID["US Senate"]: 6,
    OFFICE_ID["State Rep"]: 2,
    OFFICE_ID["State Senate"]: 2,
    OFFICE_ID["Gov Council"]: 2,
    }

STAGES = [
    "General",
    "Primaries",
    "Democratic",
    "Republican",
    ]

def main():
    pres = query_elections(2004, 2016, OFFICE_ID["President"], "General")
    # us_sen = query_elections(2004, 2016, OFFICE_ID["US Senate"], "General")
    # us_rep = query_elections(2004, 2016, OFFICE_ID["US House"], "General")
    ma_rep = query_elections(2008, 2008, OFFICE_ID["State Rep"], "General")
    ma_rep = ma_rep[(ma_rep["year"] == "2008") & (~ma_rep["is_special"])]
    ma_rep["precinct_results"] = ma_rep["election_id"].map(read_election)
    ma_rep_08_pcts = pd.concat(list(ma_rep["precinct_results"]), ignore_index=True)[["election_id", "City/Town", "Ward", "Pct"]]
    
def query_elections(year_from, year_to, office, stage, include_no_cand_elecs=False, include_specials=False):
    """Read a summary of election results.
    
    Paramaters
    ----------
    year_from : int
        The first year for which results should be returned
    year_to : int
        The last year for which results should be returned
    office : str
        Which office results to return (e.g., "President", "US House", "State Rep", "State Senate")
    stage : str
        Which type of election ("General", "Primaries", "Democratic", "Republican")
    include_no_cand_elecs : boolean, optional
        Whether to include elections with zero candidates (default False)
    include_specials : boolean, optional
        Whether to include special elections (default False)

    Returns
    -------
        pandas.DataFrame
           A summary of each election results in each row
    """
    office_id = OFFICE_ID[office]
    elecs_list = []
    # for year in range(year_from, year_to+1, ELECTION_FREQ[office_id]):
    for year in range(year_from, year_to+1):
        elecs = query_elections_work(year, office_id, stage, include_no_cand_elecs, include_specials)
        if not elecs is None:
            elecs_list.append(elecs)
    elecs_all = pd.concat(elecs_list, ignore_index=True).sort_values(["date", "district"])
    return elecs_all

def query_elections_work(year, office_id, stage, include_no_cand_elecs=False, include_specials=False):
    # Need to include previous election for incumbency determination
    prev_elec_year = year - ELECTION_FREQ[office_id]
    search_url = SEARCH_URL.format(year_from=prev_elec_year,
                                   year_to=year,
                                   office_id=office_id,
                                   stage=stage)
    r = requests.get(search_url, headers=JSON_HEADERS)
    rj = r.json()
    elecs = pd.DataFrame([election_details(e) for e in rj["output"]])
    elecs["date"] = pd.to_datetime(elecs["date"])
    if len(elecs) == 0:
        return None
    if not include_no_cand_elecs:
        elecs = elecs[elecs["num_candidates"] != 0]
    if len(elecs) == 0:
        return None
    elecs = elecs.sort_values(["date", "district"])
    elecs = elecs.groupby("district").apply(find_incumbent)
    elecs = elecs.groupby("district").apply(find_prev_party)
    elecs = elecs[elecs["year"] == year]
    if len(elecs) == 0:
        return None
    if not include_specials:
        elecs = elecs[elecs["is_special"] == False]
    if len(elecs) == 0:
        return None
    elecs["open_race"] = elecs.apply(open_race, axis=1)
    elecs["incumbent_party"] = elecs.apply(incumbent_party, axis=1)
    elecs["incumbent_status"] = elecs.apply(incumbent_status, axis=1)
    return elecs

def read_election(election_id, precincts_include=True):
    """Read town-by-town or precinct-by-precinct CSV as DataFrame."""
    if precincts_include:
        ct = pd.read_csv(DOWNLOAD_URL.format(election_id=election_id,
                                             precincts_include=1),
                         thousands=",",
                         dtype={"Ward": str, "Pct": str},
                         skiprows=[1],
                         skipfooter=1,
                         engine="python")
    else:
        ct = pd.read_csv(DOWNLOAD_URL.format(election_id=election_id,
                                             precincts_include=0),
                         thousands=",",
                         dtype={"Ward": str, "Pct": str},
                         usecols=not_unnamed_ward_pct,
                         skiprows=[1],
                         skipfooter=1,
                         engine="python")
    return ct
    
def not_unnamed_ward_pct(col_name):
    nu = ((not col_name.startswith("Unnamed:")) and
          (col_name != "Ward") and
          (col_name != "Pct"))
    return nu

def election_details(e):
    winning_cand = winning_candidate(e["Candidate"])
    if winning_cand:
        winner = winning_cand["display_name"]
        winner_votes = int(winning_cand["CandidateToElection"]["n_votes"])
        winner_pct = winner_votes / int(e["Election"]["n_total_votes"])
        if e["Election"]["party_primary"]:
            winning_party = e["Election"]["party_primary"]
        else:
            winning_party = winning_cand["CandidateToElection"]["party"]
    else:
        winner = None
        winning_party = None
        winner_votes = None
        winner_pct = None
    ed = {
        "election_id": e["Election"]["id"],
        "year": int(e["Election"]["year"]),
        "date": e["Election"]["date"],
        "office": e["Office"]["name"],
        "district": election_district(e),
        "is_special": True if e["Election"]["is_special"] else False,
        "party_primary": e["Election"]["party_primary"],
        "dem_candidate": dem_candidate(e),
        "gop_candidate": gop_candidate(e),
        "other_candidates": other_candidates(e),
        "dem_votes": dem_votes(e),
        "gop_votes": gop_votes(e),
        "total_votes": int(e["Election"]["n_total_votes"]),
        "other_votes": int(e["Election"]["n_all_other_votes"]),
        "blank_votes": int(e["Election"]["n_blank_votes"]),
        "num_candidates": len(e["Candidate"]),
        "winner": winner,
        "winner_votes": winner_votes,
        "winner_pct": winner_pct,
        "winning_party": winning_party,
        "candidates": e["Candidate"],
    }
    ed["dem_percent"] = dem_percent(ed)
    return ed

def get_candidate(e, party):
    if party is None:
        cands = []
        for c in e["Candidate"]:
            if ((c["CandidateToElection"]["party"] != "Democratic") and
                (c["CandidateToElection"]["party"] != "Republican")):
                cands.append(c)
        return cands
    else:
        for c in e["Candidate"]:
            if c["CandidateToElection"]["party"] == party:
                return c
    return None

def dem_candidate(e):
    c = get_candidate(e, "Democratic")
    if c is None:
        return None
    else:
        return c["CandidateToElection"]["display_name"]

def gop_candidate(e):
    c = get_candidate(e, "Republican")
    if c is None:
        return None
    else:
        return c["CandidateToElection"]["display_name"]

def other_candidates(e):
    cs = get_candidate(e, None)
    if cs is None:
        return None
    else:
        names = [c["CandidateToElection"]["display_name"] for c in cs]
        names_str = ",".join(names)
        return names_str

def dem_votes(e):
    c = get_candidate(e, "Democratic")
    if c is None:
        return None
    else:
        return int(c["CandidateToElection"]["n_votes"])

def gop_votes(e):
    c = get_candidate(e, "Republican")
    if c is None:
        return None
    else:
        return int(c["CandidateToElection"]["n_votes"])

def dem_percent(ed):
    dem_votes = ed["dem_votes"]
    gop_votes = ed["gop_votes"]
    if dem_votes and gop_votes:
        dp = dem_votes / (dem_votes + gop_votes)
    else:
        dp = None
    return dp
    
def election_district(e):
    office_name = e["Office"]["name"]
    if office_name == "President":
        district = "United States"
    elif office_name == "U.S. Senate":
        district = "Massachusetts"
    else:
        district = e["District"]["display_name"]
    return district
    
def winning_candidate(cands):
    for cand in cands:
        if cand["CandidateToElection"]["is_winner"]:
            return cand
    return None

def find_incumbent(df):
    df["incumbent"] = df["winner"].shift(1)
    return df

def find_prev_party(df):
    df["prev_party"] = df["winning_party"].shift(1)
    return df

def open_race(e):
    open = (e["incumbent"] not in [c["display_name"] for c in e["candidates"]])
    return open

def incumbent_party(e):
    if e["incumbent"]:
        for c in e["candidates"]:
            if c["display_name"] == e["incumbent"]:
                party = c["CandidateToElection"]["party"]
                return party
    else:
        return None

# This function gives an answer of zero when
# and incumbent runs under a different party
# e.g., election IDs 131567 and 131541
def incumbent_status(e):
    if e["incumbent_party"] == "Democratic":
        return "Dem_Incumbent"
    elif e["incumbent_party"] == "Republican":
        return "GOP_Incumbent"
    else:
        return "No_Incumbent"

# Code for converting word-based numbers to numeric
# format and vice-versa, primarily for differing legislative
# district formats.

NUMBERS = {
    'First': '1st',
    'Second': '2nd',
    'Third': '3rd',
    'Fourth': '4th',
    'Fifth': '5th',
    'Sixth': '6th',
    'Seventh': '7th',
    'Eighth': '8th',
    'Ninth': '9th',
    'Tenth': '10th',
    'Eleventh': '11th',
    'Twelfth': '12th',
    'Thirteenth': '13th',
    'Fourteenth': '14th',
    'Fifteenth': '15th',
    'Sixteenth': '16th',
    'Seventeenth': '17th',
    'Eighteenth': '18th',
    'Nineteenth': '19th',
    'Twentieth': '20th',
    'Twenty-First': '21st',
    'Twenty-Second': '22nd',
    'Twenty-Third': '23rd',
    'Twenty-Fourth': '24th',
    'Twenty-Fifth': '25th',
    'Twenty-Sixth': '26th',
    'Twenty-Seventh': '27th',
    'Twenty-Eighth': '28th',
    'Twenty-Ninth': '29th',
    'Thirtieth': '30th',
    'Thirty-First': '31st',
    'Thirty-Second': '32nd',
    'Thirty-Third': '33rd',
    'Thirty-Fourth': '34th',
    'Thirty-Fifth': '35th',
    'Thirty-Sixth': '36th',
    'Thirty-Seventh': '37th',
}

WORDS = {NUMBERS[word]: word for word in NUMBERS}

def word_to_number(name):
    """Convert the first word of a legislative distrct like
    'First Middlesex' to '1st Middlesex."""
    parts = name.split(" ")
    word = parts[0]
    if word in NUMBERS:
        parts[0] = NUMBERS[word]
        new_name = " ".join(parts)
    return new_name

def number_to_word(dist):
    """Convert the first word of a legislative distrct like
    '1st Middlesex' to 'First Middlesex."""
    parts = name.split(" ")
    num = parts[0]
    if num in WORDS:
        parts[0] = WORDS[num]
        new_name = " ".join(parts)
    return new_name

    
if __name__ == "__main__":
    main()
    
