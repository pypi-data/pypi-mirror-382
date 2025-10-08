"""Simple GitHub API client used by GitPersona."""

import os
import requests
from typing import List, Dict, Any


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        self.base = "https://api.github.com"

    def fetch_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """Fetch public repos for a user. Returns a list of repo JSON objects."""
        repos = []
        url = f"{self.base}/users/{username}/repos"
        params = {"per_page": 100, "type": "owner", "sort": "pushed"}
        while url:
            r = self.session.get(url, params=params)
            if r.status_code == 404:
                raise ValueError(f"User {username} not found")
            r.raise_for_status()
            page = r.json()
            repos.extend(page)
            # pagination
            if "next" in r.links:
                url = r.links["next"]["url"]
                params = None
            else:
                url = None
        return repos
