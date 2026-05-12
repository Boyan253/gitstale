import gitstale

NOW = 1_700_000_000
DAY = 86400


def test_parse_branches():
    raw = "feature/a\x1f%d\x1fadd thing\n" % NOW
    assert gitstale.parse_branches(raw) == [("feature/a", NOW, "add thing")]

def test_parse_branches_ignores_blank_lines():
    assert gitstale.parse_branches("\n\n") == []
