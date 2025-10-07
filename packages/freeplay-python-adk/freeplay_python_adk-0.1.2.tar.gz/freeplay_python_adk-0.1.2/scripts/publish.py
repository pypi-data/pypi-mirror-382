#!/usr/bin/env -S uv run --script
#
# /// script
# dependencies = ["httpx"]
# ///

import subprocess
from pathlib import Path

import httpx


def main():
    branch = (
        subprocess.run(
            ["git", "branch", "--show-current"], check=True, capture_output=True
        )
        .stdout.strip()
        .decode("utf-8")
    )
    if branch != "main":
        print("Skipping unnecessary publish for branch %s.", branch)
        return

    with Path("pyproject.toml").open("r") as f:
        pyproject_toml = f.read()
    repo_version = pyproject_toml.split("version = ")[1].split("\n")[0].strip('"')

    response = httpx.get("https://pypi.org/pypi/freeplay-python-adk/json")
    releases = response.json()["releases"]

    if repo_version in releases:
        print("Skipping unnecessary publish.")
        return

    print(f"Publishing new version {repo_version}")
    subprocess.run(["uv", "build"], check=True)
    subprocess.run(["uv", "publish"], check=True)


main()
