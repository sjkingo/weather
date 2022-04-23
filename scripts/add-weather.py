#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import pytz
import subprocess


REPO_PATH = os.path.expanduser("~/.weather-script")
DATA_PATH = os.path.join(REPO_PATH, "data", "weather.json")
TZ = "Australia/Brisbane"


def run(args):
    return subprocess.run(args, cwd=REPO_PATH, check=True)

def update_json(args):
    timestamp = pytz.timezone(TZ).localize(datetime.datetime.now()).isoformat()
    print(timestamp, args)

    # Ensure the data is up to date. This will abort if tree is dirty
    if not args.dry_run:
        run(["git", "checkout", "web"])
        run(["git", "pull"])

    # Read json, append to it, and write it out. Do this in 2 steps as we want to override the file.
    with open(DATA_PATH, "r") as fp:
        data = json.load(fp)
    data.append({
        "timestamp": timestamp,
        "rain": args.rain,
    })
    if not args.dry_run:
        with open(DATA_PATH, "w") as fp:
            json.dump(data, fp, indent=2)
    else:
        from pprint import pprint
        pprint(data)

    # Commit and push
    if not args.dry_run:
        run(["git", "add", DATA_PATH])
        run(["git", "commit", "-m", f"add-weather.py update at {timestamp}"])
        run(["git", "push"])

def main():
    parser = argparse.ArgumentParser(description="Add a weather entry")
    parser.add_argument("--rain", required=True, type=int, help="Rain since last measurement in mm")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update or perform any destructive operations")
    args = parser.parse_args()
    update_json(args)


if __name__ == "__main__":
    main()