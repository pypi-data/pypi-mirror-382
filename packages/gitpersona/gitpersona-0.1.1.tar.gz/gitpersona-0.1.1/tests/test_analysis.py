from gitpersona.analysis import analyze_user
from datetime import datetime, timezone


def make_repo(name, lang, pushed_at, stars=0, forks=0):
    return {
        "name": name,
        "language": lang,
        "pushed_at": pushed_at.isoformat().replace("+00:00", "Z"),
        "stargazers_count": stars,
        "forks_count": forks,
    }


def test_analyze_basic():
    now = datetime(2025, 10, 8, 23, 30, tzinfo=timezone.utc)
    repos = [
        make_repo("a", "Python", now, stars=5),
        make_repo("b", "Python", now, stars=2),
        make_repo("c", "JavaScript", now, stars=0),
    ]
    res = analyze_user("alice", repos)
    assert res["username"] == "alice"
    assert res["total_repos"] == 3
    assert any(item["language"] == "Python" for item in res["top_languages"])
    assert res["stars"] == 7
