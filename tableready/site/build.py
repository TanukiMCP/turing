#!/usr/bin/env python3
"""Build the static Table Ready site from data/games/*.json into dist/.

Standard library only. Run from anywhere:

    python3 tableready/site/build.py

Every page is complete without JavaScript: all player counts are listed.
static/app.js then narrows the page to the chosen player count.
"""
import json
import shutil
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "data" / "games"
STATIC = ROOT / "site" / "static"
DIST = ROOT / "dist"
SITE_NAME = "Table Ready"
TAGLINE = "Setup, turn and scoring for your player count, checked against the rulebook."

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def e(text):
    return escape(str(text), quote=True)


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def player_range(players):
    lo, hi = players["min"], players["max"]
    return f"{lo} players" if lo == hi else f"{lo}–{hi} players"


def count_phrase(counts):
    """[2] -> '2 players', [2, 3] -> '2 or 3 players', [2, 3, 4] -> '2–4 players'."""
    counts = sorted(counts)
    if len(counts) == 1:
        return f"{counts[0]} player" if counts[0] == 1 else f"{counts[0]} players"
    if len(counts) == 2:
        return f"{counts[0]} or {counts[1]} players"
    if counts == list(range(counts[0], counts[-1] + 1)):
        return f"{counts[0]}–{counts[-1]} players"
    return ", ".join(str(n) for n in counts[:-1]) + f" or {counts[-1]} players"


def only_attr(item):
    return f' data-only="{",".join(str(n) for n in item["only"])}"' if item.get("only") else ""


def only_label(item):
    if not item.get("only"):
        return ""
    return f'<span class="only-label">With {e(count_phrase(item["only"]))}:</span> '


def variants(item):
    """The per-player-count lines of a step, one per covered count."""
    if not item.get("by_count"):
        return ""
    lines = "".join(
        f'<span class="variant" data-count="{e(n)}">'
        f'<span class="per-label">{e(count_phrase([int(n)]))}:</span> {e(text)}</span>'
        for n, text in sorted(item["by_count"].items(), key=lambda kv: int(kv[0]))
    )
    return f' <span class="variants">{lines}</span>'


def page(title, description, body, depth, body_class):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="preload" href="{up}static/fonts/ibm-plex-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{up}static/style.css">
<script src="{up}static/app.js" defer></script>
</head>
<body class="{body_class}">
<header class="site-header"><a class="site-name" href="{up or './'}">{SITE_NAME}</a></header>
{body}
<footer class="site-footer">
<p>Rules are summarised in our own words from each game's rulebook, with a link to the source. Game names belong to their publishers; this site is not affiliated with any of them.</p>
</footer>
</body>
</html>
"""


def value_class(value):
    """Short values take the large numeral size; phrases drop to text size."""
    return "value long" if len(str(value)) > 14 else "value"


def key_numbers(game):
    rows = []
    for number in game["key_numbers"]:
        value = number["value"]
        if isinstance(value, dict):
            per = "".join(
                f'<span class="per" data-count="{e(n)}">'
                f'<span class="per-label">{e(count_phrase([int(n)]))}</span> '
                f'<span class="{value_class(v)}">{e(v)}</span></span>'
                for n, v in sorted(value.items(), key=lambda kv: int(kv[0]))
            )
            rows.append(f'<div class="fact dep"><dt>{e(number["label"])}</dt><dd>{per}</dd></div>')
        else:
            rows.append(
                f'<div class="fact"><dt>{e(number["label"])}</dt>'
                f'<dd><span class="{value_class(value)}">{e(value)}</span></dd></div>'
            )
    return f'<dl class="facts">{"".join(rows)}</dl>'


def setup(game):
    out = []
    index = 0
    for group, heading in (("table", "On the table"), ("each player", "Each player"), ("to start", "To start")):
        items = [s for s in game["setup"] if s["group"] == group]
        if not items:
            continue
        lis = []
        for item in items:
            box_id = f"step-{index}"
            lis.append(
                f'<li class="step"{only_attr(item)}><input type="checkbox" id="{box_id}" data-step="{index}">'
                f'<label for="{box_id}">{only_label(item)}{e(item["text"])}{variants(item)}</label></li>'
            )
            index += 1
        out.append(f'<h3 class="group">{heading}</h3><ul class="checks">{"".join(lis)}</ul>')
    return "".join(out)


def plain_list(items, tag="ul"):
    lis = "".join(f'<li{only_attr(i)}>{only_label(i)}{e(i["text"])}{variants(i)}</li>' for i in items)
    return f'<{tag} class="plain">{lis}</{tag}>'


def count_control(game):
    players = game["players"]
    covered = set(players["covered"])
    # "All" is the explicit no-choice option, so nothing is selected silently.
    options = [
        '<label class="count-option"><input type="radio" name="players" value="" checked>'
        "<span>All</span></label>"
    ]
    for n in range(players["min"], players["max"] + 1):
        disabled = "" if n in covered else " disabled"
        options.append(
            f'<label class="count-option"><input type="radio" name="players" value="{n}"{disabled}>'
            f"<span>{n}</span></label>"
        )
    unplayable = players.get("not_playable", [])
    uncovered = [n for n in range(players["min"], players["max"] + 1) if n not in covered and n not in unplayable]
    note = ""
    if unplayable:
        note += f'<p class="count-note">The game can\'t be played with {count_phrase(unplayable)}.</p>'
    if uncovered:
        what = "Solo play" if uncovered == [1] else f"Play with {count_phrase(uncovered)}"
        note += f'<p class="count-note">{what} isn\'t covered yet.</p>'
    return (
        '<fieldset class="count js-only" hidden>'
        "<legend>How many players?</legend>"
        f'<div class="count-options">{"".join(options)}</div>'
        '<p class="count-help" aria-live="polite"></p>'
        f"{note}</fieldset>"
    )


def game_page(game):
    source = game["source"]
    meta_bits = [player_range(game["players"])]
    if game.get("play_time"):
        meta_bits.append(game["play_time"])
    if game.get("age"):
        meta_bits.append(f'ages {game["age"]}')
    partial = ""
    if game["status"] == "partial":
        gaps = " ".join(e(g) for g in game.get("not_covered", [])) or "Some sections are not finished."
        partial = f'<p class="notice"><strong>Partial entry.</strong> {gaps}</p>'

    round_end = ""
    if game.get("round_end"):
        lis = "".join(f"<li>{e(t)}</li>" for t in game["round_end"])
        round_end = f'<h3 class="group">End of each round</h3><ul class="plain">{lis}</ul>'
    tiebreak = f'<p class="tie"><strong>Tie-break:</strong> {e(game["tiebreak"])}</p>' if game.get("tiebreak") else ""
    missed = ""
    jump_missed = ""
    if game["missed"]:
        missed = f'<section id="missed"><h2>Easily missed</h2>{plain_list(game["missed"])}</section>'
        jump_missed = '<a href="#missed">Missed</a>'

    host = "The publisher's own file" if source["host"] == "publisher" else "A copy of the publisher's file, hosted elsewhere"
    about_rows = [
        ("Rulebook", f'<a href="{e(source["url"])}" rel="noopener">{e(source["title"])}</a>'),
        ("Edition", e(game["edition"])),
        ("Checked", e(nice_date(source["retrieved"]))),
        ("Source", e(host)),
        ("Publisher", e(game["publisher"])),
    ]
    if game.get("designer"):
        about_rows.append(("Designer", e(game["designer"])))
    about = "".join(f'<div class="fact"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in about_rows)
    extra = ""
    if game.get("not_covered"):
        lis = "".join(f"<li>{e(t)}</li>" for t in game["not_covered"])
        extra += f'<h3 class="group">Not covered</h3><ul class="plain">{lis}</ul>'
    if game.get("unverified"):
        lis = "".join(f"<li>{e(t)}</li>" for t in game["unverified"])
        extra += f'<h3 class="group">Not checked against the rulebook text</h3><ul class="plain">{lis}</ul>'

    players = game["players"]
    body = f"""<main class="game" data-slug="{e(game['slug'])}" data-min="{players['min']}" data-max="{players['max']}" data-covered="{','.join(str(n) for n in players['covered'])}" data-unplayable="{','.join(str(n) for n in players.get('not_playable', []))}">
<div class="lead">
<h1>{e(game['name'])}</h1>
<p class="meta">{e(' · '.join(meta_bits))}<br>{e(game['edition'])} · checked {e(nice_date(source['retrieved']))}</p>
{partial}
{count_control(game)}
<section id="numbers" aria-labelledby="numbers-h"><h2 id="numbers-h">Key numbers</h2>{key_numbers(game)}</section>
</div>
<div class="rules">
<nav class="jump" aria-label="On this page"><a href="#setup">Setup</a><a href="#turn">Turn</a><a href="#end">End</a><a href="#scoring">Scoring</a>{jump_missed}</nav>
<section id="setup"><h2>Setup</h2>{setup(game)}<button type="button" class="clear-ticks js-only" hidden>Clear ticks</button></section>
<section id="turn"><h2>Your turn</h2><p>{e(game['turn']['summary'])}</p><ol class="plain">{''.join(f'<li>{e(s)}</li>' for s in game['turn']['steps'])}</ol>{round_end}</section>
<section id="end"><h2>End of the game</h2><p>{e(game['end'])}</p></section>
<section id="scoring"><h2>Scoring</h2>{plain_list(game['scoring'])}{tiebreak}</section>
{missed}
<section id="about"><h2>About this entry</h2><dl class="facts compact">{about}</dl>{extra}</section>
</div>
</main>"""
    title = f"{game['name']}: setup, turn and scoring for {player_range(players)} | {SITE_NAME}"
    description = (
        f"{game['name']} quick reference: setup for {player_range(players)}, turn summary, "
        f"end of game and scoring. Checked against the {game['edition']}."
    )
    return page(title, description, body, depth=2, body_class="page-game")


def home_page(games):
    rows = []
    for game in games:
        kind = {"card": "card game", "dice": "dice game"}.get(game["kind"], "board game")
        tag = ' <span class="tag">Partial</span>' if game["status"] == "partial" else ""
        rows.append(
            f'<li class="game-row" data-name="{e(game["name"].lower())}">'
            f'<a href="games/{e(game["slug"])}/">{e(game["name"])}</a>'
            f'<span class="meta">{e(player_range(game["players"]))} · {kind}{tag}</span></li>'
        )
    count = len(games)
    body = f"""<main class="home">
<h1>{SITE_NAME}</h1>
<p class="tagline">{TAGLINE}</p>
<div class="finder js-only" hidden>
<label for="find">Find a game</label>
<input type="search" id="find" autocomplete="off" spellcheck="false">
</div>
<ul class="game-list" aria-label="Games">{''.join(rows)}</ul>
<div class="no-match" hidden><p>No game matches “<span class="no-match-term"></span>”. {count} games are listed so far.</p><button type="button" class="clear-search">Clear search</button></div>
<section class="how"><h2>How entries are made</h2>
<p>Each entry is written from the game's rulebook: the publisher's own file where it is online, otherwise a copy of it. Every page names the edition, links the file and gives the date it was checked. Anything that could not be read directly from the rulebook is listed at the bottom of the page.</p></section>
</main>"""
    return page(f"{SITE_NAME}: board and card game setup by player count", TAGLINE, body, depth=0, body_class="page-home")


def main():
    check = subprocess.run([sys.executable, str(ROOT / "pipeline" / "validate.py")], capture_output=True, text=True)
    if check.returncode != 0:
        print(check.stdout)
        print("Build stopped: fix the entries above first.")
        return 1
    games = sorted((json.loads(p.read_text(encoding="utf-8")) for p in GAMES.glob("*.json")), key=lambda g: g["name"].lower())
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST / "static")
    (DIST / "index.html").write_text(home_page(games), encoding="utf-8")
    for game in games:
        out = DIST / "games" / game["slug"]
        out.mkdir(parents=True)
        (out / "index.html").write_text(game_page(game), encoding="utf-8")
    print(f"Built {len(games)} game pages and the home page into {DIST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
