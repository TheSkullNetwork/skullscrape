# Contributing to SkullScrape

First off, thank you for considering contributing to SkullScrape! It's contributions like yours that make open-source security tools awesome.

## 🚀 How Can I Contribute?

### 1. Reporting Bugs
Before creating a bug report, please check existing issues to see if it has already been reported. When creating an issue, include:
* Your operating system and Python version.
* The exact command or steps to reproduce the issue.
* Expected vs. actual behavior (along with error logs/stack traces).

### 2. Requesting Features
Feature requests are welcome! Please clearly describe:
* The problem the feature solves.
* How you envision the feature working in the script.

### 3. Pull Requests
1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name

2. Keep code single-file compliant (all core logic should reside in `scraper.py`).
3. Ensure no unnecessary external dependencies are introduced (prefer standard library or lightweight modules).
4. Commit your changes with clear, descriptive commit messages.
5. Push to your fork and submit a Pull Request targeting the `main` branch.

## 🎨 Code Style & Guidelines

* **Formatting:** Follow standard [PEP 8](https://peps.python.org/pep-0008/) conventions.
* **Terminal Output:** Use `rich` formatting consistent with the existing UI theme.
* **Compatibility:** Ensure code works across Windows PowerShell/CMD, macOS, and Linux UTF-8 environments.
