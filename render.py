"""Turns the data into one newspaper-style HTML page (no external fonts, scripts or images)."""
import html
import re
from datetime import datetime, timezone

import config as C
from util import IST, has

esc = html.escape

# ---------------------------------------------------------------- style + script
CSS = """
:root{--paper:#f7f3ea;--ink:#171715;--mut:#6a675f;--rule:#d9d3c4;--link:#7a1f1f;--card:#fffdf8;
--chipbg:#efe8d6;--chipfg:#4a3f1d;--up:#0b6b2d;--down:#b3261e;--accent:#8c1c13;--warn:#9a5b00}
@media (prefers-color-scheme:dark){:root{--paper:#161513;--ink:#ece8dd;--mut:#a29d90;--rule:#38352e;
--link:#e8a07a;--card:#1d1b18;--chipbg:#2c2819;--chipfg:#e8d9a8;--up:#4cc26f;--down:#ff7a7a;--accent:#e8a07a;--warn:#e0a84a}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 Georgia,'Times New Roman',serif}
.ui,.meta,table,nav,.ticker,.label,.note,.chip,.ai,.kicker,time,button,.tier,summary{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
a{color:inherit;text-decoration:none}a:hover{text-decoration:underline;color:var(--link)}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 60px}
.mast{text-align:center;padding:14px 0 8px;border-bottom:3px double var(--ink)}
.mast .top{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;font-size:12px;
color:var(--mut);text-transform:uppercase;letter-spacing:.06em;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.mast h1{font-size:clamp(34px,7vw,66px);margin:8px 0 2px;font-weight:700;letter-spacing:-.01em;line-height:1.05}
.mast .sub{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--mut);
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
.up{color:var(--up)}.down{color:var(--down)}.stale{color:var(--warn);font-weight:600}
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
border-radius:3px;padding:0 4px;color:var(--mut);margin-left:6px;vertical-align:middle;white-space:nowrap;font-style:normal}
.tier{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;border-radius:3px;padding:0 5px;
margin-left:4px;border:1px solid var(--rule);color:var(--mut);white-space:nowrap}
.t-primary{color:var(--up);border-color:var(--up)}
.save{font-size:11px;border:1px solid var(--rule);background:transparent;color:var(--mut);border-radius:10px;
padding:0 8px;margin-left:8px;cursor:pointer}.save.on{color:var(--accent);border-color:var(--accent)}
.grid2{display:grid;grid-template-columns:minmax(0,1fr);gap:0 26px;margin-top:20px}
@media (min-width:640px){.grid2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.item{padding:12px 0;border-top:1px solid var(--rule)}
.item h3{font-size:20px;line-height:1.2;margin:2px 0 4px}
.sum{font-size:15px;margin:0;color:var(--ink)}
details.blk{margin-top:38px}
summary.sec{font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.16em;border-top:3px double var(--ink);
border-bottom:1px solid var(--rule);padding:7px 0;margin:0 0 14px;cursor:pointer;list-style:none}
summary.sec::-webkit-details-marker{display:none}
summary.sec::after{content:'\\25BE';float:right;color:var(--mut)}
details.blk:not([open]) summary.sec::after{content:'\\25B8'}
.label{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;border-top:2px solid var(--ink);
padding-top:6px;margin:22px 0 6px}
.cols{column-gap:30px;column-rule:1px solid var(--rule)}
@media (min-width:760px){.cols{column-count:2}}
.cols>*{break-inside:avoid}
.briefs{list-style:none;margin:0;padding:0}
.briefs li{padding:7px 0;border-bottom:1px solid var(--rule);font-size:16px;line-height:1.3}
.briefs li a.t{font-weight:600}
.side h2{font:700 12px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;text-transform:uppercase;
letter-spacing:.14em;border-top:2px solid var(--ink);padding-top:6px;margin:0 0 8px}
.side section{margin-bottom:26px}
.read p{margin:0 0 8px;font-size:15px}
.top5{border:1px solid var(--ink);border-top-width:4px;padding:6px 16px 10px;margin-bottom:22px;background:var(--card)}
.top5 h2{font:700 12px sans-serif;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;text-transform:uppercase;
letter-spacing:.16em;margin:8px 0 4px}
.top5 ol{margin:0;padding-left:22px}.top5 li{padding:5px 0;font-size:16px;line-height:1.3}
.wire{list-style:none;margin:0;padding:0}
.wire li{display:grid;grid-template-columns:46px minmax(0,1fr);gap:8px;padding:7px 0;border-bottom:1px solid var(--rule);
font-size:14px;line-height:1.3}
.wire time{font-size:12px;font-weight:700;color:var(--accent);padding-top:1px}
.wire .meta{margin-top:2px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
td,th{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut)}
.num{text-align:right;font-variant-numeric:tabular-nums}.day{color:var(--mut);font-size:12px;text-align:right}
.region td{font-weight:700;color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.08em;padding-top:14px}
.hd td{color:var(--mut);font-size:11px;text-transform:uppercase}
.two{display:grid;grid-template-columns:minmax(0,1fr);gap:0 30px}
@media (min-width:900px){.two{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)}}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px;margin-top:6px}
.tile{border:1px solid var(--rule);padding:7px 8px;font-size:13px;display:flex;flex-direction:column;background:var(--card);
font-family:-apple-system,'Segoe UI',Roboto,sans-serif}.tile b{font-size:15px}
.dealcard{background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--accent);padding:10px 14px;margin:10px 0;
font-size:13px;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.dealcard h4{margin:0 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)}
.dealcard dl{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:3px 14px;margin:6px 0}
.dealcard dt{color:var(--mut)}.dealcard dd{margin:0}.nd{color:var(--mut)}
.dealcard p{margin:6px 0 0}.dealcard .ai{white-space:normal}
.cards3{display:grid;grid-template-columns:minmax(0,1fr);gap:0 18px}
@media (min-width:900px){.cards3{grid-template-columns:repeat(3,minmax(0,1fr))}}
.note{font-size:12px;color:var(--mut);margin:8px 0}
details>summary{cursor:pointer}
details.more{margin-top:3px}details.more>summary{font-size:12px;color:var(--mut);font-weight:600}
details.more .meta{margin:2px 0 2px 12px}
.study p{margin:4px 0 10px;font-size:16px}
.conflict{border:1px solid var(--warn);border-left-width:4px;padding:6px 14px;margin:14px 0;background:var(--card);font-size:14px}
.conflict b{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--warn)}
.rng{display:inline-block;position:relative;width:70px;height:6px;background:var(--rule);border-radius:3px;vertical-align:middle;margin:0 6px}
.rng i{position:absolute;top:-3px;width:3px;height:12px;background:var(--accent);border-radius:1px}
.badge{display:inline-block;font-size:10px;font-weight:700;border:1px solid var(--accent);color:var(--accent);border-radius:3px;
padding:0 4px;margin:0 3px 2px 0;white-space:nowrap}
#saved{display:none;margin-top:12px;border:1px solid var(--rule);padding:4px 14px;background:var(--card)}
#saved summary{font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.1em;padding:6px 0}
#saved ul{list-style:none;margin:0 0 6px;padding:0}#saved li{padding:4px 0;font-size:14px;display:flex;gap:10px;justify-content:space-between}
#saved .rm{font-size:11px;border:0;background:none;color:var(--mut);cursor:pointer;text-decoration:underline}
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

  // nav links re-open a collapsed section
  Array.prototype.forEach.call(document.querySelectorAll('nav a'), function(a){
    a.addEventListener('click', function(){
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if (t && t.tagName === 'DETAILS') t.open = true;
    });
  });

  // save for later (kept in this browser only)
  var KEY = 'mb_saved_v1';
  function load(){ try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function store(l){ try { localStorage.setItem(KEY, JSON.stringify(l)); } catch (e) {} }
  var saved = load();
  function mark(){
    Array.prototype.forEach.call(document.querySelectorAll('.save'), function(b){
      var on = saved.some(function(s){ return s.u === b.getAttribute('data-u'); });
      b.textContent = on ? '\\u2605 Saved' : '\\u2606 Save';
      b.className = on ? 'save on' : 'save';
    });
  }
  function render(){
    var box = document.getElementById('saved'), list = document.getElementById('savedlist'), n = document.getElementById('savedn');
    if (!box) return;
    n.textContent = saved.length;
    box.style.display = saved.length ? 'block' : 'none';
    list.innerHTML = '';
    saved.forEach(function(it, i){
      var li = document.createElement('li'), a = document.createElement('a'), b = document.createElement('button');
      a.href = it.u; a.target = '_blank'; a.rel = 'noopener'; a.textContent = it.t;
      b.className = 'rm'; b.textContent = 'remove';
      b.onclick = function(){ saved.splice(i, 1); store(saved); render(); mark(); };
      li.appendChild(a); li.appendChild(b); list.appendChild(li);
    });
  }
  document.addEventListener('click', function(e){
    var b = e.target.closest ? e.target.closest('.save') : null;
    if (!b) return;
    var u = b.getAttribute('data-u'), i = -1;
    saved.forEach(function(s, k){ if (s.u === u) i = k; });
    if (i > -1) saved.splice(i, 1); else saved.unshift({u: u, t: b.getAttribute('data-t')});
    saved = saved.slice(0, 60); store(saved); render(); mark();
  });
  render(); mark();
})();
"""


# ---------------------------------------------------------------- small helpers
def safe(u):
    """Only real web links; anything else (e.g. javascript:) becomes a dead link."""
    return u if str(u).startswith(('http://', 'https://')) else '#'


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


def asof_label(asof, today_date):
    """('live' | date | date + stale, css class). Stale = last price is more than 4 days old."""
    if asof == today_date.strftime('%d %b'):
        return 'live', ''
    try:
        d = datetime.strptime(f'{asof} {today_date.year}', '%d %b %Y').date()
        if d > today_date:
            d = d.replace(year=d.year - 1)
        if (today_date - d).days > 4:
            return f'{asof} · stale', 'stale'
    except ValueError:
        pass
    return asof, ''


def link(s, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{esc(safe(s["url"]))}" target="_blank" rel="noopener">{esc(s["headline"])}</a>'


def tier_of(s):
    if s['desk'].startswith('Trading Ideas'):
        return 'Trading idea'
    return C.SOURCE_TIERS.get(s['source'], '')


def meta_line(s, stage=False):
    src = esc(s['source'])
    tier = tier_of(s)
    if tier:
        cls = 't-primary' if tier == 'Primary' else ''
        src += f' <span class="tier {cls}">{esc(tier)}</span>'
    bits = [src, esc(ago(s['published']))]
    if stage and s.get('stage'):
        bits.append(esc(s['stage']))
    return ' · '.join(b for b in bits if b)


def save_btn(s):
    return (f'<button class="save" type="button" data-u="{esc(safe(s["url"]))}" '
            f'data-t="{esc(s["headline"])}">&#9734; Save</button>')


def also_line(s):
    seen, uniq = {s['source']}, []
    for r in s['related']:
        if r['source'] not in seen:
            seen.add(r['source'])
            uniq.append(r)
    if not uniq:
        return ''
    links = ''.join(f'<div class="meta"><a href="{esc(safe(r["url"]))}" target="_blank" rel="noopener">'
                    f'{esc(r["source"])}: {esc(r["headline"][:90])}</a></div>' for r in uniq[:4])
    return f'<details class="more"><summary>More coverage ({len(uniq)})</summary>{links}</details>'


def summary_text(s, ai_text, limit):
    text = ai_text or s['summary']
    if not ai_text and text.lower().startswith(s['headline'].lower()[:40]):
        return ''
    return text if len(text) <= limit else text[:limit].rsplit(' ', 1)[0] + '…'


def chips(s):
    return ('<div class="chips">' + ''.join(f'<span class="chip">{esc(c)}</span>' for c in s['concepts']) + '</div>'
            if s['concepts'] else '')


def why_line(s, extras):
    """Mandatory for stories at or above the importance threshold: AI sentence if there is one, else the desk template."""
    if s['importance'] < C.WHY_MIN_IMPORTANCE:
        return ''
    ai_text = extras['whys'].get(s['id'])
    text = ai_text or s['why']
    if not text:
        return ''
    badge = '<span class="ai">AI</span>' if ai_text else ''
    return f'<div class="why"><b>Why it matters:</b> {esc(text)}{badge}</div>'


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
            + f'<div class="meta">{meta_line(s)}{save_btn(s)}</div>{deal_card(extras["deals"].get(s["id"]))}'
            + why_line(s, extras) + chips(s) + also_line(s) + '</article>')


def item_html(s, extras, stage=False, kicker=True):
    ai_text = extras['summaries'].get(s['id'])
    text = summary_text(s, ai_text, 230)
    return (f'<div class="item">' + (f'<div class="kicker">{esc(s["desk"])}</div>' if kicker else '')
            + f'<h3>{link(s)}</h3>'
            + (f'<p class="sum">{esc(text)}{"<span class=ai>AI</span>" if ai_text else ""}</p>' if text else '')
            + f'<div class="meta">{meta_line(s, stage)}{save_btn(s)}</div>'
            + deal_card(extras['deals'].get(s['id'])) + why_line(s, extras) + also_line(s) + '</div>')


def brief_li(s, stage=False):
    return f'<li>{link(s, "t")}<div class="meta">{meta_line(s, stage)}{save_btn(s)}</div></li>'


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


def block(id_, title, inner):
    return f'<details class="blk" id="{id_}" open><summary class="sec">{esc(title)}</summary>{inner}</details>'


# ---------------------------------------------------------------- tables
def pct_cell(v):
    if v is None:
        return '<td class="num">—</td>'
    return f'<td class="num {updown(v)}">{v:+.2f}%</td>'


def index_board(tables):
    today = datetime.now(IST).date()
    rows = ''
    for region, members in C.GLOBAL_INDICES.items():
        data = tables.get('Region: ' + region)
        if not data:
            continue
        order = list(members)
        rows += f'<tr class="region"><td colspan="6">{esc(region)}</td></tr>'
        for name, last, day, asof, week, ytd, *_ in sorted(data, key=lambda r: order.index(r[0])):
            label, cls = asof_label(asof, today)
            rows += (f'<tr><td>{esc(name)}</td><td class="num">{last:,.2f}</td>{pct_cell(day)}{pct_cell(week)}'
                     f'{pct_cell(ytd)}<td class="day {cls}">{esc(label)}</td></tr>')
    if not rows:
        return ''
    head = ('<tr class="hd"><td>Index</td><td class="num">Last</td><td class="num">Day</td><td class="num">1W</td>'
            '<td class="num">YTD</td><td class="day">As of</td></tr>')
    return (f'<div class="label">Global indices</div><div class="scroll"><table>{head}{rows}</table></div>'
            '<p class="note">"live" = the market has traded today, so the price can be delayed intraday rather than a close. '
            'A date is that market\'s last close (each market\'s own trading day). "stale" = last price is over 4 days old: '
            'a holiday or a data problem. MSCI rows use tracking ETFs.</p>')


def quote_table(title, rows):
    if not rows:
        return ''
    today = datetime.now(IST).date()
    body = ''
    for name, last, change, day, *_ in rows:
        arrow = '▲' if change >= 0 else '▼'
        label, cls = asof_label(day, today)
        body += (f'<tr><td>{esc(name)}</td><td class="num">{last:,.2f}</td>'
                 f'<td class="num {updown(change)}">{arrow} {change:+.2f}%</td><td class="day {cls}">{esc(label)}</td></tr>')
    return f'<div class="label">{esc(title)}</div><div class="scroll"><table>{body}</table></div>'


def sector_heat(rows):
    if not rows:
        return ''
    tiles = ''.join(f'<div class="tile {updown(r[2])}"><span>{esc(r[0])}</span><b>{r[2]:+.2f}%</b></div>'
                    for r in sorted(rows, key=lambda r: r[2], reverse=True))
    return f'<div class="label">Sector heat map</div><div class="tiles">{tiles}</div>'


def watchlist_table(tables, stories):
    rows = tables.get('My watchlist')
    if not rows:
        return ''
    today = datetime.now(IST).date()
    body = ''
    for name, last, change, asof, week, ytd, *rest in rows:
        hi, lo = (rest + [None, None])[:2]
        label, cls = asof_label(asof, today)
        rng = '—'
        if hi and lo and hi > lo:
            pos = max(0, min(100, (last - lo) / (hi - lo) * 100))
            rng = (f'{lo:,.0f}<span class="rng"><i style="left:{pos:.0f}%"></i></span>{hi:,.0f}'
                   f'<div class="meta">{(last / hi - 1) * 100:+.1f}% vs 52-wk high</div>')
        names = C.WATCHLIST_ALIASES.get(name, [name.lower()])
        hits = sorted([s for s in stories if has(s['headline'].lower(), names)],
                      key=lambda s: s['importance'], reverse=True)
        news = link(hits[0]) if hits else '<span class="nd">no headline today</span>'
        badges = ''
        for label_, words in C.WATCHLIST_ALERT_WORDS.items():
            if any(has(s['headline'].lower(), words) for s in hits):
                badges += f'<span class="badge">{esc(label_)}</span>'
        note = C.WATCHLIST_NOTES.get(name, {})
        watching = esc(note.get('catalyst', ''))
        if note.get('thesis'):
            watching += f'<div class="meta">Thesis: {esc(note["thesis"])}</div>'
        body += (f'<tr><td><b>{esc(name)}</b><div class="meta {cls}">{esc(label)}</div></td>'
                 f'<td class="num">{last:,.2f}</td><td class="num {updown(change)}">{change:+.2f}%</td>'
                 f'<td>{rng}</td><td>{news}</td><td>{badges}</td><td>{watching}</td></tr>')
    head = ('<tr><th>Stock</th><th class="num">Price</th><th class="num">Day</th><th>52-week range</th>'
            '<th>Latest headline</th><th>Alerts</th><th>Watching for</th></tr>')
    return (f'<div class="label">My watchlist</div><div class="scroll"><table>{head}{body}</table></div>'
            '<p class="note">Headlines are matched by company name. "Watching for" and thesis are your own notes (edit them in config.py).</p>')


def flows_html(plan):
    items = plan.get('flows') or []
    if not items:
        return ''
    lis = ''.join(f'<li>{link(s, "t")}<div class="meta">{meta_line(s)}</div></li>' for s in items)
    return ('<div class="label">Investor flows in the news (FPI / DII)</div>'
            f'<ul class="briefs">{lis}</ul><p class="note">Figures are as reported in these articles. '
            'Official data: NSDL (FPI) and the exchanges (DII).</p>')


def macro_manual_html():
    rows = [m for m in C.MACRO_MANUAL if str(m.get('value', '')).strip()]
    if not rows:
        return ''
    body = ''.join(
        f'<tr><td>{esc(m["name"])}</td><td class="num"><b>{esc(m["value"])}</b></td><td class="day">{esc(m.get("as_of", ""))}</td>'
        f'<td class="day"><a href="{esc(safe(m.get("source", "")))}" target="_blank" rel="noopener">source</a></td></tr>' for m in rows)
    return (f'<div class="label">India macro snapshot</div><div class="scroll"><table>{body}</table></div>'
            '<p class="note">Entered by you from the primary sources (config.py), not fetched automatically.</p>')


def conflicts_html(plan):
    out = ''
    for c in plan.get('conflicts') or []:
        out += (f'<div class="conflict"><b>Check: headlines disagree on {esc(c["topic"])}</b>'
                f'<div>{link(c["up"])}<div class="meta">{esc(c["up"]["source"])} · reads as up</div></div>'
                f'<div>{link(c["down"])}<div class="meta">{esc(c["down"]["source"])} · reads as down</div></div>'
                '<div class="meta">They may cover different time periods. Check the dates before drawing a conclusion.</div></div>')
    return out


def earnings_html(rows):
    if not rows:
        return ''

    def cell(v):
        return f'<td class="{"nd" if v == "Not disclosed" else ""}">{esc(v if v != "Not disclosed" else "—")}</td>'

    body = ''.join(
        f'<tr><td><a href="{esc(safe(r["url"]))}" target="_blank" rel="noopener"><b>{esc(r["company"])}</b></a></td>'
        f'<td>{esc(r["period"])}</td>' + ''.join(cell(r[k]) for k in ('result', 'revenue', 'ebitda', 'profit', 'margin', 'driver'))
        + '</tr>' for r in rows)
    out = ('<div class="label">Results at a glance <span class="ai">AI · only what the report states</span></div>'
           '<div class="scroll"><table><tr><th>Company</th><th>Period</th><th>Result</th><th>Revenue</th><th>EBITDA</th>'
           f'<th>Profit</th><th>Margin</th><th>Driver</th></tr>{body}</table></div>')
    cards = ''
    for r in [r for r in rows if r.get('card')][:C.EARNINGS_CARDS]:
        fields = [('Result vs expectations', 'result'), ('Revenue growth', 'revenue'), ('EBITDA', 'ebitda'),
                  ('Profit growth', 'profit'), ('Margin', 'margin'), ('Net debt', 'net_debt'),
                  ('Key positive', 'key_positive'), ('Key negative', 'key_negative'),
                  ('Broker view', 'broker_view'), ('What to watch', 'watch')]
        dl = ''.join(f'<dt>{esc(lbl)}</dt><dd class="{"nd" if r[k] == "Not disclosed" else ""}">{esc(r[k])}</dd>'
                     for lbl, k in fields)
        cards += (f'<div class="dealcard"><h4>{esc(r["company"])} · {esc(r["period"])}</h4><dl>{dl}</dl></div>')
    if cards:
        out += f'<div class="cards3">{cards}</div><p class="note">"Not disclosed" means the article did not say.</p>'
    return out


def deal_log_html(rows):
    if not rows:
        return ''
    body = ''.join(
        f'<tr><td>{esc((r.get("published") or r.get("first_seen", ""))[:10])}</td>'
        f'<td><a href="{esc(safe(r.get("url", "")))}" target="_blank" rel="noopener">{esc(r.get("headline", ""))}</a></td>'
        f'<td>{esc(r.get("deal_type", ""))}</td><td>{esc(r.get("value", "") or "—")}</td>'
        f'<td>{esc(r.get("stake", "") or "—")}</td><td>{esc(r.get("status", ""))}</td></tr>' for r in rows)
    return (f'<details class="more"><summary class="label" style="border-top:2px solid var(--ink)">Deal log: latest {len(rows)} '
            '(full history in <a href="deals.csv">deals.csv</a>)</summary><div class="scroll"><table><tr><th>Date</th><th>Deal</th><th>Type</th>'
            f'<th>Value</th><th>Stake</th><th>Status</th></tr>{body}</table></div>'
            '<p class="note">Value and stake are copied as written in the headline or summary. Blank means unknown, never guessed.</p></details>')


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
    """Numbers and interpretation are kept apart: the numbers always come from the tables."""
    nums = rule_read(tables)
    out = ''
    if nums:
        out += '<h2>Market read: the numbers</h2>' + ''.join(f'<p>{esc(l)}</p>' for l in nums)
    if extras['read']:
        out += (f'<h2 style="margin-top:14px">What it may mean <span class="ai">AI · {esc(extras["read_at"])} IST</span></h2>'
                + ''.join(f'<p>{esc(l)}</p>' for l in extras['read'])
                + '<p class="note">AI-written from today\'s headlines; any cause named comes from a headline. Check the sources.</p>')
    return f'<section class="read">{out}</section>' if out else ''


def wire_html(wire, today):
    if not wire:
        return ''
    lis = ''.join(f'<li><time title="{esc(str(s["published"]))}">{esc(clock(s["published"], today))}</time>'
                  f'<div>{link(s)}<div class="meta">{meta_line(s)}</div></div></li>' for s in wire)
    return f'<section><h2><span class="live"></span>Latest wire</h2><ul class="wire">{lis}</ul></section>'


def ticker_html(tables):
    items = []
    for name in C.TICKER:
        r = find_quote(tables, name)
        if r:
            arrow = '▲' if r[2] >= 0 else '▼'
            short = name.replace(' ($)', '').replace(' ($/oz)', '').replace(' (%)', '')
            items.append(f'<span><b>{esc(short)}</b> {r[1]:,.2f} <span class="{updown(r[2])}">{arrow} {pct(r[2])}</span></span>')
    return f'<div class="ticker">{"".join(items)}</div>' if items else ''


def top5_html(plan, tables):
    items = []
    n, sx = find_quote(tables, 'Nifty 50'), find_quote(tables, 'Sensex')
    secs = sorted(tables.get('Sectors', []), key=lambda r: r[2], reverse=True)
    if n:
        t = f'India: Nifty {pct(n[2])}' + (f', Sensex {pct(sx[2])}' if sx else '')
        if len(secs) >= 2:
            t += f'; {secs[0][0]} led ({pct(secs[0][2])}), {secs[-1][0]} lagged ({pct(secs[-1][2])})'
        items.append(esc(t) + '.')
    movers = []
    for region in C.GLOBAL_INDICES:
        if region != 'India' and 'ETF' not in region:
            movers += tables.get('Region: ' + region, [])
    big = sorted(movers, key=lambda r: abs(r[2]), reverse=True)[:2]
    if big and abs(big[0][2]) >= 1:
        items.append('Biggest global index moves: ' + ', '.join(f'{esc(r[0])} {pct(r[2])}' for r in big) + '.')
    by_desk, deals = plan['by_desk'], plan['top_deals']
    if deals:
        items.append('Deal: ' + link(deals[0]))
    ipos = [s for s in by_desk.get('IPOs & Block Deals', []) if s['how'] == 'head' and s not in deals]
    if ipos:
        items.append('IPO / block deal: ' + link(ipos[0]))
    pol = sorted(by_desk.get('Central Banks & Policy', []) + by_desk.get('Macro Indicators', []),
                 key=lambda s: s['importance'], reverse=True)
    if pol:
        items.append('Macro / policy: ' + link(pol[0]))
    if not items:
        return ''
    return '<section class="top5"><h2>Top 5</h2><ol>' + ''.join(f'<li>{i}</li>' for i in items[:5]) + '</ol></section>'


def watchlist_alerts_mini(stories):
    return ''


# ---------------------------------------------------------------- study desk
def study_html(stories, plan, extras):
    parts = []
    les = extras['lesson']
    if les:
        parts.append(f'<div class="label">Today\'s lesson <span class="ai">AI</span></div>'
                     f'<p><b>{esc(les["concept"])}.</b> {esc(les["explanation"])}</p>'
                     f'<p><i>Apply it:</i> {esc(les["apply_it"])}</p>')
    else:
        best = None
        for s in ([plan['lead']] if plan['lead'] else []) + plan['secondary'] + stories:
            for c in s['concepts']:
                if c in C.CONCEPT_PRIORITY and (best is None or C.CONCEPT_PRIORITY.index(c) < best[0]):
                    best = (C.CONCEPT_PRIORITY.index(c), c, s)
        if best:
            _, c, s = best
            parts.append(f'<div class="label">Today\'s lesson</div><p><b>{esc(c)}.</b> {esc(s["definitions"].get(c, ""))}</p>'
                         f'<p><i>Apply it:</i> see "{esc(s["headline"])}".</p>')
    if extras['questions']:
        parts.append('<div class="label">Questions to research <span class="ai">AI</span></div><ol>'
                     + ''.join(f'<li>{esc(q)}</li>' for q in extras['questions']) + '</ol>')
    else:
        qs, seen_desks = [], set()
        for s in ([plan['lead']] if plan['lead'] else []) + plan['top_deals'] + plan['secondary'] + plan['earnings']:
            tpl = C.RESEARCH_BY_DESK.get(s['desk'])
            if tpl and s['desk'] not in seen_desks:
                seen_desks.add(s['desk'])
                qs.append(tpl.replace('{h}', s['headline']))
            if len(qs) == 3:
                break
        if qs:
            parts.append('<div class="label">Questions to research</div><ol>' + ''.join(f'<li>{esc(q)}</li>' for q in qs) + '</ol>')
    parts.append('<div class="label">For every story, ask</div><p>What changed? Why does it matter? Who gains or loses? '
                 'What would change my view?</p>')
    seen = {}
    for s in stories:
        for c in s['concepts']:
            seen.setdefault(c, s['definitions'].get(c) or C.CONCEPTS.get(c, ('', ''))[1])
    if seen:
        parts.append('<div class="label">Terms in today\'s news</div><ul class="briefs cols">'
                     + ''.join(f'<li><b>{esc(c)}</b>: {esc(m)}</li>' for c, m in seen.items()) + '</ul>')
    links = ' · '.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a>' for n, u in C.PRIMARY_LINKS)
    parts.append(f'<div class="label">Check the primary sources</div><p class="note">{links}. For any IPO or deal, read the '
                 'DRHP/RHP, the exchange announcement and the investor presentation.</p>')
    return '<div class="study">' + ''.join(parts) + '</div>'


# ---------------------------------------------------------------- page
def build_page(stories, plan, tables, extras, failed, notes, now, debug=''):
    today = now.date()
    by_desk, lead = plan['by_desk'], plan['lead']
    front = ([lead] if lead else []) + plan['secondary']
    shown = {s['url'] for s in front}
    deal_urls = {s['url'] for s in plan['top_deals']}
    shown |= {s['url'] for s in plan.get('flows') or []}
    shown |= {r['url'] for r in extras['rows']}

    def desk(name, cap=None, stage=False):
        rest = [s for s in by_desk.get(name, []) if s['url'] not in shown and s['url'] not in deal_urls]
        return desk_html(name, rest, extras, cap or C.DESK_CAPS.get(name, C.MAX_PER_DESK), stage)

    # --- front page
    main_col = top5_html(plan, tables)
    if lead:
        main_col += lead_html(lead, extras)
    if plan['secondary']:
        main_col += '<div class="grid2">' + ''.join(item_html(s, extras) for s in plan['secondary']) + '</div>'
    side = market_read_html(tables, extras) + wire_html(plan['wire'], today)
    front_html = f'<div class="front" id="front"><div>{main_col}</div><aside class="side">{side}</aside></div>'

    # --- markets
    markets = block('markets', 'Markets',
                    '<div class="two"><div>' + index_board(tables) + '</div><div>'
                    + quote_table('Volatility, rates, FX & commodities', tables.get('Macro'))
                    + sector_heat(tables.get('Sectors')) + '</div></div>'
                    + watchlist_table(tables, stories) + conflicts_html(plan) + flows_html(plan) + macro_manual_html())

    # --- deals
    deals_inner = ''
    shown_deals = [s for s in plan['top_deals'] if s['url'] not in shown]
    if shown_deals:
        deals_inner += '<div class="label">Top deals</div><div class="grid2">' + ''.join(
            item_html(s, extras, kicker=False) for s in shown_deals) + '</div>'
    radar = ''
    exclude = shown | deal_urls
    for cat in C.RADAR_ORDER:
        items = sorted([s for s in stories if s['deal_cat'] == cat and s['how'] == 'head' and s['url'] not in exclude],
                       key=lambda s: s['importance'], reverse=True)[:C.MAX_PER_RADAR_CATEGORY]
        if items:
            exclude |= {s['url'] for s in items}
            radar += f'<div class="desk"><div class="label">{esc(cat)}</div><ul class="briefs">' + ''.join(
                brief_li(s, stage=True) for s in items) + '</ul></div>'
    if radar:
        deals_inner += f'<div class="cols">{radar}</div>'
    shown |= exclude - deal_urls
    desks_html = ''.join(desk(n) for n in C.DESK_ORDER[:5])
    deals_inner += f'<div class="cols">{desks_html}</div>'
    if not (shown_deals or radar or desks_html):
        deals_inner += '<p class="note">No further deal news beyond the front page right now.</p>'
    deals_inner += deal_log_html(extras.get('deal_log') or [])
    deals = block('deals', 'Deals & capital markets', deals_inner)

    # --- companies
    companies = block('companies', 'Companies & stocks', earnings_html(extras['rows']) + '<div class="cols">' + ''.join(
        desk(n) for n in ('Companies & Earnings', 'Broker Calls & Stock Movers', 'Corporate Actions')) + '</div>')

    # --- policy and world
    policy = block('policy', 'Economy, policy & world', '<div class="cols">' + ''.join(
        desk(n) for n in ('Central Banks & Policy', 'Macro Indicators', 'Market Pulse & Global Cues')) + '</div>')

    # --- study + low priority
    study = block('study', 'Study desk', study_html(stories, plan, extras))
    low = by_desk.get('Trading Ideas (low priority)', [])[:5]
    low_html = ''
    if low:
        low_html = (f'<details><summary class="note"><b>Trading ideas, low priority ({len(low)})</b></summary><ul class="briefs">'
                    + ''.join(brief_li(s) for s in low) + '</ul></details>')

    foot = ''.join(f'<p class="note">{esc(n)}</p>' for n in notes if n)
    foot += ('<p class="note">Every headline links to the original publisher. Parts marked AI were written by Gemini from the '
             'article text; figures that were not in the text are removed. Badges: Primary = regulator release; Startup press = '
             'trade publication; no badge = mainstream business press; Trading idea = low priority.</p>')
    if failed:
        foot += f'<p class="note"><b>Did not load:</b> {esc("; ".join(failed))}</p>'
    if debug:
        foot += '<!-- ' + esc(debug).replace('--', '- -') + ' -->'

    body = front_html + markets + deals + companies + policy + study + low_html
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    minutes = max(1, round(words / 230))

    date_long = now.strftime('%A, ') + str(now.day) + now.strftime(' %B %Y')
    masthead = (
        '<header class="mast"><div class="top">'
        f'<span>{esc(date_long)} · about {minutes} min read</span><span><span class="live"></span>'
        f'<span id="upd">updated {now.strftime("%H:%M")} IST</span></span>'
        '</div><h1>The Morning Brief</h1><div class="sub">Markets · Deals · Companies · Policy</div></header>')
    nav = ('<nav><a href="#front">Front page</a><a href="#markets">Markets</a><a href="#deals">Deals</a>'
           '<a href="#companies">Companies</a><a href="#policy">Policy &amp; world</a><a href="#study">Study</a></nav>')
    saved = ('<details id="saved"><summary>Saved for later (<span id="savedn">0</span>)</summary><ul id="savedlist"></ul>'
             '<p class="note">Saved on this device only.</p></details>')

    script = SCRIPT.replace('%REFRESH%', str(int(C.REFRESH_SECONDS * 1000)))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        '<meta name="theme-color" content="#161513"><title>The Morning Brief</title>'
        f'<style>{CSS}</style></head><body data-built="{now.isoformat()}"><div class="wrap">'
        + masthead + ticker_html(tables) + nav + saved + body + foot
        + '</div><div id="newed" onclick="location.reload()">New edition available. Tap to load.</div>'
        f'<script>{script}</script></body></html>'
    )
