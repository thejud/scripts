#!/usr/bin/env python3

"""
gcauto.py: Generate git commit messages using Claude AI

This command-line tool helps automate the process of writing git commit messages by leveraging Claude AI (via the 'claude' CLI). It inspects the staged git changes and generates either a concise commit title or a full commit message, depending on the provided arguments.

Features:
    - Automatically checks for staged files before proceeding
    - Extracts ticket IDs from branch names (e.g., ABC-123) and prefixes commit messages
    - Generates contextually appropriate commit messages based on git diff

Usage:
    python gcauto.py           # Generate a full commit message and commit
    python gcauto.py -s        # Generate a short commit title and commit

Arguments:
    -s, --short   Generate a short commit title instead of a full message

Requirements:
    - The 'claude' CLI must be installed and accessible in your PATH.
    - You must have staged changes in your git repository.

Branch naming:
    If your branch starts with a ticket ID pattern (e.g., ABC-123-feature-name),
    the commit message will be automatically prefixed with the ticket ID.

On success, the tool prints the generated message to stderr and runs 'git commit -m <message>'.
"""

import subprocess
import sys
import argparse
import re

# File-level constants for prompts
SHORT_PROMPT = """Look at the staged git changes and create a summarizing git title.
Only respond with the title and no affirmation.
If there are no changes, respond with the empty string."""

FULL_PROMPT = """Look at the staged git changes and create a summarizing git commit message.
Keep the title short and concise.
Do not include mention of claude or anthropic.
Only respond with the message and no affirmation.
If there are no stagged changes, respond with the empty string."""

def check_staged_files():
    """Check if there are any staged files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def get_ticket_id_from_branch():
    """Extract ticket ID from current git branch name if it matches pattern."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        branch_name = result.stdout.strip()
        
        # Check if branch starts with ticket pattern (e.g., ABC-123)
        match = re.match(r'^([A-Z]+)-([0-9]+)', branch_name)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        return None
    except subprocess.CalledProcessError:
        return None

def get_commit_message(short_mode=False):
    """Get commit message from Claude AI based on staged changes."""
    prompt = SHORT_PROMPT if short_mode else FULL_PROMPT
    
    try:
        result = subprocess.run(
            ['claude', '--model', 'sonnet', '-p', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running claude: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Generate git commit messages using Claude AI')
    parser.add_argument('-s', '--short', action='store_true', 
                        help='Generate a short commit title instead of a full message')
    args = parser.parse_args()
    
    # Check for staged files first
    if not check_staged_files():
        print("Error: No staged files found. Please stage some changes before running gcauto.", file=sys.stderr)
        sys.exit(1)
    
    msg = get_commit_message(short_mode=args.short)
    
    if msg:
        # Check for ticket ID and prefix if found
        ticket_id = get_ticket_id_from_branch()
        if ticket_id:
            msg = f"{ticket_id}: {msg}"
        
        print(msg, file=sys.stderr)
        try:
            subprocess.run(['git', 'commit', '-m', msg], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error committing: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()