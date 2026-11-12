#!/usr/bin/env python3
"""Validate every game entry against data/schema.json plus consistency rules.

Uses only the standard library, so it runs anywhere the build runs.
Exit code 0 means every entry is valid.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))


def check(value, schema, path, errors):
    """Minimal JSON Schema checker covering the keywords schema.json uses."""
    if "$ref" in schema:
        schema = SCHEMA["$defs"][schema["$ref"].split("/")[-1]]
    for sub in schema.get("allOf", []):
        check(value, sub, path, errors)
    if "oneOf" in schema:
        matches = 0
        for sub in schema["oneOf"]:
            trial = []
            check(value, sub, path, trial)
            matches += not trial
        if matches != 1:
            errors.append(f"{path}: must match exactly one allowed shape")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    kind = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int}
    if kind and (not isinstance(value, types[kind]) or isinstance(value, bool)):
        errors.append(f"{path}: expected {kind}")
        return
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, int) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        for i, item in enumerate(value):
            check(item, schema.get("items", {}), f"{path}[{i}]", errors)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing '{key}'")
        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{path}: needs at least {schema['minProperties']} key(s)")
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key, item in value.items():
            if key in props:
                check(item, props[key], f"{path}.{key}", errors)
            elif any(re.search(p, key) for p in patterns):
                for p, sub in patterns.items():
                    if re.search(p, key):
                        check(item, sub, f"{path}.{key}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key '{key}'")


def consistency(game, path, errors):
    """Rules a schema cannot express."""
    players = game.get("players", {})
    lo, hi, covered = players.get("min"), players.get("max"), players.get("covered", [])
    if isinstance(lo, int) and isinstance(hi, int):
        if lo > hi:
            errors.append(f"{path}: players.min is greater than players.max")
        for n in covered:
            if not lo <= n <= hi:
                errors.append(f"{path}: covered count {n} is outside {lo}-{hi}")
    if path.stem != game.get("slug"):
        errors.append(f"{path}: file name must match slug '{game.get('slug')}'")

    def counts(where, mapping):
        missing = [n for n in covered if str(n) not in mapping]
        extra = [k for k in mapping if int(k) not in covered]
        if missing:
            errors.append(f"{path}: {where} has no value for player count(s) {missing}")
        if extra:
            errors.append(f"{path}: {where} lists count(s) {extra} that are not covered")

    for i, number in enumerate(game.get("key_numbers", [])):
        if isinstance(number.get("value"), dict):
            counts(f"key_numbers[{i}]", number["value"])
    for section in ("setup", "scoring", "missed"):
        for i, item in enumerate(game.get(section, [])):
            if "by_count" in item:
                counts(f"{section}[{i}].by_count", item["by_count"])
            for n in item.get("only", []):
                if n not in covered:
                    errors.append(f"{path}: {section}[{i}].only names uncovered count {n}")
    if game.get("status") == "complete" and game.get("not_covered") and not covered:
        errors.append(f"{path}: complete entries need at least one covered count")


def main():
    files = sorted((ROOT / "data" / "games").glob("*.json"))
    failed = 0
    for path in files:
        errors = []
        try:
            game = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"FAIL {path.name}: not valid JSON ({exc})")
            failed += 1
            continue
        check(game, SCHEMA, path.name, errors)
        consistency(game, path, errors)
        if errors:
            failed += 1
            print(f"FAIL {path.name}")
            for line in errors:
                print(f"   {line}")
        else:
            print(f"ok   {path.name}")
    print(f"{len(files) - failed} of {len(files)} entries valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
