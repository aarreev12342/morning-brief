"""Persistent deal log: a CSV that grows a little every run and lives in your repo (data/deals.csv).

Only facts that can be read straight from the headline/summary text are filled in by rules (value and
stake as written, status). Target, buyer and seller come from the AI deal card when there is one.
Anything unknown stays blank; nothing is guessed.
"""
import csv
import os
import re
from collections import Counter

import config as C
from util import has

FIELDS = ['first_seen', 'published', 'headline', 'deal_type', 'status', 'value', 'stake',
          'target', 'buyer_investor', 'seller', 'sector', 'source', 'url',
          'geography', 'valuation', 'use_of_proceeds', 'strategic_rationale', 'exit_route']

AMOUNT = re.compile(r'(?:₹|rs\.?\s?|usd\s?|\$)\s?[\d,]+(?:\.\d+)?\s?(?:lakh crore|crore|cr|trillion|billion|bn|million|mn)?', re.I)
STAKE = re.compile(r'(\d+(?:\.\d+)?)\s?(?:%|per cent|percent)\s+(?:stake|shareholding|equity)', re.I)


def _safe(value):
    """Stops spreadsheet programs treating a cell as a formula."""
    value = (value or '').replace('\n', ' ').strip()
    return "'" + value if value[:1] in ('=', '+', '-', '@') else value


def _ai(card, key):
    v = (card or {}).get(key, '')
    return '' if not v or v == 'Not disclosed' else v


INVESTOR_RE = re.compile(r'^(.{2,40}?)\s+(?:to acquire|acquires|to invest|invests|to buy|buys|picks up|to pick up|bags|to take|'
                         r'may take|may acquire|may invest|to snap up|agrees to buy|agrees to acquire)\b', re.I)
TARGET_RE = re.compile(r'(?:stake in|acquire|acquires|acquisition of|buys|buy|invest(?:s)? in)\s+(.{2,50}?)'
                       r'(?:\s+for\b|\s+at\b|\s+in\b|\s+from\b|,|$)', re.I)
INDIA_RE = re.compile(r'₹|\bcrore\b|\brs\.?\s?\d|\bindia\b|\bindian\b|\bsebi\b|\bnse\b|\bbse\b|bengaluru|mumbai|delhi|'
                      r'gurugram|hyderabad|chennai|pune', re.I)


def sector_of(text):
    t = text.lower()
    for name, words in C.SECTOR_KEYWORDS:
        if has(t, words):
            return name
    return ''


def load():
    try:
        with open(C.DEAL_LOG_PATH, encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def is_deal(s):
    h = s['headline'].lower()
    return bool(s.get('deal_cat') and s['how'] == 'head' and has(h, C.TRANSACTION_WORDS)
                and not has(h, C.TOP_DEAL_EXCLUDE))


def update(stories, extras, now):
    """Adds today's deal stories to the CSV. Returns (recent rows for the page, number added)."""
    rows = load()
    by_url = {r['url']: r for r in rows}
    added = 0
    for s in stories:
        if not is_deal(s):
            continue
        text = s['headline'] + ' ' + s['summary']
        m = AMOUNT.search(s['headline']) or AMOUNT.search(text)
        st = STAKE.search(s['headline']) or STAKE.search(text)
        card = extras.get('deals', {}).get(s['id'])
        new = {
            'first_seen': now.strftime('%Y-%m-%d %H:%M'),
            'published': s['published'].astimezone(now.tzinfo).strftime('%Y-%m-%d %H:%M') if s['published'] else '',
            'headline': _safe(s['headline']),
            'deal_type': s['deal_cat'] or '',
            'status': s.get('stage') or '',
            'value': _safe(m.group(0).strip(' ,.')) if m else '',
            'stake': (st.group(1) + '%') if st else '',
            'target': _safe(_ai(card, 'Target')),
            'buyer_investor': _safe(_ai(card, 'Buyer / investor')),
            'seller': _safe(_ai(card, 'Seller')),
            'sector': '',
            'source': s['source'],
            'url': s['url'],
            'geography': 'India' if INDIA_RE.search(text) else '',
            'valuation': _safe(_ai(card, 'Valuation')),
            'use_of_proceeds': _safe(_ai(card, 'Use of proceeds')),
            'strategic_rationale': _safe(_ai(card, 'Strategic logic') or (card or {}).get('_why', '')),
            'exit_route': _safe(_ai(card, 'Exit route')),
        }
        new['sector'] = sector_of(text)
        old = by_url.get(s['url'])
        if old is None:
            rows.append(new)
            by_url[s['url']] = new
            added += 1
        else:                                   # fill in blanks only (e.g. AI card arrived later)
            for k in ('value', 'stake', 'target', 'buyer_investor', 'seller', 'status', 'sector', 'geography',
                      'valuation', 'use_of_proceeds', 'strategic_rationale', 'exit_route'):
                if not old.get(k) and new[k]:
                    old[k] = new[k]
    rows = rows[-C.DEAL_LOG_MAX_ROWS:]
    try:
        os.makedirs(os.path.dirname(C.DEAL_LOG_PATH) or '.', exist_ok=True)
        with open(C.DEAL_LOG_PATH, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows({k: r.get(k, '') for k in FIELDS} for r in rows)
    except Exception:
        pass
    return list(reversed(rows))[:C.DEAL_LOG_SHOW], added


# ---------------------------------------------------------------- PitchBook-style view
def investor_of(r):
    if r.get('buyer_investor'):
        return r['buyer_investor']
    m = INVESTOR_RE.match(r.get('headline', ''))
    return m.group(1).strip() if m else ''


def company_of(r):
    if r.get('target'):
        return r['target']
    m = TARGET_RE.search(r.get('headline', ''))
    return m.group(1).strip() if m else ''


def write_pitchbook(rows):
    """Writes data/pitchbook_style_deals.csv: the deal log in the column layout of a deal database.
    Company and investor come from the AI card when there is one, else from the headline wording."""
    try:
        os.makedirs(os.path.dirname(C.PITCHBOOK_PATH) or '.', exist_ok=True)
        with open(C.PITCHBOOK_PATH, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(C.PITCHBOOK_FIELDS)
            for r in rows:
                w.writerow([_safe((r.get('published') or r.get('first_seen', ''))[:10]), _safe(company_of(r)),
                            _safe(investor_of(r)), r.get('deal_type', ''), r.get('sector', ''), r.get('geography', ''),
                            r.get('value', ''), r.get('stake', ''), r.get('valuation', ''), r.get('status', ''),
                            r.get('use_of_proceeds', ''), r.get('strategic_rationale', ''), r.get('exit_route', ''),
                            r.get('url', '')])
    except Exception:
        pass


UNIT = {'lakh crore': 1e5, 'crore': 1.0, 'cr': 1.0, 'trillion': 1e12, 'billion': 1e9, 'bn': 1e9, 'million': 1e6, 'mn': 1e6}


def value_crore(text, usdinr):
    """Deal value in rupee crore, only when the unit is stated. Dollar values use today's USD/INR (approximate)."""
    t = (text or '').lower()
    m = re.search(r'([\d,]+(?:\.\d+)?)\s?(lakh crore|crore|cr|trillion|billion|bn|million|mn)\b', t)
    if not m:
        return None
    try:
        n = float(m.group(1).replace(',', ''))
    except ValueError:
        return None
    unit = m.group(2)
    if unit in ('crore', 'cr', 'lakh crore'):
        return n * UNIT[unit]
    if '$' in t or 'usd' in t:
        return n * UNIT[unit] * usdinr / 1e7 if usdinr else None
    return None


def insights(rows, usdinr):
    """Counts and rankings over the whole log. Only values with a stated unit are ranked."""
    valued = []
    for r in rows:
        v = value_crore(r.get('value'), usdinr)
        if v:
            valued.append((v, r))
    valued.sort(key=lambda x: x[0], reverse=True)
    sectors = Counter(r['sector'] for r in rows if r.get('sector'))
    investors = Counter(investor_of(r) for r in rows if investor_of(r))
    low = lambda r: r.get('headline', '').lower()
    return {
        'top_value': [r for _, r in valued[:5]],
        'india': [r for _, r in valued if r.get('geography') == 'India'][:5],
        'sectors': sectors.most_common(5),
        'investors': investors.most_common(5),
        'ipo_bound': [r for r in reversed(rows) if r.get('deal_type') == 'IPO & Block Deals'
                      and has(low(r), C.IPO_BOUND_WORDS)][:5],
        'exits': [r for r in reversed(rows) if has(low(r), C.EXIT_WORDS)][:5],
        'usd_note': bool(usdinr),
        'n': len(rows),
    }
