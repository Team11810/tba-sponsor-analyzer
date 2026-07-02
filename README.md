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
