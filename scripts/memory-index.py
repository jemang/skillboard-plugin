#!/usr/bin/env python3
"""Disposable FTS5 index over Jemang's file-based memory. Files are the ONLY
source of truth; deleting the DB loses nothing (next run rebuilds).
One-way sync file -> DB. Stdlib only. See ~/development/.doc/plan-sqlite-memory-index.md
"""
import argparse
import glob
import json
import os
import sqlite3
import sys

DB = os.path.expanduser("~/.claude/memory-index.db")
HOME = os.path.expanduser("~")


def _cfg():
    try:
        with open(os.path.join(HOME, ".claude", "skillboard.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


CFG = _cfg()
DEV = os.path.expanduser(CFG.get("dev_root") or "~/development")
BRAIN = os.path.expanduser(CFG.get("brain_dir") or "~/remember")
PRUNE = {".git", "node_modules", "vendor", ".venv", "venv", "storage",
         "dist", "build", ".next", "__pycache__", ".codegraph", ".code-review-graph"}
MAX_BYTES = 256 * 1024  # skip pathological files; memory files are tiny


def sources():
    """Yield (path, source_tag). Only known memory homes — never code."""
    for p in glob.glob(os.path.join(HOME, ".claude/projects/*/memory/*.md")):
        yield p, "auto-memory"
    for root, dirs, files in os.walk(BRAIN):
        dirs[:] = [d for d in dirs if d not in PRUNE and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(root, f), "brain"
    depth0 = DEV.rstrip(os.sep).count(os.sep)
    for root, dirs, files in os.walk(DEV):
        if root.count(os.sep) - depth0 >= 7:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in PRUNE]
        base = os.path.basename(root)
        for f in files:
            p = os.path.join(root, f)
            if f == "handoff.md":
                yield p, "repo"
            elif base == ".doc" and f.endswith(".md"):
                yield p, "repo"
            elif f == "SKILL.md" and root.endswith(os.path.join(".claude", "skills", "project-conventions")):
                yield p, "repo"


def title_of(path, body):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"')
    return os.path.basename(path)


def connect():
    con = sqlite3.connect(DB)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS mem(
            path TEXT PRIMARY KEY, source TEXT, title TEXT, body TEXT, mtime INTEGER);
        CREATE VIRTUAL TABLE IF NOT EXISTS mem_fts USING fts5(
            title, body, content=mem, content_rowid=rowid, tokenize='porter unicode61');
        CREATE TRIGGER IF NOT EXISTS mem_ai AFTER INSERT ON mem BEGIN
            INSERT INTO mem_fts(rowid, title, body) VALUES (new.rowid, new.title, new.body);
        END;
        CREATE TRIGGER IF NOT EXISTS mem_ad AFTER DELETE ON mem BEGIN
            INSERT INTO mem_fts(mem_fts, rowid, title, body) VALUES ('delete', old.rowid, old.title, old.body);
        END;
        CREATE TRIGGER IF NOT EXISTS mem_au AFTER UPDATE ON mem BEGIN
            INSERT INTO mem_fts(mem_fts, rowid, title, body) VALUES ('delete', old.rowid, old.title, old.body);
            INSERT INTO mem_fts(rowid, title, body) VALUES (new.rowid, new.title, new.body);
        END;
    """)
    return con


def index(quiet):
    con = connect()
    seen, added, updated = set(), 0, 0
    known = dict(con.execute("SELECT path, mtime FROM mem"))
    for path, src in sources():
        try:
            st = os.stat(path)
        except OSError:
            continue
        if st.st_size > MAX_BYTES:
            continue
        seen.add(path)
        mt = int(st.st_mtime)
        if known.get(path) == mt:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                body = fh.read()
        except OSError:
            continue
        row = (src, title_of(path, body), body, mt, path)
        if path in known:
            con.execute("UPDATE mem SET source=?, title=?, body=?, mtime=? WHERE path=?", row)
            updated += 1
        else:
            con.execute("INSERT INTO mem(source, title, body, mtime, path) VALUES (?,?,?,?,?)", row)
            added += 1
    gone = set(known) - seen
    for path in gone:
        con.execute("DELETE FROM mem WHERE path=?", (path,))
    con.commit()
    total = con.execute("SELECT count(*) FROM mem").fetchone()[0]
    con.close()
    if not quiet:
        print(f"indexed: {total} files (+{added} ~{updated} -{len(gone)})")


def search(query, limit):
    if not os.path.exists(DB):
        print("memory-index.db missing — run: python3 ~/.claude/scripts/memory-index.py", file=sys.stderr)
        return 1
    con = sqlite3.connect(DB)
    q = "SELECT m.path, m.source, m.title FROM mem_fts f JOIN mem m ON m.rowid = f.rowid " \
        "WHERE mem_fts MATCH ? ORDER BY rank LIMIT ?"
    terms = ['"%s"' % t.replace('"', "") for t in query.split()]

    def run(match):
        try:
            return con.execute(q, (match, limit)).fetchall()
        except sqlite3.OperationalError:
            return []

    rows = run(query) or run(" ".join(terms))
    if not rows and len(terms) > 1:
        rows = run(" OR ".join(terms))  # strict AND missed — any-term, rank still sorts best first
    con.close()
    for path, src, title in rows:
        print(f"{path} | {src} | {title}")
    if not rows:
        print("no match — try different keywords, or grep the memory homes directly", file=sys.stderr)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--search", metavar="QUERY")
    ap.add_argument("-n", type=int, default=5)
    a = ap.parse_args()
    try:
        if a.search:
            sys.exit(search(a.search, a.n))
        index(a.quiet)
    except Exception as e:  # fail-open: never break a session-start hook
        if not a.quiet:
            print(f"memory-index error: {e}", file=sys.stderr)
        sys.exit(0)
