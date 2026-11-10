"""Persistent deal log: a CSV that grows a little every run and lives in your repo (data/deals.csv).

Only facts that can be read straight from the headline/summary text are filled in by rules (value and
stake as written, status). Target, buyer and seller come from the AI deal card when there is one.
Anything unknown stays blank; nothing is guessed.
"""
import csv
import os
import re

import config as C
from util import has

FIELDS = ['first_seen', 'published', 'headline', 'deal_type', 'status', 'value', 'stake',
          'target', 'buyer_investor', 'seller', 'sector', 'source', 'url']

AMOUNT = re.compile(r'(?:₹|rs\.?\s?|usd\s?|\$)\s?[\d,]+(?:\.\d+)?\s?(?:lakh crore|crore|cr|trillion|billion|bn|million|mn)?', re.I)
STAKE = re.compile(r'(\d+(?:\.\d+)?)\s?(?:%|per cent|percent)\s+(?:stake|shareholding|equity)', re.I)


def _safe(value):
    """Stops spreadsheet programs treating a cell as a formula."""
    value = (value or '').replace('\n', ' ').strip()
    return "'" + value if value[:1] in ('=', '+', '-', '@') else value


def _ai(card, key):
    v = (card or {}).get(key, '')
    return '' if not v or v == 'Not disclosed' else v


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
        }
        old = by_url.get(s['url'])
        if old is None:
            rows.append(new)
            by_url[s['url']] = new
            added += 1
        else:                                   # fill in blanks only (e.g. AI card arrived later)
            for k in ('value', 'stake', 'target', 'buyer_investor', 'seller', 'status'):
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
