# SkullScrape

> **Fast, Lightweight, and Autonomous Contact & Link Intelligence Extractor**

SkullScrape is a single-file OSINT tool built to quickly discover emails, phone numbers, social media profiles, and external links from target web pages. Featuring a zero-setup dependency bootstrapper and automatic GitHub updates, it requires zero manual setup.

---

## 🌟 Key Features

- 🚀 **Zero-Setup Bootstrapper:** Automatically detects and installs required dependencies (`requests`, `beautifulsoup4`, `rich`) on launch—no `requirements.txt` or manual `pip` commands required.
- 🔄 **Autonomous GitHub Updates:** Syncs with the main GitHub branch on startup to fetch and install new script revisions seamlessly.
- 🌐 **Pre-Flight Connectivity Test:** Verifies active internet connectivity prior to executing network requests to avoid hanging processes.
- 🛡️ **Robust Input Sanitization:** Performs TLD and domain validation with continuous fallback prompts on malformed inputs.
- 📊 **Flexible Data Export:** Exports extracted intelligence directly into structured `.log`, `.csv`, or `.json` formats.
- 🖥️ **Cross-Platform Compatibility:** Configured with forced UTF-8 standard output for full rendering on Windows PowerShell/CMD, macOS, and Linux terminals.
- ⚡ **Pipeline-Ready Quiet Mode (`-q`):** Disables interactive UI elements and outputs raw JSON to stdout for easy integration into automation workflows and tools like `jq`.

---

## ⚙️ Installation

Clone the repository and run the script directly. Missing packages will install automatically upon execution.

```bash
git clone https://github.com/theskullnetwork/skullscrape.git
cd skullscrape
python scraper.py

```

*(Optional)* Grant execution permissions on Linux/macOS:

```bash
chmod +x scraper.py

```

---

## 💻 Usage & Examples

### Interactive Mode

Launch without parameters to enter the interactive console:

```bash
python scraper.py

```

### Command Line Interface (CLI)

Run non-interactively using standard flags for CI/CD pipelines or scripts:

```bash
# Basic single-target scan
python scraper.py -u example.com

# Auto-save scan output to CSV without interactive prompts
python scraper.py -u example.com --save -f csv

# Silent mode outputting clean JSON to stdout
python scraper.py -u example.com -q

# Run without checking for GitHub script updates
python scraper.py -u example.com --no-update

```

---

## 🚩 Command-Line Arguments

| Short Flag | Long Flag | Description |
| --- | --- | --- |
| `-u` | `--url` | Target URL (bypasses interactive prompt) |
| `-f` | `--format` | Output file format: `log`, `json`, `csv` *(Default: `log`)* |
|  | `--save` | Auto-save output files without user prompting |
| `-q` | `--quiet` | Suppress terminal UI and output raw JSON to stdout |
|  | `--no-update` | Bypass automatic GitHub release checks on launch |
| `-h` | `--help` | Display full help documentation and exit |

---

## 📁 Output Directory Structure

Scan logs are sorted by target domain into isolated folders:

```text
logs_example_com/
├── 20260721_120000.log
├── 20260721_120512.csv
└── 20260721_121045.json

```

### Sample JSON Output Schema

```json
{
  "url": "[https://example.com](https://example.com)",
  "elapsed_seconds": 0.38,
  "title": "Example Domain",
  "description": "Domain description metadata",
  "emails": [
    "contact@example.com"
  ],
  "phones": [
    "+1 (555) 019-2834"
  ],
  "social": [
    "[https://twitter.com/example](https://twitter.com/example)"
  ],
  "links": [
    "[https://external-resource.com](https://external-resource.com)"
  ]
}

```

---

## 📄 License

This software is open-source and released under the [MIT License](LICENSE).

```