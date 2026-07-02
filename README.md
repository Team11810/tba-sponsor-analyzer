# tba-sponsor-analyzer

## What does this project do?

[FIRST Robotics Competition (FRC)](https://www.firstinspires.org/robotics/frc) is a robotics competition for high school students. Every team needs money, tools, and mentors to build a robot, so teams get help from **sponsors** — companies, schools, and organizations that donate money, equipment, or time.

[The Blue Alliance (TBA)](https://www.thebluealliance.com/) is a website that tracks data on every FRC team and event. It has an API (a way for programs to ask a website for data) that we can use to download information about teams.

The problem: TBA doesn't have a "list of sponsors" you can just download. Instead, sponsor names are jammed into each team's official `name` field, all mixed together in a single line of text. This project is a two-step pipeline that:

1. **Downloads every active FRC team from TBA** and saves it to a spreadsheet-friendly file (`teams.csv`).
2. **Picks apart that messy `name` text** to figure out who each team's sponsors are, then counts how many teams each sponsor supports (`sponsors.json`).

By the end, you'll have a file that can answer questions like "which company sponsors the most FRC teams?" or "which sponsors support teams in Utah?"

## Before you start

You'll need:

- **Python** installed on your computer (version 3.10 or newer). You can check what you have by opening a terminal and typing `python --version`. If that doesn't work, download Python from [python.org](https://www.python.org/downloads/).
- **A terminal** (also called a command line or console). On Windows this is PowerShell or Git Bash; on Mac/Linux it's called Terminal.
- **A free TBA account**, so you can get an API key (instructions are in Step 4 below).
- Some familiarity with typing commands into a terminal and pressing Enter. If a command in this guide looks unfamiliar, that's okay — just type it exactly as shown.

## Step 1: Get the code

If you haven't already, download or clone this repository, then open a terminal **inside the project folder** (the folder that contains this README).

## Step 2: Set up a Python virtual environment

A "virtual environment" (or "venv") is a private, isolated copy of Python just for this project. It keeps the packages this project needs separate from everything else on your computer, so nothing gets mixed up or broken.

Create one:

```sh
python -m venv .venv
```

This creates a `.venv` folder. You only need to do this once. Now activate it (turn it on) — you'll need to do this every time you open a new terminal to work on this project:

**Windows (PowerShell or Git Bash):**
```sh
.venv\Scripts\activate
```

**Mac/Linux:**
```sh
source .venv/bin/activate
```

You'll know it worked if you see `(.venv)` appear at the start of your terminal prompt.

## Step 3: Install the dependencies

"Dependencies" are other people's code that this project relies on, instead of reinventing everything from scratch. With your virtual environment activated, run:

```sh
pip install -r requirements.txt
```

This reads the `requirements.txt` file in this project and installs everything listed there, including the official TBA API client library.

## Step 4: Get your own TBA API key

An API key is like a password that identifies you to TBA's servers, so they know who's asking for data. You need your own — never share it or commit it to git.

1. Go to your [TBA account page](https://www.thebluealliance.com/account) and sign in (or create a free account).
2. Scroll to the "Read API Keys" section and generate a new key.
3. Copy the key somewhere safe — you'll need it in the next step.

## Step 5: Configure your API key

This project reads your API key from a file named `.env`, which is never uploaded to git (it's listed in `.gitignore` on purpose, so you don't accidentally share your private key with the world).

Copy the example file to create your own:

```sh
cp .env.example .env
```

Then open `.env` in a text editor and fill in your key, so it looks like:

```
TBA_AUTH_KEY=your-actual-key-goes-here
```

Save the file.

## Step 6: Run the scripts

Make sure your virtual environment is still activated (you should see `(.venv)` in your prompt), then run the two scripts **in order** — the second one depends on the output of the first.

**Download all active teams:**

```sh
python export_teams.py
```

This asks TBA for every team that competed in the 2025 season, one "page" of ~500 teams at a time, and saves the results to `teams.csv`. You'll see progress printed as each page downloads. When it's done, you'll have a `teams.csv` file with one row per team and these columns:

| Column | Meaning |
| --- | --- |
| `team_number` | The team's official number (e.g. 254) |
| `key` | TBA's internal ID for the team (e.g. `frc254`) |
| `nickname` | The team's nickname |
| `name` | The team's full official name — this is the messy field that has sponsor names crammed into it |
| `city`, `state_prov`, `country` | Where the team is based |
| `website` | The team's website, if they have one |

You can open `teams.csv` in Excel, Google Sheets, or any spreadsheet program to look through it.

**Extract the sponsor list:**

```sh
python extract_sponsors.py
```

This reads `teams.csv`, figures out the sponsors hidden in each team's `name` field (see "How sponsor extraction works" below), and writes `sponsors.json`.

## Understanding sponsors.json

`sponsors.json` is a **JSON file** — a common format for storing structured data that both humans and programs can read. It contains a list of sponsor records that looks like this:

```jsonc
{
  "sponsor": "Boeing",
  "qty": 218,
  "qty_utah": 3,
  "teams": [
    {"team_number": 31, "state": "Oklahoma"}
    // ...more teams
  ]
}
```

Here's what each field means:

- `sponsor` — the sponsor's name.
- `qty` — how many teams list this sponsor.
- `qty_utah` — how many of those teams are based in the state of Utah.
- `teams` — a list of every team that has this sponsor, including that team's number and the state it's from.

The file is sorted with the most common sponsors first.

## Bonus: querying sponsors.json with jq

[`jq`](https://jqlang.org/) is a small command-line tool for reading and filtering JSON files, without having to write a whole program. You may need to install it separately (it doesn't come with Python). Here are two examples you can try:

**Top 10 sponsors overall, by number of teams:**

```sh
jq --argjson n 10 'sort_by(-.qty)[:$n] | map({sponsor, qty})' sponsors.json
```

**Top 10 sponsors in Utah, by number of Utah teams:**

```sh
jq --argjson n 10 '[.[] | select(.qty_utah > 0)] | sort_by(-.qty_utah)[:$n] | map({sponsor, qty_utah})' sponsors.json
```

You can change `--argjson n 10` to any number to see more or fewer results.

## How sponsor extraction works (and why it's not perfect)

TBA doesn't have a dedicated "sponsors" field — sponsor names are packed into each team's `name` field as unstructured text, shaped roughly like:

```
Sponsor1/Sponsor2/Sponsor3&School Name
```

Sponsors are separated by `/`, and the school name is tacked on at the end after an `&`. `extract_sponsors.py` splits each team's `name` on `/`, then looks at the very last piece and splits *that* on its last `&` to separate the final sponsor from the school name.

This mostly works, but real-world data is messy:

- Some sponsor names contain their own `&`, like "Florida Power & Light" or "Boys & Girls Club" — these are usually fine as long as they aren't the very last sponsor in the list.
- Some teams have multiple schools or extra organizations chained together with more `&`s, which can confuse the split.
- About 800 of the roughly 3,700 teams have more than one `&` in their name, so some of these edge cases are unavoidable.

There's no way to parse this perfectly without a human reading every single team name, so treat `sponsors.json` as a very good estimate, not a perfectly accurate list.

## Project files

| File | Purpose |
| --- | --- |
| `export_teams.py` | Downloads team data from TBA into `teams.csv` |
| `extract_sponsors.py` | Turns `teams.csv` into `sponsors.json` |
| `csv_utils.py` | A small shared helper that keeps `teams.csv` safe to open in Excel/Sheets |
| `requirements.txt` | The list of Python packages this project needs |
| `.env.example` | A template showing what your `.env` file should look like |
| `teams.csv`, `sponsors.json` | Generated output files (not stored in git — you create them by running the scripts) |

## License

MIT — see [LICENSE](LICENSE). This means you're free to use, copy, modify, and share this code, as long as you keep the original copyright notice.
