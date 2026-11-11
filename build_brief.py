"""Data pipeline: fetch feeds and prices, classify, cluster, pick the front page, then render.

Runs on GitHub Actions every 15 minutes (see .github/workflows/brief.yml), or locally with:
    python build_brief.py
"""
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import config as C
import deals
import learn
from util import IST, clean_text, full_text, has, run_with_timeout

try:                      # market prices; the page still builds without it
    import yfinance as yf
except ImportError:
    yf = None

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
OUT_DIR = os.environ.get('OUT_DIR', 'site')


# ---------------------------------------------------------------- RSS fetching
def parse_date(raw):
    if not raw:
        return None
    try:
        d = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=IST)     # feeds without a zone (e.g. RBI) are in Indian time


def fetch_feed(item):
    name, url = item
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as resp:
            root = ET.fromstring(resp.read())
    except Exception as err:
        return name, [], f'{name} ({str(err)[:60]})'

    # RSS uses <item>, Atom uses <entry>.
    nodes = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
    articles = []
    for node in nodes[:C.ITEMS_PER_SOURCE]:
        def get(tag):
            el = node.find(tag)
            if el is None:
                el = node.find('{http://www.w3.org/2005/Atom}' + tag)
            return el

        title = clean_text(get('title').text if get('title') is not None else '')
        link_el = get('link')
        link = ''
        if link_el is not None:
            link = (link_el.text or link_el.get('href') or '').strip()
        desc_el = get('description') if get('description') is not None else get('summary')
        summary = clean_text(desc_el.text if desc_el is not None else '')
        date_el = get('pubDate') if get('pubDate') is not None else get('published')
        published = parse_date(date_el.text if date_el is not None else '')
        if published and published > datetime.now(timezone.utc) + timedelta(minutes=5):
            published = datetime.now(timezone.utc)      # a time in the future is a feed error: show as 'just now'
        if title and link:
            articles.append({'headline': title, 'url': link, 'source': name,
                             'summary': summary, 'published': published})
    err = None if articles else f'{name} (loaded but no articles found)'
    return name, articles, err


def fetch_all_articles(failed):
    with ThreadPoolExecutor(max_workers=len(C.FEEDS)) as pool:
        results = list(pool.map(fetch_feed, C.FEEDS.items()))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=C.MAX_AGE_HOURS)
    articles = []
    for _, items, err in results:
        if err:
            failed.append(err)
        for a in items:
            if a['published'] and a['published'] < cutoff:
                continue
            if has(full_text(a), C.NON_FINANCE_WORDS) or has(a['headline'].lower(), C.DROP_HEADLINE_WORDS):
                continue
            articles.append(a)
    return articles


def fetch_money_stuff(failed):
    """The single newest Money Stuff column (daily limit 1), kept apart from the news stories."""
    cfg = C.MONEY_STUFF
    _, items, err = fetch_feed((cfg['name'], cfg['url']))
    if err:
        failed.append(err)
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(hours=C.MAX_AGE_HOURS)
    items = [a for a in items if not a['published'] or a['published'] >= cutoff]
    if not items:
        return None
    a = max(items, key=lambda x: x['published'] or datetime.min.replace(tzinfo=timezone.utc))
    a['importance'] = 5 if has(full_text(a), C.MONEY_STUFF_BOOST) else 4
    a['desk'] = 'Finance Logic & Market Structure'
    return a


# ---------------------------------------------------------------- classification
def classify(a):
    """Returns (desk, deal_category, how) where how is 'head', 'summary' or 'default'."""
    head, full = a['headline'].lower(), full_text(a)
    if a['source'] == 'RBI press releases':      # a regulator release is policy news whatever its wording
        return 'Central Banks & Policy', None, 'head'
    for rule in C.DESK_RULES:                       # pass 1: headline only
        desk, deal_cat, words = rule[:3]
        if has(head, words):
            return desk, deal_cat, 'head'
    for rule in C.DESK_RULES:                       # pass 2: headline + summary
        desk, deal_cat, words = rule[:3]
        if desk in C.SUMMARY_PASS_SKIP or len(rule) > 3:
            continue
        if has(full, words):
            return desk, deal_cat, 'summary'
    return C.DEFAULT_DESK, None, 'default'


def importance(a):
    text, desk = full_text(a), a['desk']
    score = 2 + min(sum(1 for w in C.HIGH_VALUE_DEAL_WORDS if has(text, [w])), 2)
    if desk in C.DEAL_DESKS:
        score += 1
    if has(text, ['rbi', 'fed', 'repo rate', 'inflation', 'gdp', 'sebi']):
        score += 1
    if has(text, ['record', 'largest', 'major', 'billion', 'trillion', 'crore']):
        score += 1
    return max(1, min(score, 5))


def deal_stage(a):
    text = full_text(a)
    for stage, words in C.STAGE_RULES:
        if has(text, words):
            return stage
    return 'Announced'


def why_it_matters(a):
    text = full_text(a)
    head = a['headline'].lower()
    for words, line in C.WHY_SPECIAL:
        if has(head, words) and a['desk'] != 'IPOs & Block Deals':
            return line
    rules = C.WHY_RULES if a['desk'] in C.WHY_RULE_DESKS else []
    for words, line in rules:
        if has(text, words):
            return line
    return C.WHY_BY_DESK.get(a['desk'], C.WHY_DEFAULT)


def preset_concepts(a):
    text = full_text(a)
    found = [name for name, (trig, _) in C.CONCEPTS.items() if has(text, trig)]
    found.sort(key=lambda n: C.CONCEPT_PRIORITY.index(n) if n in C.CONCEPT_PRIORITY else 99)
    found = found[:4]
    return found, {n: C.CONCEPTS[n][1] for n in found}


def enrich(a):
    a['desk'], a['deal_cat'], a['how'] = classify(a)
    a['importance'] = importance(a)
    a['why'] = why_it_matters(a)
    a['stage'] = deal_stage(a) if a['deal_cat'] else None
    a['concepts'], a['definitions'] = preset_concepts(a)
    return a


# ---------------------------------------------------------------- clustering
STOP = {'the', 'and', 'for', 'with', 'from', 'over', 'that', 'this', 'will', 'has',
        'are', 'how', 'why', 'can', 'you', 'not', 'new', 'its', 'but', 'after', 'into',
        'what', 'your', 'about', 'says', 'amid', 'more', 'than', 'crore', 'lakh',
        'shares', 'share', 'price', 'stock', 'stocks', 'india', 'today', 'news',
        'here', 'details', 'key', 'top'}
ENTITY_IGNORE = {'the', 'and', 'for', 'with', 'from', 'india', 'indian', 'markets',
                 'market', 'stock', 'stocks', 'share', 'shares', 'price', 'prices',
                 'ipo', 'drhp', 'qip', 'fpo', 'rbi', 'sebi', 'fed', 'gmp', 'check',
                 'should', 'what', 'why', 'how', 'update', 'exclusive', 'live', 'news',
                 'top', 'best', 'after', 'before', 'amid', 'nifty', 'sensex', 'q1', 'q2', 'q3', 'q4'}


def title_words(title):
    return {w for w in re.findall(r'[a-z0-9]+', title.lower()) if w not in STOP}


def entities(a):
    caps = re.findall(r'\b[A-Z][A-Za-z0-9&.\-]{2,}\b', a['headline'])
    return {w.lower() for w in caps if w.lower() not in ENTITY_IGNORE}


def same_story(a, b):
    wa, wb = title_words(a['headline']), title_words(b['headline'])
    overlap = len(wa & wb) / max(len(wa | wb), 1)
    shared = len(entities(a) & entities(b))
    event = bool(wa & wb & C.EVENT_WORDS)         # same subject + same kind of event, e.g. Anthropic + IPO
    return overlap >= 0.4 or shared >= 2 or (shared == 1 and overlap >= 0.2) or (shared >= 1 and event and overlap >= 0.08)


def cluster(articles):
    groups = []
    for a in articles:
        for g in groups:
            if any(same_story(a, m) for m in g):
                g.append(a)
                break
        else:
            groups.append([a])
    stories = []
    for g in groups:
        def pick(x):
            h = x['headline'].lower()
            penalty = (1 if has(h, C.PROMO_WORDS) else 0) + (1 if has(h, C.WRAP_WORDS) else 0)
            return (x['importance'] - penalty, x['published'] or datetime.min.replace(tzinfo=timezone.utc))
        primary = max(g, key=pick)
        primary['related'] = [x for x in g if x is not primary]
        stories.append(primary)
    return stories



# ---------------------------------------------------------------- market prices
def get_quote(symbol):
    """Returns (last, day %, as-of date, 1-week %, year-to-date %, 52-week high, 52-week low)."""
    hist = yf.Ticker(symbol).history(period='1y')
    closes = hist['Close'].dropna()
    if len(closes) < 2:
        raise ValueError('not enough data')
    last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
    week = (last / float(closes.iloc[-6]) - 1) * 100 if len(closes) >= 6 else None
    prior = closes[closes.index.year < closes.index[-1].year]
    ytd = (last / float(prior.iloc[-1]) - 1) * 100 if len(prior) else None
    hi = float(hist['High'].dropna().max()) if 'High' in hist else float(closes.max())
    lo = float(hist['Low'].dropna().min()) if 'Low' in hist else float(closes.min())
    return last, (last - prev) / prev * 100, closes.index[-1].strftime('%d %b'), week, ytd, hi, lo


def fetch_quotes(groups, failed):
    """groups: {title: {name: symbol}} -> {title: [(name, last, change, day)]}"""
    if yf is None:
        failed.append('Market prices (yfinance not installed)')
        return {}
    jobs = [(t, n, s) for t, items in groups.items() for n, s in items.items()]

    def run(job):
        title, name, sym = job
        try:
            return title, name, run_with_timeout(get_quote, C.QUOTE_TIMEOUT, sym), None
        except Exception as err:
            return title, name, None, f'{name} ({str(err)[:50] or "timed out"})'

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(run, jobs))
    out = defaultdict(list)
    for title, name, quote, err in results:
        if err:
            failed.append(err)
        else:
            out[title].append((name, *quote))
    return out



# ---------------------------------------------------------------- front page selection
NOISE_HEADLINES = ['live updates', 'stock market live', 'stocks in focus', 'stocks to watch',
                   'sensex today', 'nifty today']
FAR_PAST = datetime.min.replace(tzinfo=timezone.utc)


def prominence(s):
    """Importance plus a bonus when several outlets cover the same story."""
    sources = {s['source']} | {r['source'] for r in s['related']}
    return s['importance'] + 0.75 * min(len(sources) - 1, 4)


def select_front(stories):
    by_desk = defaultdict(list)
    for s in stories:
        by_desk[s['desk']].append(s)
    for d in by_desk.values():
        d.sort(key=lambda s: (s['importance'], s['published'] or FAR_PAST), reverse=True)

    eligible = [s for s in stories
                if s['how'] == 'head' and not s['desk'].startswith('Trading Ideas')
                and not has(s['headline'].lower(), NOISE_HEADLINES)]
    ranked = sorted(eligible, key=lambda s: (prominence(s) - (1 if has(s['headline'].lower(), C.PROMO_WORDS) else 0),
                                             s['published'] or FAR_PAST), reverse=True)
    lead = ranked[0] if ranked else None
    secondary = ranked[1:7]

    cands = [s for d in C.DEAL_DESKS for s in by_desk.get(d, [])
             if deals.is_deal(s)]            # a real transaction headline, not commentary
    top_deals = sorted(cands, key=lambda s: (s['importance'], s['published'] or FAR_PAST),
                       reverse=True)[:C.MAX_TOP_DEALS]
    earnings = [s for s in by_desk.get('Companies & Earnings', []) if s['how'] == 'head'][:C.EARNINGS_ROWS_MAX]
    wire = sorted([s for s in stories if not s['desk'].startswith('Trading Ideas')],
                  key=lambda s: s['published'] or FAR_PAST, reverse=True)[:C.WIRE_ITEMS]
    day_ago = datetime.now(timezone.utc) - timedelta(hours=30)
    flows = sorted([s for s in stories if has(s['headline'].lower(), C.FLOW_WORDS)],
                   key=lambda s: s['published'] or FAR_PAST, reverse=True)[:C.MAX_FLOW_ITEMS]
    return dict(by_desk=by_desk, lead=lead, secondary=secondary, top_deals=top_deals,
                earnings=earnings, wire=wire, flows=flows, conflicts=find_conflicts(stories, day_ago))


def find_conflicts(stories, since):
    """Headlines on the same topic pointing in opposite directions (they may cover different periods)."""
    out = []
    recent = [s for s in stories if not s['desk'].startswith('Trading Ideas')
              and (s['published'] is None or s['published'] >= since)]
    for topic, words in C.CONFLICT_TOPICS.items():
        ups, downs = [], []
        for s in recent:
            h = s['headline'].lower()
            if not has(h, words):
                continue
            up, down = has(h, C.UP_WORDS), has(h, C.DOWN_WORDS)
            if up and not down:
                ups.append(s)
            elif down and not up:
                downs.append(s)
        if ups and downs:
            out.append({'topic': topic, 'up': ups[0], 'down': downs[0]})
    return out


# ---------------------------------------------------------------- main
def main():
    import ai
    import render

    t0 = time.monotonic()

    def log(msg):
        print(f'[{time.monotonic() - t0:6.1f}s] {msg}', flush=True)

    now = datetime.now(IST)
    failed = []
    log('fetching news feeds')
    articles = [enrich(a) for a in fetch_all_articles(failed)]
    ms = fetch_money_stuff(failed)
    articles = [a for a in articles
                if not (a['how'] == 'default' and not has(full_text(a), C.MARKET_WORDS))]
    stories = cluster(articles)
    for i, s in enumerate(stories):
        s['id'] = i
    log(f'{len(articles)} articles -> {len(stories)} stories; fetching prices')
    if len(articles) < 3:
        # Nothing usable loaded: stop here so the last good edition stays online.
        print('No news loaded; keeping the previous edition. Problems: ' + '; '.join(failed), flush=True)
        sys.exit(1)

    groups = {'Macro': C.MACRO, 'My watchlist': C.WATCHLIST, 'Sectors': C.SECTORS}
    groups.update({'Region: ' + r: m for r, m in C.GLOBAL_INDICES.items()})
    tables = fetch_quotes(groups, failed)
    log('prices done; starting AI layer')

    plan = select_front(stories)
    gem = ai.Gemini()
    extras = ai.run(gem, stories, plan, tables, now)
    extras['ms'] = ms
    extras['money'] = ai.run_learn(gem, ms, now)
    extras['concall'] = learn.load_concall(now.date())
    extras['ai_state'] = gem.state()
    extras['feeds_failed'] = len(failed)
    log('AI layer done; updating deal log and rendering page')
    extras['deal_log'], added = deals.update(stories, extras, now)

    allrows = deals.load()
    usdinr = next((r[1] for r in tables.get('Macro', []) if r[0] == 'USD/INR'), None)
    extras['insights'] = deals.insights(allrows, usdinr)
    deals.write_pitchbook(allrows)

    page = render.build_page(stories, plan, tables, extras, failed, [gem.reader_note()], now, gem.detail())
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    try:
        import shutil
        for src_path, name in ((C.DEAL_LOG_PATH, 'deals.csv'), (C.PITCHBOOK_PATH, 'pitchbook_style_deals.csv')):
            if os.path.exists(src_path):
                shutil.copy(src_path, os.path.join(OUT_DIR, name))
    except Exception:
        pass
    gem.save()
    log(f'Built {OUT_DIR}/index.html. {gem.status_note()} Deal log: {added} new row(s).')
    for item in failed:
        log('did not load: ' + item)


if __name__ == '__main__':
    main()
    sys.stdout.flush()
    os._exit(0)        # do not wait for any abandoned background request
