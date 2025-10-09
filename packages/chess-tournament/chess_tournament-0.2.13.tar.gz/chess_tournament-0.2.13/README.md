# Chess Tournament Software

![Build Dev](https://gitlab.com/thi26/chess-tournament-software/badges/dev/pipeline.svg)
![PyPI](https://img.shields.io/pypi/v/chess-tournament.svg)

## Table of Contents

- [Overview](#overview)
- [Installation (for users)](#installation-for-users)
- [Usage](#usage)
- [Architecture](#architecture)
- [Developer Setup](#developer-setup)
- [Author](#author)

---

## Overview

Chess Tournament Software is a standalone Python CLI application to manage players and tournaments in a chess club.
Data is stored in JSON files. The app is cross-platform and follows the **Model-View-Controller (MVC)** pattern.

---

## Installation (for users)

You’ll need **Python 3.8+** installed.

To avoid system-level issues (PEP 668, etc.), install the app in a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install chess-tournament
```

---

## Usage

After installation, simply run:

```bash
chess
```

---

## flake8 reports

```bash
make flake8-html
```

or

```bash
flake8 --format=html --htmldir=reports/flake8_report
```

---

## Architecture

Main directories:

controllers/ – business logic (players, matches)

models/ – data structures

views/ – command-line interface

data/ – local JSON storage

main.py – CLI entry point

See Issue #7 – Code Architecture for a full breakdown.

---

## Developer Setup

Want to contribute or run the app locally?
See: [Developer_Setup_instructions.md](Developer_Setup_instructions.md)

---

## Author

@Thi26, OpenClassrooms student
Training: Python Application Developer
