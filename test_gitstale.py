import gitstale

NOW = 1_700_000_000
DAY = 86400


def test_parse_branches():
    raw = "feature/a\x1f%d\x1fadd thing\n" % NOW
    assert gitstale.parse_branches(raw) == [("feature/a", NOW, "add thing")]

def test_parse_branches_ignores_blank_lines():
    assert gitstale.parse_branches("\n\n") == []


def test_age_days():
    assert round(gitstale.age_days(NOW - 3 * DAY, now=NOW)) == 3

def test_classify_puts_merged_first():
    branches = [("feature/a", NOW, "x")]
    groups = gitstale.classify(branches, {"feature/a"}, "main", 90, now=NOW)
    assert [n for n, _, _ in groups["merged"]] == ["feature/a"]


def test_classify_marks_old_branches_stale():
    branches = [("old", NOW - 200 * DAY, "x")]
    groups = gitstale.classify(branches, set(), "main", 90, now=NOW)
    assert [n for n, _, _ in groups["stale"]] == ["old"]

def test_classify_keeps_recent_branches_active():
    branches = [("fresh", NOW - DAY, "x")]
    groups = gitstale.classify(branches, set(), "main", 90, now=NOW)
    assert [n for n, _, _ in groups["active"]] == ["fresh"]


def test_protected_branches_are_skipped():
    branches = [("main", NOW - 500 * DAY, "x")]
    groups = gitstale.classify(branches, set(), "main", 90, now=NOW)
    assert groups["merged"] == [] and groups["stale"] == []
