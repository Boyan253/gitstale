# gitstale

> List git branches that are already merged or have gone quiet, and delete them safely.

## Why

Every repo accumulates branches. Some were merged a year ago, some were
abandoned after two commits, and `git branch` lists them all in one
undifferentiated wall. `gitstale` sorts them into merged, stale and active.

## Usage

```
python gitstale.py                             # report on the repo here
python gitstale.py -C ../other-repo -b develop
python gitstale.py --days 30                   # stricter staleness
python gitstale.py --delete-merged --dry-run
python gitstale.py --delete-merged
```

## Output

```
merged (4)
  feature/login-rework                 142d  add password reset
  fix/typo-readme                       98d  fix typo
stale (2)
  spike/graphql                        310d  try a schema
active (3)
  feature/billing                        4d  wire up webhook
```

Each line is branch, age of its last commit, and that commit's subject — enough
to decide without checking anything out.

## Deleting

`--delete-merged` uses `git branch -d`, never `-D`. Git refuses to delete
anything that is not actually merged, so the worst case is a refusal, not lost
work. `main`, `master`, `develop`, `release` and the `--base` branch are always
skipped.

Always run with `--dry-run` first.
