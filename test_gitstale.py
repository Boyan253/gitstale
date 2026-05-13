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
