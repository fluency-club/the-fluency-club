#!/usr/bin/env python3
"""Copy an unchanged HTML file, commit it, and publish it on main."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REMOTE_URLS = {
    "https://github.com/fluency-club/the-fluency-club.git",
    "https://github.com/fluency-club/the-fluency-club",
    "git@github.com:fluency-club/the-fluency-club.git",
}


def git(*args):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True
    ).strip()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to the original HTML file")
    parser.add_argument("short_name", help="Lowercase name, e.g. future or past-simple")
    args = parser.parse_args()

    require(
        re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.short_name),
        "Use lowercase letters, numbers, and single hyphens for the short name.",
    )
    source = args.source.expanduser().resolve()
    require(source.is_file() and source.suffix.lower() == ".html",
            "Source must be an existing .html file.")
    relative = f"homework/{args.short_name}.html"
    destination = ROOT / relative
    require(destination.parent.is_dir() and not destination.parent.is_symlink(),
            "The repository must contain a regular homework directory.")
    require(not destination.exists() and not destination.is_symlink(),
            f"Refusing to overwrite {relative}.")
    require(git("branch", "--show-current") == "main", "Switch to main first.")
    require(not git("status", "--porcelain", "--untracked-files=all"),
            "The working tree must be clean. Commit or set aside existing changes first.")
    for direction in ([], ["--push"]):
        urls = git("remote", "get-url", *direction, "--all", "origin").splitlines()
        require(len(urls) == 1 and urls[0] in REMOTE_URLS,
                "origin must point only to fluency-club/the-fluency-club on GitHub.")

    # Do not accidentally publish other local commits or work from an old main.
    git("fetch", "origin", "refs/heads/main")
    require(git("rev-parse", "HEAD") == git("rev-parse", "FETCH_HEAD"),
            "Local main must match GitHub main exactly. Synchronize it first.")
    require(not git("check-attr", "--all", "--", relative),
            "Git attributes apply to this file and could change its contents.")

    original = source.read_bytes()
    with destination.open("xb") as output:
        output.write(original)
    # --no-filters prevents line-ending conversion and clean filters.
    blob = git("hash-object", "-w", "--no-filters", "--", relative)
    git("update-index", "--add", "--cacheinfo", f"100644,{blob},{relative}")
    require(git("diff", "--cached", "--name-only").splitlines() == [relative],
            "Unexpected staged files. Stopping before committing.")
    git("commit", "-m", f"Add {args.short_name} homework")
    committed = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"HEAD:{relative}"]
    )
    require(committed == original and destination.read_bytes() == original,
            "HTML bytes changed during commit. Stopping before pushing.")
    require(git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD") == relative,
            "The commit includes unexpected files. Stopping before pushing.")
    git("push", "origin", "HEAD:refs/heads/main")
    print(f"https://fluency-club.github.io/the-fluency-club/{relative}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Publishing stopped: {error}", file=sys.stderr)
        print("Any files or commits already created are kept for inspection.", file=sys.stderr)
        sys.exit(1)
