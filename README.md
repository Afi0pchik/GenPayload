# GenPayload Tool

A CLI tool to clone and browse the [SecLists](https://github.com/danielmiessler/SecLists) repository locally, select and merge payload wordlists, and manage custom wordlists easily with an interactive interface and progress feedback.

---

## Features

- Clone or update the SecLists repository with a rich progress bar.
- Interactive browsing of the SecLists directory structure to select payload files.
- Merge multiple selected wordlist files into a single combined list.
- Upload your own custom wordlist file to replace the merged list.
- Merge two local wordlist files with an interactive file selection interface.
- Clean, colorful terminal output with rich tables, prompts, and panels.

---

## Requirements

- Python 3.0+
- requirments.txt

---

## Installation

Use the provided setup script for an easy setup:

```bash
chmod +x setup.sh
./setup.sh
python3 genpayload.py 
