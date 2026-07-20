#!/usr/bin/env python3
import os
import sys
import subprocess

REQUIRED_PACKAGES = ["requests", "beautifulsoup4", "rich"]

def ensure_dependencies():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            if pkg == "beautifulsoup4":
                __import__("bs4")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print(f"[!] Missing required dependencies: {', '.join(missing)}")
        print("[*] Automatically installing missing packages...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *missing],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[+] Dependencies installed successfully!\n")
        except Exception as err:
            print(f"[X] Failed to auto-install dependencies: {err}")
            print(f"Please manually run: pip install {' '.join(missing)}")
            sys.exit(1)

ensure_dependencies()

import re
import json
import csv
import socket
import argparse
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

console = Console()

REPO_OWNER = "theskullnetwork"
REPO_NAME = "skullscrape"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/scraper.py"
GITHUB_API_COMMITS = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/main"

VERSION_TAG = "v1.0.0"

EMAIL_RE = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_RE = r'(?<!\.)(?:\+?\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]\d{3}[-\s]\d{4,6}(?!\.\d)'

SOCIAL_DOMAINS = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com',
                  'instagram.com', 'github.com', 'youtube.com', 'tiktok.com']

USER_AGENT = 'Mozilla/5.0 (compatible; SkullScrape/1.0)'


def check_and_apply_update():
    try:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}
        resp = requests.get(GITHUB_API_COMMITS, headers=headers, timeout=3)
        if resp.status_code != 200:
            return
        
        latest_sha = resp.json().get("sha", "")
        sha_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".latest_sha")
        
        current_sha = ""
        if os.path.exists(sha_file):
            with open(sha_file, "r") as f:
                current_sha = f.read().strip()
                
        if not current_sha:
            with open(sha_file, "w") as f:
                f.write(latest_sha)
            return

        if latest_sha and current_sha != latest_sha:
            console.print("[bold yellow][!] New update found on GitHub! Downloading...[/bold yellow]")
            
            raw_code = requests.get(GITHUB_RAW_URL, headers={"User-Agent": USER_AGENT}, timeout=5)
            if raw_code.status_code == 200:
                script_path = os.path.abspath(__file__)
                
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(raw_code.text)
                
                with open(sha_file, "w") as f:
                    f.write(latest_sha)
                    
                console.print("[bold green][+] Successfully updated! Restarting script...[/bold green]\n")
                
                os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception:
        pass


def is_connected() -> bool:
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("1.1.1.1", 53))
        return True
    except OSError:
        return False


def is_valid_url(target: str) -> bool:
    parsed = urlparse(target)
    netloc = parsed.netloc or parsed.path.split('/')[0]
    return bool(re.match(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?$', netloc))


def normalize_url(target: str) -> str:
    target = target.strip()
    if not target.startswith("http://") and not target.startswith("https://"):
        target = f"https://{target}"
    return target


def fetch_with_retry(target: str, retries: int = 3, timeout: int = 10):
    headers = {'User-Agent': USER_AGENT}
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(target, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            last_err = e
            if attempt < retries:
                console.print(f"[dim]  retry {attempt}/{retries}...[/dim]")
    raise last_err


def extract_data(html_text: str, soup: BeautifulSoup):
    emails = sorted(set(re.findall(EMAIL_RE, html_text)))
    phones = sorted(set(re.findall(PHONE_RE, html_text)))

    all_links = sorted(set(
        a.get('href') for a in soup.find_all('a', href=True)
        if a.get('href').startswith('http')
    ))

    social = sorted({l for l in all_links if any(s in l for s in SOCIAL_DOMAINS)})
    links = sorted(set(all_links) - set(social))

    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else None

    desc_tag = soup.find('meta', attrs={'name': 'description'})
    description = desc_tag.get('content', '').strip() if desc_tag else None

    return {
        "title": title,
        "description": description,
        "emails": emails,
        "phones": phones,
        "links": links,
        "social": social,
    }


LOGO = r"""
   _____ __          ____   _____                          
  / ___// /____  _  / / /  / ___/______________ _____  ___ 
  \__ \/ //_/ / / / / /   \__ \/ ___/ ___/ __ `/ __ \/ _ \
 ___/ / ,< / /_/ / / /   ___/ / /__/ /  / /_/ / /_/ /  __/
/____/_/|_|\__,_/_/_/   /____/\___/_/   \__,_/ .___/\___/ 
                                            /_/           
"""


def render_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(f"[bold cyan]{LOGO}[/bold cyan]")
    console.print(f"[bold bright_white]SkullScrape {VERSION_TAG}[/bold bright_white] [dim white]— Contact & Link Intelligence Extraction[/dim white]")
    console.print(f"[bold cyan]Github:[/bold cyan] [underline bright_blue]{REPO_URL}[/underline bright_blue]")
    console.print(f"[dim yellow]Run 'python scraper.py --help' for CLI flags and usage.[/dim yellow]\n")


def prompt_target_url() -> str:
    while True:
        target = console.input("[bold cyan]Enter URL[/bold cyan][bold white]: [/bold white]").strip()
        if not target:
            return ""
        
        normalized = normalize_url(target)
        if is_valid_url(normalized):
            return normalized
        
        console.print("[bold red]Error:[/bold red] Invalid URL format. Please enter a valid domain (e.g. example.com).\n")


def render_page_info(data: dict):
    if data.get("title") or data.get("description"):
        lines = []
        if data.get("title"):
            lines.append(f"[bold]{data['title']}[/bold]")
        if data.get("description"):
            lines.append(f"[dim]{data['description']}[/dim]")
        console.print(Panel("\n".join(lines), title="Page Info", expand=False, border_style="cyan"))


def render_table(data: dict):
    table = Table(box=None, header_style="bold cyan")
    table.add_column("Type", width=12)
    table.add_column("Data")

    for m in data["emails"]:
        table.add_row("Email", m)
    for p in data["phones"]:
        table.add_row("Phone", p)
    for s in data["social"]:
        table.add_row("Social", s)
    for l in data["links"]:
        table.add_row("Link", l)

    console.print(table)


def render_summary(data: dict):
    summary = (
        f"[bold]{len(data['emails'])}[/bold] emails   "
        f"[bold]{len(data['phones'])}[/bold] phones   "
        f"[bold]{len(data['social'])}[/bold] social   "
        f"[bold]{len(data['links'])}[/bold] links"
    )
    console.print(Panel(summary, title="Summary", expand=False))


def save_output(data: dict, target: str, domain: str, fmt: str):
    safe_domain = re.sub(r'[^\w.\-]', '_', domain)
    log_dir = f"logs_{safe_domain}"
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "json":
        path = os.path.join(log_dir, f"{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"url": target, **data}, f, indent=2)
        return path

    if fmt == "csv":
        path = os.path.join(log_dir, f"{ts}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "value"])
            for k in ("emails", "phones", "social", "links"):
                for v in data[k]:
                    writer.writerow([k[:-1], v])
        return path

    path = os.path.join(log_dir, f"{ts}.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"SkullScrape {VERSION_TAG}\nURL: {target}\n")
        if data.get("title"):
            f.write(f"Title: {data['title']}\n")
        f.write("\n")
        for k in ("emails", "phones", "social", "links"):
            f.write(f"{k.capitalize()}:\n" + "\n".join(data[k]) + "\n\n")
    return path


def run(target: str, out_fmt: str, quiet: bool, auto_save: bool):
    target = normalize_url(target)
    domain = urlparse(target).netloc

    if not quiet:
        console.print(f"[bold white][*][/bold white] Target: {target}")

    try:
        start = datetime.now()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      console=console, transient=True, disable=quiet) as progress:
            progress.add_task(description="Fetching page...", total=None)
            r = fetch_with_retry(target)
            soup = BeautifulSoup(r.text, 'html.parser')
            data = extract_data(r.text, soup)
        elapsed = (datetime.now() - start).total_seconds()

        if not quiet:
            console.print()
            render_page_info(data)
            render_table(data)
            console.print()
            render_summary(data)
            console.print(f"[dim]Completed in {elapsed:.2f}s[/dim]")

        if auto_save or (not quiet and console.input("\n[bold white]Save results? (y/n): [/bold white]").lower() == 'y'):
            path = save_output(data, target, domain, out_fmt)
            console.print(f"[bold green]Saved: {path}[/bold green]")

        if quiet:
            print(json.dumps({"url": target, "elapsed_seconds": elapsed, **data}))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to reach target ({e})\n")


def main():
    parser = argparse.ArgumentParser(description="Extract emails, phones, and links from a webpage.")
    parser.add_argument("-u", "--url", help="Target URL (skips interactive prompt)")
    parser.add_argument("-f", "--format", choices=["log", "json", "csv"], default="log",
                        help="Output format when saving (default: log)")
    parser.add_argument("--save", action="store_true", help="Auto-save without prompting")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress UI, print JSON result to stdout (for scripting)")
    parser.add_argument("--no-update", action="store_true", help="Disable auto-checking GitHub updates")
    args = parser.parse_args()

    if not is_connected():
        if not args.quiet:
            render_banner()
            console.print("[bold red]Error:[/bold red] No internet connection detected. Please check your network and try again.\n")
        sys.exit(1)

    if not args.no_update:
        check_and_apply_update()

    if not args.quiet:
        render_banner()

    if args.url:
        target = normalize_url(args.url)
        if not is_valid_url(target):
            console.print("[bold red]Error:[/bold red] Invalid URL format provided via argument.\n")
            sys.exit(1)
        run(target, args.format, args.quiet, args.save)
        return

    while True:
        target = prompt_target_url()
        if not target:
            break
            
        run(target, args.format, args.quiet, args.save)

        console.print()
        choice = console.input("[bold cyan]Test another URL?[/bold cyan] [bold white][Y/n][/bold white]: ").strip().lower()
        if choice in ('n', 'no', 'q', 'quit', 'exit'):
            console.print("\n[dim]Exiting SkullScrape.[/dim]\n")
            break
        
        render_banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[dim]Session interrupted. Exiting...[/dim]\n")
        sys.exit()
