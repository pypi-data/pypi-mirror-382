"""Analysis utilities for GitPersona."""

from collections import Counter
from datetime import datetime
from typing import List, Dict, Any


def analyze_user(username: str, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute basic stats from a list of repo JSON objects from GitHub API.

    Returns a dict with summaries and a short persona string.
    """
    total_repos = len(repos)
    languages = Counter()
    stars = 0
    forks = 0
    pushes_by_hour = Counter()
    recent_activity = []

    for r in repos:
        lang = r.get("language") or "Unknown"
        languages[lang] += 1
        stars += r.get("stargazers_count", 0) or 0
        forks += r.get("forks_count", 0) or 0
        pushed = r.get("pushed_at")
        if pushed:
            try:
                dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                pushes_by_hour[dt.hour] += 1
                recent_activity.append(dt)
            except Exception:
                pass

    top_languages = languages.most_common(5)

    persona = _derive_persona(total_repos, languages, pushes_by_hour)
    summary = {
        "username": username,
        "total_repos": total_repos,
        "top_languages": [{"language": k, "count": v} for k, v in top_languages],
        "stars": stars,
        "forks": forks,
        "pushes_by_hour": dict(pushes_by_hour),
        "persona": persona,
    }
    return summary


def _derive_persona(
    total_repos: int, languages: Counter, pushes_by_hour: Counter
) -> str:
    """Very simple heuristic rules to produce a persona label."""
    if not languages:
        return "Observer"

    top_lang, top_count = languages.most_common(1)[0]
    night_activity = sum(v for h, v in pushes_by_hour.items() if h >= 22 or h < 6)
    day_activity = sum(v for h, v in pushes_by_hour.items() if 9 <= h <= 18)

    tags = []
    if night_activity > day_activity:
        tags.append("Night Owl")
    else:
        tags.append("Daytime Coder")

    if total_repos >= 50:
        tags.append("Prolific Repo Creator")
    elif total_repos >= 10:
        tags.append("Seasoned Maintainer")

    if top_lang and top_lang != "Unknown":
        tags.append(f"{top_lang} Enthusiast")

    if top_count >= 3 and total_repos > 0:
        tags.append("Focused")

    return ", ".join(tags) if tags else "Balanced"
