# GitPersona

## Overview

GitPersona is a lightweight developer persona and analytics toolkit for GitHub profiles. It fetches public GitHub data on-demand and performs local analysis to produce a concise persona summary and simple stats.

## Install (recommended: virtualenv)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
pip install -e .
```

## Run tests

```bash
.venv/bin/python -m pytest -q
```

## Usage

Command-line:

```bash
gitpersona analyze <username>
# Example:
gitpersona analyze octocat --output octocat.json
```

Python API:

```python
from gitpersona.github_client import GitHubClient
from gitpersona.analysis import analyze_user

client = GitHubClient()
repos = client.fetch_user_repos('octocat')
report = analyze_user('octocat', repos)
```

## Privacy

All processing is local. GitPersona fetches public GitHub data and does not store it permanently.

## Notes

- To increase GitHub API rate limits, set `GITHUB_TOKEN` in your environment:

```bash
export GITHUB_TOKEN=ghp_...
```

- The project uses a minimal `requests`-based client. For larger-scale usage consider hitting GraphQL or adding caching and rate-limit handling.

# GitPersona

Lightweight developer persona and analytics toolkit for GitHub profiles.

Install:

    pip install -r requirements.txt
    pip install .

Usage:

    gitpersona analyze <username>

Or from Python:

    from gitpersona.github_client import GitHubClient
    from gitpersona.analysis import analyze_user

    client = GitHubClient()
    repos = client.fetch_user_repos('octocat')
    report = analyze_user('octocat', repos)

Privacy:

All processing is local. GitPersona fetches public GitHub data and does not store it permanently.

# GitPersona
