"""Command-line interface for GitPersona."""

import argparse
import os
import sys
from .github_client import GitHubClient
from .analysis import analyze_user


def build_parser():
    p = argparse.ArgumentParser(
        prog="gitpersona", description="Analyze a GitHub user's persona and stats"
    )
    sub = p.add_subparsers(dest="cmd")

    analyze = sub.add_parser("analyze", help="Analyze a GitHub username")
    analyze.add_argument("username", help="GitHub username to analyze")
    analyze.add_argument("--output", "-o", help="Write JSON output to file")

    return p


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "analyze":
        token = os.environ.get("GITHUB_TOKEN")
        client = GitHubClient(token=token)
        data = client.fetch_user_repos(args.username)
        result = analyze_user(args.username, data)
        import json

        text = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(text)
            print(f"Wrote analysis to {args.output}")
        else:
            print(text)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
