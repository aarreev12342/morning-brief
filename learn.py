"""Concall watch: your hand-filled results calendar plus links. Nothing here is scraped or guessed."""
import csv
from datetime import datetime, timedelta

import config as C
from util import has


def _date(text):
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d %b %Y', '%d %B %Y', '%d/%m/%Y'):
        try:
            return datetime.strptime((text or '').strip(), fmt).date()
        except ValueError:
            pass
    return None


def load_concall(today):
    """Rows from data/concall_links.csv, split into reporting today and within the next 7 days."""
    rows = []
    try:
        with open(C.CONCALL_LINKS_PATH, encoding='utf-8', newline='') as f:
            rows = [r for r in csv.DictReader(f) if (r.get('company') or '').strip()]
    except Exception:
        pass
    out = {'today': [], 'week': [], 'all': rows}
    for r in rows:
        d = _date(r.get('results_date'))
        if d == today:
            out['today'].append(r)
        elif d and today < d <= today + timedelta(days=7):
            out['week'].append(r)
    return out


def auto_links(company):
    """Starting points for a company's filings. Screener only for companies on your watchlist."""
    out = []
    name = (company or '').lower()
    for wl, sym in C.WATCHLIST.items():
        aliases = C.WATCHLIST_ALIASES.get(wl, [wl.lower()])
        if wl.lower() == name or has(name, aliases):
            out.append(('Screener (documents)', f'https://www.screener.in/company/{sym.split(".")[0]}/consolidated/'))
            break
    return out + list(C.CONCALL_GENERIC_LINKS)
