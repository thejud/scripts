#!/usr/bin/env python
"""
migration script for the atuin shell history tool
to fix imported ~/.persistent-history commands that include metadata.

I loaded my existing shell history into into the atuin sqlite db via:
    HISTFILE=~/.persistent_history atuin import bash

Sample command formats are like:
#   date       time       pid   command                          optional-working-directory
    2020-04-20 12:01:27   946 | vi /Users/jdagnall/.bash_profile
    2020/04/20 12:01:29   946 | vi /Users/jdagnall/.bash_profile
    2020-04-20 12:01:30  1946 | vi /Users/jdagnall/.bash_profile [PWD /Users/jdagnall]

However, although atui extracts the dates correctly, it doesn't understand the
metadata format and so adds the whole line into the history. This script will
look for commands that match the above patterns, and then:

    1. extract the pid into the session id
    2. Extract the [PWD ] portion if present into the cwd field, or set to 'unknown'
    3. remove everything before the command, and the working directory section
    4. update the session

"""


import argparse
import re
import sqlite3
import sys

def process_command(command):
    # Regular expression to match the required patterns:
    #  2020-04-20 12:01:27   946 | vi /Users/jdagnall/.bash_profile
    #  2020/04/20 12:01:29   946 | vi /Users/jdagnall/.bash_profile
    #  2020-04-20 12:01:30  1946 | vi /Users/jdagnall/.bash_profile [PWD /Users/jdagnall]

    pattern = r'(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2})\s+(\d+)\s+\|\s+(.+?)( \[PWD (.+)\])?$'
    match = re.match(pattern, command)

    if match:
        date_time = match.group(1)
        pid = match.group(2)
        cmd = match.group(3).strip()
        cwd = match.group(5) if match.group(5) else 'unknown'

        return pid, cmd, cwd

    return None, None, None

def update_database(db_path, dry_run=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to select all rows
    cursor.execute("SELECT id, command FROM history")
    rows = cursor.fetchall()

    for row in rows:
        command_id = row[0]
        command = row[1]

        pid, cmd, cwd = process_command(command)

        if pid and cmd:
            # Update the command, session, and cwd fields
            print(f"FIXED: {pid} ## {cmd} ## {cwd}")
            if dry_run:
                continue
            cursor.execute("""
                UPDATE history
                SET command = ?, session = ?, cwd = ?
                WHERE id = ?
            """, (cmd, pid, cwd, command_id))
        else:
            print(f"skipping: {command}")

    conn.commit()
    conn.close()

def parse_args():
    desc = "clean up atuin commands imported from .persistent_history"
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('-n', '--dry-run', action='store_true', help='dry run')
    p.add_argument('dbfile', help='sqlite3 database file to update')
    return p.parse_args()

if __name__ == "__main__":
    opts = parse_args()
    update_database(opts.dbfile, opts.dry_run)
