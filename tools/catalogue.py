"""The catalogue of extensions of tensela.com: one file per extension in extensions/<id>.json.

    python tools/catalogue.py entry <the .zip> <its download address>   the file of an extension, from its .zip
    python tools/catalogue.py check [--download]                         every file is right (and, with --download,
                                                                         each .zip is the one its fingerprint says,
                                                                         and its card says the same as its file)
    python tools/catalogue.py build <catalogue.json>                     all of them in one file, for the site

Only the standard library: it runs anywhere, also in the review of each pull request (.github/workflows/check.yml).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ENTRIES = HERE / "extensions"
REQUIRED = ("id", "name", "description", "version", "author", "licence", "tensela", "source", "permissions")
PERMISSIONS = ("network", "files", "programs", "local")
LANGUAGES = ("en", "es")
_ID = re.compile(r"^[a-z][a-z0-9-]{1,39}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


def card_of(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as z:
        cards = [n for n in z.namelist() if n.count("/") <= 1 and n.rpartition("/")[2] == "extension.toml"]
        if len(cards) != 1:
            raise ValueError(f"{archive.name} has no extension.toml (or more than one)")
        return tomllib.loads(z.read(cards[0]).decode("utf-8"))


def in_languages(card: dict, key: str) -> dict:
    out = {"en": str(card.get(key, ""))}
    for lang in LANGUAGES[1:]:
        if card.get(lang, {}).get(key):
            out[lang] = str(card[lang][key])
    return out


def entry(archive: Path, download: str) -> dict:
    """The file of an extension, from its .zip (what the card says) and where it is downloaded."""
    card = card_of(archive)
    permissions = {}
    for key, why in (card.get("permissions") or {}).items():
        permissions[key] = {"en": str(why)}
        for lang in LANGUAGES[1:]:
            said = (card.get(lang, {}).get("permissions") or {}).get(key)
            if said:
                permissions[key][lang] = str(said)
    today = datetime.date.today().isoformat()
    return {"id": card["id"], "name": in_languages(card, "name"), "description": in_languages(card, "description"),
            "version": str(card.get("version", "")), "author": str(card.get("author", "")),
            "licence": str(card.get("licence", "")), "tensela": str(card.get("tensela", "")),
            "permissions": permissions, "website": str(card.get("website", "")),
            "issues": str(card.get("issues", "")), "source": str(card.get("source", "")),
            "download": download, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "comes_with_tensela": False, "added": today, "updated": today}


def problems(data: dict, name: str) -> list[str]:
    found = [f"{name}: it has no «{k}»" for k in REQUIRED if not data.get(k) and data.get(k) != {}]
    if data.get("id") and (not _ID.match(data["id"]) or name != f"{data['id']}.json"):
        found.append(f"{name}: the id must be lowercase letters, digits and «-», and the file <id>.json")
    for key in ("name", "description"):
        if not isinstance(data.get(key), dict) or not data[key].get("en"):
            found.append(f"{name}: «{key}» needs at least its English text ({{\"en\": …}})")
    for key, why in (data.get("permissions") or {}).items():
        if key not in PERMISSIONS:
            found.append(f"{name}: unknown permission «{key}» (they are: {', '.join(PERMISSIONS)})")
        elif not isinstance(why, dict) or not why.get("en"):
            found.append(f"{name}: the permission «{key}» must say why, at least in English")
    for key in ("source", "website", "issues", "download"):
        if data.get(key) and not str(data[key]).startswith("https://"):
            found.append(f"{name}: «{key}» must be an https:// address")
    if not data.get("comes_with_tensela"):
        if not data.get("download"):
            found.append(f"{name}: it has no «download» (the address of its .zip)")
        if not _SHA.match(str(data.get("sha256", ""))):
            found.append(f"{name}: «sha256» must be the 64 hexadecimal digits of the fingerprint of its .zip")
    return found


def check(download: bool) -> int:
    found = []
    for path in sorted(ENTRIES.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            found.append(f"{path.name}: not JSON ({error})")
            continue
        found += problems(data, path.name)
        if download and not data.get("comes_with_tensela") and data.get("download"):
            try:
                with urllib.request.urlopen(data["download"], timeout=60) as answer:
                    content = answer.read(200 * 1024 ** 2)
            except OSError as error:
                found.append(f"{path.name}: its .zip could not be downloaded ({error})")
                continue
            if hashlib.sha256(content).hexdigest() != data.get("sha256"):
                found.append(f"{path.name}: the .zip downloaded is not the one its fingerprint says")
                continue
            archive = HERE / ".download.zip"
            archive.write_bytes(content)
            try:
                card = card_of(archive)
            finally:
                archive.unlink()
            for key in ("id", "version"):
                if str(card.get(key)) != str(data.get(key)):
                    found.append(f"{path.name}: its card says {key} «{card.get(key)}», its file «{data.get(key)}»")
            if sorted(card.get("permissions") or {}) != sorted(data.get("permissions") or {}):
                found.append(f"{path.name}: its card asks for {sorted(card.get('permissions') or {})}, its file says "
                             f"{sorted(data.get('permissions') or {})}")
    for line in found:
        print(line)
    print(f"{len(list(ENTRIES.glob('*.json')))} extensions, {len(found)} problems")
    return 1 if found else 0


def build(target: Path) -> None:
    every = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ENTRIES.glob("*.json"))]
    target.write_text(json.dumps({"extensions": every}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(every)} extensions → {target}")


def main(argv: list[str]) -> int:
    if argv[:1] == ["entry"] and len(argv) == 3:
        print(json.dumps(entry(Path(argv[1]), argv[2]), ensure_ascii=False, indent=2))
        return 0
    if argv[:1] == ["check"]:
        return check("--download" in argv)
    if argv[:1] == ["build"] and len(argv) == 2:
        build(Path(argv[1]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
