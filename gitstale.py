#!/usr/bin/env python3
"""Find git branches that are merged or stale, and optionally delete them."""

import argparse
import subprocess
import sys
import time

PROTECTED = {"main", "master", "develop", "release", "HEAD"}


def git(*args, cwd=None):
    proc = subprocess.run(["git"] + list(args), cwd=cwd, text=True,
                          capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or "").strip() or "git failed")
    return proc.stdout


def parse_branches(output):
    """Parse `git for-each-ref` output into (name, timestamp, subject) tuples."""
    rows = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) < 3:
            continue
        name, stamp, subject = parts[0], parts[1], parts[2]
        rows.append((name.strip(), int(stamp), subject.strip()))
    return rows


def list_branches(cwd=None):
    out = git("for-each-ref", "--format=%(refname:short)\x1f%(committerdate:unix)\x1f%(subject)",
              "refs/heads/", cwd=cwd)
    return parse_branches(out)


def merged_into(base, cwd=None):
    out = git("branch", "--merged", base, "--format=%(refname:short)", cwd=cwd)
    return {line.strip() for line in out.splitlines() if line.strip()}


def age_days(timestamp, now=None):
    now = time.time() if now is None else now
    return (now - timestamp) / 86400.0


def classify(branches, merged, base, days, now=None, protected=PROTECTED):
    """Split branches into (merged, stale, active)."""
    out = {"merged": [], "stale": [], "active": []}
    for name, stamp, subject in branches:
        if name in protected or name == base:
            continue
        age = age_days(stamp, now)
        record = (name, age, subject)
        if name in merged:
            out["merged"].append(record)
        elif age >= days:
            out["stale"].append(record)
        else:
            out["active"].append(record)
    for key in out:
        out[key].sort(key=lambda r: -r[1])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-C", "--repo", default=".", help="repository path")
    ap.add_argument("-b", "--base", default="main", help="branch things are merged into")
    ap.add_argument("--days", type=int, default=90, help="a branch is stale after this many days")
    ap.add_argument("--delete-merged", action="store_true",
                    help="delete the merged branches (git branch -d)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    try:
        branches = list_branches(args.repo)
        merged = merged_into(args.base, args.repo)
    except RuntimeError as exc:
        print("gitstale: %s" % exc, file=sys.stderr)
        return 2

    groups = classify(branches, merged, args.base, args.days)
    for label in ("merged", "stale", "active"):
        rows = groups[label]
        if not rows:
            continue
        print("%s (%d)" % (label, len(rows)))
        for name, age, subject in rows:
            print("  %-34s %5.0fd  %s" % (name, age, subject[:50]))

    if args.delete_merged:
        for name, _age, _subject in groups["merged"]:
            if args.dry_run:
                print("would delete %s" % name)
                continue
            try:
                git("branch", "-d", name, cwd=args.repo)
                print("deleted %s" % name)
            except RuntimeError as exc:
                print("could not delete %s: %s" % (name, exc), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
