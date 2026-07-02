"""Export all FRC teams active in a given year from The Blue Alliance to a CSV file."""

import csv
import os
import sys

from dotenv import load_dotenv
import tbaapiv3client
from tbaapiv3client.api.team_api import TeamApi
from tbaapiv3client.rest import ApiException

YEAR = 2025
OUTPUT_PATH = "teams.csv"
FIELDS = ["team_number", "key", "nickname", "name", "city", "state_prov", "country", "website"]
FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(value) -> str:
    """Prefix values that spreadsheet apps would interpret as formulas."""
    s = "" if value is None else str(value)
    return "'" + s if s.startswith(FORMULA_TRIGGERS) else s


def main() -> None:
    load_dotenv()
    auth_key = os.environ.get("TBA_AUTH_KEY")
    if not auth_key:
        sys.exit("TBA_AUTH_KEY is not set. Copy .env.example to .env and fill in your key.")

    configuration = tbaapiv3client.Configuration(
        host="https://www.thebluealliance.com/api/v3",
        api_key={"X-TBA-Auth-Key": auth_key},
    )

    teams = []
    with tbaapiv3client.ApiClient(configuration) as api_client:
        api_client.user_agent = "tba-sponsor-analyzer/0.1"
        team_api = TeamApi(api_client)

        page_num = 0
        while True:
            try:
                page = team_api.get_teams_by_year(YEAR, page_num)
            except ApiException as e:
                sys.exit(f"TBA API request failed on page {page_num}: {e}")
            if not page:
                break
            teams.extend(page)
            print(f"Fetched page {page_num} ({len(page)} teams)")
            page_num += 1

    teams.sort(key=lambda t: t.team_number)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for team in teams:
            writer.writerow({field: _csv_safe(getattr(team, field)) for field in FIELDS})

    print(f"Wrote {len(teams)} teams to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
