"""Small helpers shared by build_brief.py, ai.py and render.py."""
import html
import re
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')


def clean_text(text):
    text = html.unescape(text or '')
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def has(text, words):
    """True if any word/phrase appears as a whole word (so 'lp' doesn't match 'help')."""
    def hit(w):
        tail = r'(?!\w)' if w[-1].isalnum() else ''   # 'raises ₹' ends in a symbol
        return re.search(r'(?<!\w)' + re.escape(w) + tail, text)
    return any(hit(w) for w in words)


def full_text(a):
    return (a['headline'] + ' ' + a['summary']).lower()
