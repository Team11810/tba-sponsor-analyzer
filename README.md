# tba-sponsor-analyzer

Exports the roster of FRC teams active in the 2025 season from [The Blue Alliance](https://www.thebluealliance.com/) API to `teams.csv`.

## Setup

```sh
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Get an API key from your [TBA account page](https://www.thebluealliance.com/account), then:

```sh
cp .env.example .env
# edit .env and set TBA_AUTH_KEY=<your key>
```

## Usage

```sh
python export_teams.py
```

Writes `teams.csv` with columns: `team_number, key, nickname, name, city, state_prov, country, website`.

```sh
python extract_sponsors.py
```

Reads `teams.csv` and writes `sponsors.json`, an array of records shaped like:

```json
{
  "sponsor": "Boeing",
  "qty": 218,
  "num_utah": 3,
  "teams": [
    {"team_number": 31, "state": "Oklahoma"},
    ...
  ]
}
```

`qty` is the number of teams listing that sponsor; `num_utah` is how many of those teams are in Utah.

TBA has no dedicated sponsor field; the `name` field is unstructured text shaped like `Sponsor1/Sponsor2/Sponsor3&School Name`. `extract_sponsors.py` splits on `/` for sponsors and peels a trailing school name off the last segment via its rightmost `&`. This is a best-effort heuristic: about 800 of 3731 teams have more than one `&` in their name (sponsor names that legitimately contain `&`, e.g. "Florida Power & Light", or teams with multiple chained school/org affiliations), and those can produce a stray fragment in the sponsor or school position. Not fixable without manual review of TBA's raw data.
