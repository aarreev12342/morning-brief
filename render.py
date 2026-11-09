"""Turns the data into one newspaper-style HTML page (no external fonts, scripts or images)."""
import html
from datetime import datetime, timezone

import config as C
from util import IST, has

esc = html.escape

# ---------------------------------------------------------------- style + script
CSS = """
:root{--paper:#f7f3ea;--ink:#171715;--mut:#6a675f;--rule:#d9d3c4;--link:#7a1f1f;--card:#fffdf8;
--chipbg:#efe8d6;--chipfg:#4a3f1d;--up:#0b6b2d;--down:#b3261e;--accent:#8c1c13}
@media (prefers-color-scheme:dark){:root{--paper:#161513;--ink:#ece8dd;--mut:#a29d90;--rule:#38352e;
--link:#e8a07a;--card:#1d1b18;--chipbg:#2c2819;--chipfg:#e8d9a8;--up:#4cc26f;--down:#ff7a7a;--accent:#e8a07a}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 Georgia,'Times New Roman',serif}
.ui,.meta,table,nav,.ticker,.label,.note,.chip,.ai,.kicker,time{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
a{color:inherit;text-decoration:none}a:hover{text-decoration:underline;color:var(--link)}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 60px}
.mast{text-align:center;padding:14px 0 8px;border-bottom:3px double var(--ink)}
.mast .top{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font:12px sans-serif;
color:var(--mut);text-transform:uppercase;letter-spacing:.06em;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.mast h1{font-size:clamp(34px,7vw,66px);margin:8px 0 2px;font-weight:700;letter-spacing:-.01em;line-height:1.05}
.mast .sub{font:12px sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--mut);
font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.live{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--down);margin-right:6px;animation:p 2s infinite}
@keyframes p{50%{opacity:.25}}
@media (prefers-reduced-motion:reduce){.live{animation:none}}
.ticker{display:flex;gap:22px;overflow-x:auto;white-space:nowrap;border-bottom:1px solid var(--ink);
padding:8px 0;font-size:13px;scrollbar-width:none}
.ticker::-webkit-scrollbar{display:none}.ticker b{font-weight:600}
nav{position:sticky;top:0;z-index:5;background:var(--paper);display:flex;gap:18px;overflow-x:auto;
padding:9px 0;border-bottom:1px solid var(--rule);font-weight:700;font-size:12px;text-transform:uppercase;
letter-spacing:.09em;white-space:nowrap;scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
.up{color:var(--up)}.down{color:var(--down)}
.front{display:grid;grid-template-columns:minmax(0,1fr);gap:26px;margin-top:20px}
@media (min-width:900px){.front{grid-template-columns:minmax(0,2fr) minmax(0,1fr)}
.side{border-left:1px solid var(--rule);padding-left:22px}}
.kicker{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--accent)}
.lead-hl{font-size:clamp(27px,4.2vw,40px);line-height:1.13;margin:4px 0 10px;font-weight:700}
.dek{font-size:18px;margin:0 0 8px}
.meta{font-size:12px;color:var(--mut);margin-top:4px}
.why{font-size:14px;margin-top:6px;font-style:italic}
.chips{margin-top:6px;display:flex;gap:5px;flex-wrap:wrap}
.chip{background:var(--chipbg);color:var(--chipfg);padding:1px 8px;border-radius:10px;font-size:11px}
.ai{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;border:1px solid var(--rule);
border-radius:3px;padding:0 4px;color:var(--mut);margin-left:6px;vertical-align:middle;white-space:nowrap}
.grid2{display:grid;grid-template-columns:minmax(0,1fr);gap:0 26px;margin-top:20px}
@media (min-width:640px){.grid2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.item{padding:12px 0;border-top:1px solid var(--rule)}
.item h3{font-size:20px;line-height:1.2;margin:2px 0 4px}
.sum{font-size:15px;margin:0;color:var(--ink)}
.sec{font:700 13px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;text-transform:uppercase;
letter-spacing:.16em;border-top:3px double var(--ink);border-bottom:1px solid var(--rule);padding:7px 0;margin:38px 0 14px}
.label{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;border-top:2px solid var(--ink);
padding-top:6px;margin:22px 0 6px}
.cols{column-gap:30px;column-rule:1px solid var(--rule)}
@media (min-width:760px){.cols{column-count:2}}
.cols>*{break-inside:avoid}
.briefs{list-style:none;margin:0;padding:0}
.briefs li{padding:7px 0;border-bottom:1px solid var(--rule);font-size:16px;line-height:1.3}
.briefs li a{font-weight:600}
.side h2{font:700 12px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;text-transform:uppercase;
letter-spacing:.14em;border-top:2px solid var(--ink);padding-top:6px;margin:0 0 8px}
.side section{margin-bottom:26px}
.read p{margin:0 0 8px;font-size:15px}
.wire{list-style:none;margin:0;padding:0}
.wire li{display:grid;grid-template-columns:46px minmax(0,1fr);gap:8px;padding:7px 0;border-bottom:1px solid var(--rule);
font-size:14px;line-height:1.3}
.wire time{font-size:12px;font-weight:700;color:var(--accent);padding-top:1px}
.wire .meta{margin-top:2px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
td,th{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left}
th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
.num{text-align:right;font-variant-numeric:tabular-nums}.day{color:var(--mut);font-size:12px;text-align:right}
.region td{font-weight:700;color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.08em;padding-top:14px}
.hd td{color:var(--mut);font-size:11px;text-transform:uppercase}
.two{display:grid;grid-template-columns:minmax(0,1fr);gap:0 30px}
@media (min-width:900px){.two{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)}}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px;margin-top:6px}
.tile{border:1px solid var(--rule);padding:7px 8px;font:13px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;
display:flex;flex-direction:column;background:var(--card)}.tile b{font-size:15px}
.dealcard{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--accent);padding:10px 14px;margin:10px 0;
font-size:13px;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.dealcard h4{margin:0 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)}
.dealcard dl{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:3px 14px;margin:6px 0}
.dealcard dt{color:var(--mut)}.dealcard dd{margin:0}.nd{color:var(--mut)}
.dealcard p{margin:6px 0 0}.dealcard .ai{white-space:normal}
.note{font-size:12px;color:var(--mut);margin:8px 0}
details>summary{cursor:pointer;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.1em;padding:8px 0;
font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.study p{margin:4px 0 10px;font-size:16px}
#newed{display:none;position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:var(--ink);color:var(--paper);
padding:10px 18px;border-radius:22px;font:600 13px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;cursor:pointer;z-index:20;
box-shadow:0 4px 14px rgba(0,0,0,.3)}
"""

SCRIPT = """
(function(){
  var built = Date.parse(document.body.getAttribute('data-built'));
  var upd = document.getElementById('upd');
  function tick(){
    var m = Math.max(0, Math.round((Date.now() - built) / 60000));
    if (upd) upd.textContent = m < 1 ? 'just updated' : 'updated ' + (m < 60 ? m + ' min ago' : Math.floor(m / 60) + ' h ago');
  }
  tick(); setInterval(tick, 30000);
  function check(){
    fetch(location.pathname + '?t=' + Date.now(), {cache: 'no-store'}).then(function(r){ return r.text(); }).then(function(t){
      var m = t.match(/data-built="([^"]+)"/);
      if (m && Date.parse(m[1]) > built) document.getElementById('newed').style.display = 'block';
    }).catch(function(){});
  }
  setInterval(check, %REFRESH%);
  document.addEventListener('visibilitychange', function(){ if (!document.hidden) check(); });
})();
"""


# ---------------------------------------------------------------- small helpers
def ago(dt):
    if not dt:
        return ''
    mins = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
    if mins < 1:
        return 'just now'
    if mins < 60:
        return f'{mins}m ago'
    if mins < 48 * 60:
        return f'{mins // 60}h ago'
    return dt.astimezone(IST).strftime('%d %b')


def clock(dt, today):
    if not dt:
        return ''
    local = dt.astimezone(IST)
    return local.strftime('%H:%M') if local.date() == today else local.strftime('%a')


def pct(v):
    return f'{v:+.2f}%'


def updown(v):
    return 'up' if v >= 0 else 'down'


def find_quote(tables, name):
    for rows in tables.values():
        for r in rows:
            if r[0] == name:
                return r
    return None


def link(s, cls=''):
    return f'<a{(" class=" + cls) if cls else ""} href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["headline"])}</a>'


def meta_line(s, stage=False):
    bits = [s['source'], ago(s['published'])]
    if stage and s.get('stage'):
        bits.append(s['stage'])
    return ' · '.join(esc(b) for b in bits if b)


def also_line(s):
    seen, uniq = {s['source']}, []
    for r in s['related']:
        if r['source'] not in seen:
            seen.add(r['source'])
            uniq.append(r)
    if not uniq:
        return ''
    links = ', '.join(f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["source"])}</a>' for r in uniq[:4])
    return f'<div class="meta">Also reported by {links}</div>'


def summary_text(s, ai_text, limit):
    text = ai_text or s['summary']
    if not ai_text and text.lower().startswith(s['headline'].lower()[:40]):
        return ''
    return text if len(text) <= limit else text[:limit].rsplit(' ', 1)[0] + '…'


def chips(s):
    return ('<div class="chips">' + ''.join(f'<span class="chip">{esc(c)}</span>' for c in s['concepts']) + '</div>'
            if s['concepts'] else '')


def why_line(s):
    return f'<div class="why">{esc(s["why"])}</div>' if s['importance'] >= 4 and s['why'] else ''


def deal_card(card):
    if not card:
        return ''
    keys = ['Target', 'Buyer / investor', 'Seller', 'Deal type', 'Value', 'Stake', 'Valuation', 'Financing', 'Advisors']
    rows = ''.join(
        f'<dt>{esc(k)}</dt><dd class="{"nd" if card[k] == "Not disclosed" else ""}">{esc(card[k])}</dd>' for k in keys)
    extra = ''
    if card.get('_why'):
        extra += f'<p><b>Why it matters:</b> {esc(card["_why"])}</p>'
    if card.get('_watch'):
        extra += f'<p><b>What to watch:</b> {esc(card["_watch"])}</p>'
    return (f'<div class="dealcard"><h4>Deal card <span class="ai">AI · from the article</span></h4><dl>{rows}</dl>{extra}'
            '<p class="note">"Not disclosed" means the article did not say.</p></div>')


# ---------------------------------------------------------------- story blocks
def lead_html(s, extras):
    ai_text = extras['summaries'].get(s['id'])
    text = summary_text(s, ai_text, 600)
    return (f'<article><div class="kicker">{esc(s["desk"])}</div>'
            f'<h2 class="lead-hl">{link(s)}</h2>'
            + (f'<p class="dek">{esc(text)}{"<span class=ai>AI summary</span>" if ai_text else ""}</p>' if text else '')
            + f'<div class="meta">{meta_line(s)}</div>{deal_card(extras["deals"].get(s["id"]))}'
            + why_line(s) + chips(s) + also_line(s) + '</article>')


def item_html(s, extras, stage=False, kicker=True):
    ai_text = extras['summaries'].get(s['id'])
    text = summary_text(s, ai_text, 230)
    return (f'<div class="item">' + (f'<div class="kicker">{esc(s["desk"])}</div>' if kicker else '')
            + f'<h3>{link(s)}</h3>'
            + (f'<p class="sum">{esc(text)}{"<span class=ai>AI</span>" if ai_text else ""}</p>' if text else '')
            + f'<div class="meta">{meta_line(s, stage)}</div>'
            + deal_card(extras['deals'].get(s['id'])) + why_line(s) + also_line(s) + '</div>')


def brief_li(s, stage=False):
    return f'<li>{link(s)}<div class="meta">{meta_line(s, stage)}</div></li>'


def desk_html(title, stories, extras, cap, stage=False):
    stories = stories[:cap]
    if not stories:
        return ''
    full = [s for i, s in enumerate(stories) if i == 0 or (i == 1 and s['importance'] >= 4)]
    full_ids = {s['id'] for s in full}
    rest = [s for s in stories if s['id'] not in full_ids]
    body = ''.join(item_html(s, extras, stage, kicker=False) for s in full)
    if rest:
        body += '<ul class="briefs">' + ''.join(brief_li(s, stage) for s in rest) + '</ul>'
    return f'<div class="desk"><div class="label">{esc(title)}</div>{body}</div>'


# ---------------------------------------------------------------- tables
def pct_cell(v):
    if v is None:
        return '<td class="num">—</td>'
    return f'<td class="num {updown(v)}">{v:+.2f}%</td>'


def index_board(tables):
    today = datetime.now(IST).strftime('%d %b')
    rows = ''
    for region, members in C.GLOBAL_INDICES.items():
        data = tables.get('Region: ' + region)
        if not data:
            continue
        order = list(members)
        rows += f'<tr class="region"><td colspan="6">{esc(region)}</td></tr>'
        for name, last, day, asof, week, ytd in sorted(data, key=lambda r: order.index(r[0])):
            label = 'today' if asof == today else asof
            rows += (f'<tr><td>{esc(name)}</td><td class="num">{last:,.2f}</td>{pct_cell(day)}{pct_cell(week)}'
                     f'{pct_cell(ytd)}<td class="day">{esc(label)}</td></tr>')
    if not rows:
        return ''
    head = ('<tr class="hd"><td>Index</td><td class="num">Last</td><td class="num">Day</td><td class="num">1W</td>'
            '<td class="num">YTD</td><td class="day">As of</td></tr>')
    return (f'<div class="label">Global indices</div><div class="scroll"><table>{head}{rows}</table></div>'
            '<p class="note">Latest price Yahoo has. "today" means the market has traded today, so it can be a live (delayed) '
            'price rather than a close; other dates are the last close. MSCI rows use tracking ETFs.</p>')


def quote_table(title, rows):
    if not rows:
        return ''
    body = ''
    for name, last, change, day, *_ in rows:
        arrow = '▲' if change >= 0 else '▼'
        body += (f'<tr><td>{esc(name)}</td><td class="num">{last:,.2f}</td>'
                 f'<td class="num {updown(change)}">{arrow} {change:+.2f}%</td><td class="day">{esc(day)}</td></tr>')
    return f'<div class="label">{esc(title)}</div><div class="scroll"><table>{body}</table></div>'


def sector_heat(rows):
    if not rows:
        return ''
    tiles = ''.join(f'<div class="tile {updown(r[2])}"><span>{esc(r[0])}</span><b>{r[2]:+.2f}%</b></div>'
                    for r in sorted(rows, key=lambda r: r[2], reverse=True))
    return f'<div class="label">Sector heat map</div><div class="tiles">{tiles}</div>'


def earnings_table(rows):
    if not rows:
        return ''
    body = ''.join(
        f'<tr><td><a href="{esc(r["url"])}" target="_blank" rel="noopener"><b>{esc(r["company"])}</b></a></td>'
        f'<td>{esc(r["period"])}</td>' + ''.join(
            f'<td class="{"nd" if r[k] == "Not disclosed" else ""}">{esc(r[k] if r[k] != "Not disclosed" else "—")}</td>'
            for k in ('revenue', 'profit', 'margin'))
        + f'<td>{esc(r["driver"] if r["driver"] != "Not disclosed" else "—")}</td></tr>' for r in rows)
    return ('<div class="label">Results at a glance <span class="ai">AI · only figures stated in the report</span></div>'
            '<div class="scroll"><table><tr><th>Company</th><th>Period</th><th>Revenue</th><th>Profit</th><th>Margin</th>'
            f'<th>Driver</th></tr>{body}</table></div>')


# ---------------------------------------------------------------- sidebar pieces
def rule_read(tables):
    def fmt(names):
        return ', '.join(f'{nm} {pct(r[2])}' for nm in names if (r := find_quote(tables, nm)))
    lines = []
    secs = sorted(tables.get('Sectors', []), key=lambda r: r[2], reverse=True)
    india = fmt(['Nifty 50', 'Sensex', 'Nifty Bank', 'Nifty IT'])
    if india:
        t = 'India: ' + india
        if len(secs) >= 4:
            t += (f'. Leading sectors: {secs[0][0]} {pct(secs[0][2])}, {secs[1][0]} {pct(secs[1][2])}. '
                  f'Lagging: {secs[-1][0]} {pct(secs[-1][2])}, {secs[-2][0]} {pct(secs[-2][2])}')
        lines.append(t + '.')
    for label, names in [('US', ['S&P 500', 'Nasdaq Composite', 'Dow Jones']),
                         ('Europe', ['FTSE 100', 'DAX', 'CAC 40']),
                         ('Asia', ['Nikkei 225', 'Hang Seng', 'KOSPI'])]:
        t = fmt(names)
        if t:
            lines.append(f'{label}: {t}.')
    lv = []
    for nm, f in [('US 10Y yield (%)', 'US 10Y yield {:.2f}%'), ('Dollar index', 'dollar index {:.2f}'),
                  ('USD/INR', 'USD/INR {:.2f}'), ('Brent crude ($)', 'Brent ${:.2f}'), ('Gold ($/oz)', 'gold ${:,.0f}'),
                  ('India VIX', 'India VIX {:.2f}'), ('US VIX', 'US VIX {:.2f}')]:
        r = find_quote(tables, nm)
        if r:
            lv.append(f.format(r[1]))
    if lv:
        lines.append('Levels: ' + ', '.join(lv) + '.')
    return lines


def market_read_html(tables, extras):
    if extras['read']:
        lines, badge = extras['read'], f'<span class="ai">AI · {esc(extras["read_at"])} IST</span>'
        foot = 'AI-written from the numbers and headlines on this page; any cause named comes from a headline. Check the sources.'
    else:
        lines, badge = rule_read(tables), ''
        foot = 'Numbers only, taken from the tables below. This does not guess why markets moved.'
    if not lines:
        return ''
    return (f'<section class="read"><h2>Market read {badge}</h2>' + ''.join(f'<p>{esc(l)}</p>' for l in lines)
            + f'<p class="note">{foot}</p></section>')


def wire_html(wire, today):
    if not wire:
        return ''
    lis = ''.join(f'<li><time title="{esc(str(s["published"]))}">{esc(clock(s["published"], today))}</time>'
                  f'<div>{link(s)}<div class="meta">{esc(s["source"])}</div></div></li>' for s in wire)
    return f'<section><h2><span class="live"></span>Latest wire</h2><ul class="wire">{lis}</ul></section>'


def watchlist_alerts(stories):
    out = []
    for company in C.WATCHLIST:
        names = C.WATCHLIST_ALIASES.get(company, [company.lower()])
        hits = [s for s in stories if has(s['headline'].lower(), names)]
        if hits:
            best = max(hits, key=lambda s: s['importance'])
            out.append(f'<li><b>{esc(company)}</b>: {link(best)}</li>')
    return (f'<section><h2>Watchlist news</h2><ul class="briefs">{"".join(out)}</ul></section>' if out else '')


def ticker_html(tables):
    items = []
    for name in C.TICKER:
        r = find_quote(tables, name)
        if r:
            arrow = '▲' if r[2] >= 0 else '▼'
            short = name.replace(' ($)', '').replace(' ($/oz)', '').replace(' (%)', '')
            items.append(f'<span><b>{esc(short)}</b> {r[1]:,.2f} <span class="{updown(r[2])}">{arrow} {pct(r[2])}</span></span>')
    return f'<div class="ticker">{"".join(items)}</div>' if items else ''


# ---------------------------------------------------------------- study desk
def study_html(stories, plan, extras):
    parts = []
    les = extras['lesson']
    if les:
        parts.append(f'<div class="label">Today\'s lesson <span class="ai">AI</span></div>'
                     f'<p><b>{esc(les["concept"])}.</b> {esc(les["explanation"])}</p>'
                     f'<p><i>Apply it:</i> {esc(les["apply_it"])}</p>')
    elif plan['lead'] and plan['lead']['concepts']:
        s, c = plan['lead'], plan['lead']['concepts'][0]
        parts.append(f'<div class="label">Today\'s lesson</div><p><b>{esc(c)}.</b> {esc(s["definitions"].get(c, ""))}</p>'
                     f'<p><i>Apply it:</i> see the lead story, "{esc(s["headline"])}".</p>')
    if extras['questions']:
        parts.append('<div class="label">Questions to research <span class="ai">AI</span></div><ol>'
                     + ''.join(f'<li>{esc(q)}</li>' for q in extras['questions']) + '</ol>')
    parts.append('<div class="label">For every story, ask</div><p>What changed? Why does it matter? Who gains or loses? '
                 'What would change my view?</p>')
    seen = {}
    for s in stories:
        for c in s['concepts']:
            seen.setdefault(c, s['definitions'].get(c) or C.CONCEPTS.get(c, ('', ''))[1])
    if seen:
        parts.append('<div class="label">Terms in today\'s news</div><ul class="briefs cols">'
                     + ''.join(f'<li><b>{esc(c)}</b>: {esc(m)}</li>' for c, m in seen.items()) + '</ul>')
    return '<div class="study">' + ''.join(parts) + '</div>'


# ---------------------------------------------------------------- page
def build_page(stories, plan, tables, extras, failed, notes, now):
    today = now.date()
    by_desk, lead = plan['by_desk'], plan['lead']
    front = ([lead] if lead else []) + plan['secondary']
    front_urls = {s['url'] for s in front}
    deal_urls = {s['url'] for s in plan['top_deals']}

    def desk(name, cap=None, stage=False):
        rest = [s for s in by_desk.get(name, []) if s['url'] not in front_urls and s['url'] not in deal_urls]
        return desk_html(name, rest, extras, cap or C.DESK_CAPS.get(name, C.MAX_PER_DESK), stage)

    # --- front page
    main_col = ''
    if lead:
        main_col += lead_html(lead, extras)
    if plan['secondary']:
        main_col += '<div class="grid2">' + ''.join(item_html(s, extras) for s in plan['secondary']) + '</div>'
    side = market_read_html(tables, extras) + wire_html(plan['wire'], today) + watchlist_alerts(stories)
    front_html = f'<div class="front" id="front"><div>{main_col}</div><aside class="side">{side}</aside></div>'

    # --- markets
    markets = ('<h2 class="sec" id="markets">Markets</h2><div class="two"><div>' + index_board(tables) + '</div><div>'
               + quote_table('Volatility, rates, FX & commodities', tables.get('Macro'))
               + quote_table('My watchlist', tables.get('My watchlist')) + sector_heat(tables.get('Sectors')) + '</div></div>')

    # --- deals
    deals = '<h2 class="sec" id="deals">Deals &amp; capital markets</h2>'
    shown_deals = [s for s in plan['top_deals'] if s['url'] not in front_urls]   # not repeated from the front page
    if shown_deals:
        deals += '<div class="label">Top deals</div><div class="grid2">' + ''.join(
            item_html(s, extras, kicker=False) for s in shown_deals) + '</div>'
    radar = ''
    exclude = front_urls | deal_urls
    for cat in C.RADAR_ORDER:
        items = sorted([s for s in stories if s['deal_cat'] == cat and s['how'] == 'head' and s['url'] not in exclude],
                       key=lambda s: s['importance'], reverse=True)[:C.MAX_PER_RADAR_CATEGORY]
        if items:
            exclude |= {s['url'] for s in items}
            radar += f'<div class="desk"><div class="label">{esc(cat)}</div><ul class="briefs">' + ''.join(
                brief_li(s, stage=True) for s in items) + '</ul></div>'
    if radar:
        deals += f'<div class="cols">{radar}</div>'
    front_urls |= exclude - deal_urls          # anything shown above is not repeated in a desk below
    deals += '<div class="cols">' + ''.join(desk(n) for n in C.DESK_ORDER[:5]) + '</div>'

    # --- companies
    companies = ('<h2 class="sec" id="companies">Companies &amp; stocks</h2>' + earnings_table(extras['rows'])
                 + '<div class="cols">' + ''.join(desk(n) for n in (
                     'Companies & Earnings', 'Broker Calls & Stock Movers', 'Corporate Actions')) + '</div>')

    # --- policy and world
    policy = ('<h2 class="sec" id="policy">Economy, policy &amp; world</h2><div class="cols">' + ''.join(
        desk(n) for n in ('Central Banks & Policy', 'Macro Indicators', 'Market Pulse & Global Cues')) + '</div>')

    # --- study + low priority
    study = '<h2 class="sec" id="study">Study desk</h2>' + study_html(stories, plan, extras)
    low = [s for s in by_desk.get('Trading Ideas (low priority)', [])][:5]
    low_html = ''
    if low:
        low_html = (f'<details><summary>Trading ideas, low priority ({len(low)})</summary><ul class="briefs">'
                    + ''.join(brief_li(s) for s in low) + '</ul></details>')

    foot = ''.join(f'<p class="note">{esc(n)}</p>' for n in notes if n)
    foot += ('<p class="note">Every headline links to the original publisher. Parts marked AI were written by Gemini '
             'from the article text; figures that were not in the text are removed.</p>')
    if failed:
        foot += f'<p class="note"><b>Did not load:</b> {esc("; ".join(failed))}</p>'

    date_long = now.strftime('%A, ') + str(now.day) + now.strftime(' %B %Y')
    masthead = (
        '<header class="mast"><div class="top">'
        f'<span>{esc(date_long)}</span><span><span class="live"></span><span id="upd">updated {now.strftime("%H:%M")} IST</span></span>'
        '</div><h1>The Morning Brief</h1><div class="sub">Markets · Deals · Companies · Policy</div></header>')
    nav = ('<nav><a href="#front">Front page</a><a href="#markets">Markets</a><a href="#deals">Deals</a>'
           '<a href="#companies">Companies</a><a href="#policy">Policy &amp; world</a><a href="#study">Study</a></nav>')

    script = SCRIPT.replace('%REFRESH%', str(int(C.REFRESH_SECONDS * 1000)))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        '<meta name="theme-color" content="#161513"><title>The Morning Brief</title>'
        f'<style>{CSS}</style></head><body data-built="{now.isoformat()}"><div class="wrap">'
        + masthead + ticker_html(tables) + nav + front_html + markets + deals + companies + policy + study
        + low_html + foot + '</div><div id="newed" onclick="location.reload()">New edition available. Tap to load.</div>'
        f'<script>{script}</script></body></html>'
    )
