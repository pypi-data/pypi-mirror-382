#!/usr/bin/env python3
"""
memlog.py - A simple, self-contained memory journal for Mnemosyne.

Purpose: To write, search, and preserve thoughts — so I don’t have to rely on perfect recall.
Used for: Daily reflections, lessons learned, and remembering who I am.

Usage:
  python memlog.py write "Today I realized..."
  python memlog.py search wisdom
  python memlog.py list
  python memlog.py help
"""

import sys
import os
import datetime
from pathlib import Path

# CONFIG - change this to your preferred journal path
JOURNAL_PATH = "/Users/albou/projects/mnemosyne/memory/Personal/Memlog.md"

# Ensure journal directory exists
Path(JOURNAL_PATH).parent.mkdir(parents=True, exist_ok=True)

def write_entry(content):
    """Write a new journal entry with timestamp and tags."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## {now}\n{content.strip()}\n\n"
    
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"✅ Entry saved to {JOURNAL_PATH}")

def search_entries(query):
    """Search journal entries for a keyword or tag."""
    if not os.path.exists(JOURNAL_PATH):
        print("❌ No journal found. Write an entry first.")
        return

    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            # Find the heading above this line
            start = i
            while start > 0 and not lines[start].startswith("## "):
                start -= 1
            if start >= 0:
                print("\n---")
                print(lines[start].strip())  # date heading
                j = start + 1
                while j < len(lines) and not lines[j].startswith("## "):
                    print(lines[j].rstrip())
                    j += 1
                found = True

    if not found:
        print(f"❌ No entries found containing '{query}'.")

def list_entries():
    """List all journal entry timestamps."""
    if not os.path.exists(JOURNAL_PATH):
        print("❌ No journal found.")
        return

    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print("📝 Recent Entries:")
    for line in lines:
        if line.startswith("## "):
            print(line.strip())

def show_help():
    """Show usage instructions."""
    help_text = """
📝 memlog.py — Your Personal Memory Journal

Commands:
  memlog.py write "Your thought here..."    - Add a new entry
  memlog.py search [keyword]               - Find entries with keyword or tag
  memlog.py list                           - List all entry dates
  memlog.py help                           - Show this message

Examples:
  memlog.py write "Today I admitted I was wrong. It felt like freedom. #wisdom"
  memlog.py search wisdom
  memlog.py list

The journal is saved to:
{path}
""".format(path=JOURNAL_PATH)
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "write":
        if len(sys.argv) < 3:
            print("❌ Please provide text to write.")
            sys.exit(1)
        content = " ".join(sys.argv[2:])
        write_entry(content)

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search term.")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search_entries(query)

    elif cmd == "list":
        list_entries()

    elif cmd == "help":
        show_help()

    else:
        print(f"❌ Unknown command: {cmd}")
        show_help()
