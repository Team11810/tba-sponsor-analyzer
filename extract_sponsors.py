"""Extract a deduplicated sponsor list from teams.csv.

TBA's `name` field has no dedicated sponsor field; it's an unstructured
string shaped like "Sponsor1/Sponsor2/Sponsor3&School Name". Sponsor names
can themselves contain "&" (e.g. "Florida Power & Light"), and some teams
chain multiple school/org affiliations with extra "&"s, so this parsing is
a best-effort heuristic, not exact:

  - If the name has no "&" at all, it's treated as a bare school name with
    no listed sponsors.
  - Otherwise the name is split on "/"; every segment except the last is a
    sponsor as-is. The last segment is split on its rightmost "&" only,
    peeling off a trailing school name and keeping the remainder as the
    final sponsor.
"""

import csv
import json
import re
import sys
from collections import OrderedDict

INPUT_PATH = "teams.csv"
OUTPUT_PATH = "sponsors.json"

_WHITESPACE_RE = re.compile(r"\s+")


def normalize(sponsor: str) -> str:
    return _WHITESPACE_RE.sub(" ", sponsor.strip())


def parse_sponsors(name: str) -> list[str]:
    if "&" not in name:
        return []

    segments = name.split("/")
    sponsors = [normalize(s) for s in segments[:-1]]

    last_sponsor, _, _school = segments[-1].rpartition("&")
    if last_sponsor:
        sponsors.append(normalize(last_sponsor))

    return [s for s in OrderedDict.fromkeys(sponsors) if s]


def main() -> None:
    try:
        with open(INPUT_PATH, encoding="utf-8") as f:
            teams = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.exit(f"{INPUT_PATH} not found. Run export_teams.py first.")

    sponsors: dict[str, list[dict]] = {}
    for team in teams:
        for sponsor in parse_sponsors(team["name"]):
            sponsors.setdefault(sponsor, []).append({
                "team_number": int(team["team_number"]),
                "state": team["state_prov"],
            })

    records = [
        {
            "sponsor": sponsor,
            "qty": len(teams_for_sponsor),
            "num_utah": sum(1 for t in teams_for_sponsor if t["state"] == "Utah"),
            "teams": teams_for_sponsor,
        }
        for sponsor, teams_for_sponsor in sponsors.items()
    ]
    records.sort(key=lambda r: (-r["qty"], r["sponsor"]))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} unique sponsors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
