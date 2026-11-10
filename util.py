"""Small helpers shared by build_brief.py, ai.py and render.py."""
import html
import re
import threading
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


def run_with_timeout(fn, seconds, *args):
    """Runs fn(*args) in a background thread and gives up after `seconds`.
    A hung call is abandoned (daemon thread), so it can never block the build."""
    box = {}

    def target():
        try:
            box['value'] = fn(*args)
        except BaseException as err:          # noqa: BLE001 - re-raised in the caller
            box['error'] = err

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)
    if t.is_alive():
        raise TimeoutError(f'timed out after {seconds}s')
    if 'error' in box:
        raise box['error']
    return box.get('value')
