# Table Ready

A quick-reference site for board and card games. You look up a game, choose how
many are playing, and get the setup, a turn summary, the end of the game and the
scoring on one screen. Every entry is written from the game's rulebook and links
to it.

This folder is self-contained and separate from the TuringMCP code in the rest
of the repository.

## What is here

| Path | What it holds |
|---|---|
| `data/games/*.json` | The database: one file per game |
| `data/schema.json` | The shape every entry must have |
| `pipeline/validate.py` | Checks every entry against the schema and consistency rules |
| `pipeline/fetch_rulebook.py` | Downloads a rulebook PDF and extracts its text for writing an entry |
| `site/build.py` | Generates the static site into `dist/` |
| `site/static/` | Stylesheet, script and the IBM Plex Sans font (SIL OFL, licence alongside) |
| `tests/behaviour.js` | Browser checks for every action and state |
| `captures/` | Screenshots of the built site at phone, tablet and desktop widths |

Everything except the browser test uses only the Python standard library.

## Build and preview

```sh
python3 tableready/site/build.py
python3 -m http.server 8137 --directory tableready/dist
```

Then open `http://127.0.0.1:8137/`. The build runs the validator first and stops
if any entry is invalid. Serve the folder as above; opening the files directly
does not resolve the folder links.

To run the browser checks (needs Playwright), keep the server running and:

```sh
node tableready/tests/behaviour.js
```

## Adding a game

1. Find the rulebook PDF, preferring the publisher's own file.
   `python3 tableready/pipeline/fetch_rulebook.py <slug> <url> [<fallback url>]`
   saves it under `.cache/` (not committed) and prints the lines that mention
   player counts. It warns when the file looks like a packaging sheet or has a
   broken text layer.
2. Check the edition. The first search hit is often a variant or an old printing.
3. Write `data/games/<slug>.json` from the rulebook text, in your own words.
   Copy an existing entry as a starting point.
4. Run `python3 tableready/pipeline/validate.py`, then rebuild.

## Rules for entries

- **Own words.** Restate the rules; do not copy rulebook sentences or artwork.
- **Link the source.** `source.url` is the file the entry was written from,
  `source.host` says whether it is the publisher's file or a copy hosted
  elsewhere, and `source.retrieved` is the date it was checked.
- **Name the edition.** Printings differ.
- **Player counts.** `players.covered` lists the counts the entry handles. A
  step or number that changes with player count uses `by_count`, with a value
  for every covered count. A rule that applies only at some counts uses `only`.
- **Setup order.** Steps are grouped `table`, `each player`, then `to start`
  (first player, turn-order steps).
- **Be honest about gaps.** Set `status` to `partial` and list what is missing
  in `not_covered`. List in `unverified` anything that was not read directly
  from the rulebook text, for example values printed only as icons.

## Current contents

57 games: 48 complete and 9 partial (35 board, 20 card, 2 dice). 26 were
written from the publisher's own file and 31 from library, retailer or other
copies of it.

Partial entries: Ark Nova, Carcassonne, Kutná Hora: The City of Silver, Risk (classic), Sagrada, Small World, The Crew: The Quest for Planet Nine, The Quacks of Quedlinburg, Ticket to Ride: Europe.

Two games in the first batch were skipped because no readable English rulebook
could be fetched: Hanabi (the publisher's PDF has no text layer) and Coup (the
copies found would not download).

`players.not_playable` lists counts a game does not allow (for example Sequence
with 5, 7 or 11 players); `kind` is `board`, `card` or `dice`.
