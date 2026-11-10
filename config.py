"""Everything you are likely to edit lives in this file.

build_brief.py does the work; this file only holds settings and word lists.
"""

# ---------- News sources (name -> RSS URL) ----------
FEEDS = {
    'ET Markets': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'ET Top Stories': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    'Mint Markets': 'https://www.livemint.com/rss/markets',
    'Mint Companies': 'https://www.livemint.com/rss/companies',
    'Business Standard Markets': 'https://www.business-standard.com/rss/markets-106.rss',
    'Inc42': 'https://inc42.com/feed/',
    # Added for stock news. Not yet verified: if one is wrong it shows under "Did not load".
    'ET Stocks': 'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
    'Business Standard Companies': 'https://www.business-standard.com/rss/companies-101.rss',
    'BusinessLine Markets': 'https://www.thehindubusinessline.com/markets/stock-markets/feeder/default.rss',
}

ITEMS_PER_SOURCE = 12      # newest N items taken from each feed
MAX_AGE_HOURS = 48         # ignore anything older than this
MAX_TOP_DEALS = 5
MAX_PER_RADAR_CATEGORY = 6
MAX_PER_DESK = 10
DESK_CAPS = {'Market Pulse & Global Cues': 6}   # per-desk override of MAX_PER_DESK
# Stock-news desks are decided by the headline only (summaries often mention 'upgrades' etc. in passing).
SUMMARY_PASS_SKIP = {'Companies & Earnings', 'Broker Calls & Stock Movers', 'Corporate Actions',
                     'Trading Ideas (low priority)'}
AI_MAX_STORIES = 4         # how many top stories get Gemini-written concepts
GEMINI_MODEL = 'gemini-3.8-flash'   # change here if Google renames the model

# ---------- Market tables (name -> Yahoo Finance symbol) ----------
# Global index board, grouped by region (name -> Yahoo Finance symbol).
# MSCI indices have no free Yahoo data, so ETFs that track them are used as proxies.
GLOBAL_INDICES = {
    'India': {
        'Nifty 50': '^NSEI', 'Sensex': '^BSESN', 'Nifty Bank': '^NSEBANK',
        'Nifty IT': '^CNXIT', 'Nifty Midcap 50': '^NSEMDCP50',
    },
    'US': {
        'S&P 500': '^GSPC', 'Nasdaq Composite': '^IXIC', 'Nasdaq 100': '^NDX',
        'Dow Jones': '^DJI', 'Russell 2000': '^RUT',
    },
    'Europe': {
        'FTSE 100': '^FTSE', 'DAX': '^GDAXI', 'CAC 40': '^FCHI',
        'Euro Stoxx 50': '^STOXX50E', 'STOXX Europe 600': '^STOXX',
    },
    'Asia-Pacific': {
        'Nikkei 225': '^N225', 'Hang Seng': '^HSI', 'Shanghai Composite': '000001.SS',
        'KOSPI': '^KS11', 'S&P/ASX 200': '^AXJO',
    },
    'Global / EM (ETF proxies)': {
        'MSCI World (URTH)': 'URTH', 'MSCI Emerging Mkts (EEM)': 'EEM',
        'MSCI India (INDA)': 'INDA', 'MSCI ACWI (ACWI)': 'ACWI',
    },
}

# Volatility, rates, currency, commodities.
MACRO = {
    'India VIX': '^INDIAVIX',
    'US VIX': '^VIX',
    'US 10Y yield (%)': '^TNX',
    'Dollar index': 'DX-Y.NYB',
    'USD/INR': 'INR=X',
    'Brent crude ($)': 'BZ=F',
    'Gold ($/oz)': 'GC=F',
    'Silver ($/oz)': 'SI=F',
}

WATCHLIST = {
    'Max Healthcare': 'MAXHEALTH.NS',
    'Bharat Electronics': 'BEL.NS',
    'Reliance': 'RELIANCE.NS',
    'HDFC Bank': 'HDFCBANK.NS',
    'TCS': 'TCS.NS',
    'Bajaj Finance': 'BAJFINANCE.NS',
}

# Real sector-index moves (replaces the old placeholder "Watch" table).
# If Yahoo does not return one of these it simply shows under "Did not load".
SECTORS = {
    'Banks': '^NSEBANK',
    'IT': '^CNXIT',
    'Pharma': '^CNXPHARMA',
    'FMCG': '^CNXFMCG',
    'Auto': '^CNXAUTO',
    'Metals': '^CNXMETAL',
    'Energy': '^CNXENERGY',
}

# ---------- Headline filters ----------
NON_FINANCE_WORDS = [
    'bollywood', 'movie', 'film', 'cricket', 'football', 'celebrity',
    'election', 'riot', 'murder', 'crime', 'viral', 'gold paste',
    'emergency fund', 'retiree', 'leave encashment', 'oral gift',
    'fake commute', 'separation push', 'russia trip', 'peter lynch',
    'warren buffett', 'dussehra', 'diwali', 'smart kitchens', 'pf limit',
    'data breach claims', 'labour law', 'wedding', 'et wealth',
]

# ---------- Desk rules (core list) ----------
# Checked top to bottom, first match wins. Each entry: (desk, radar_category, words)
# radar_category is None for desks that are not "deals".
# Headlines are checked first (more reliable); only if nothing matches does it look at the
# longer summary text (and the Earnings desk is skipped in that second pass).
DESK_RULES = [
    # Headline-only rules (4th item True): roundups, live blogs and technical-trading noise.
    ('Trading Ideas (low priority)', None, [
        'marubozu', 'rsi trending', 'rsi upswing', 'stockedge', 'technical outlook', 'trade strategy',
        'intraday', 'candlestick', 'breakout stocks', 'support and resistance', 'stock picks',
        'stocks to buy', 'recommends three stocks', 'recommends 3 stocks'], True),
    ('Broker Calls & Stock Movers', None, ['stocks in focus', 'stocks to watch'], True),
    ('Market Pulse & Global Cues', None, [
        'live updates', 'stock market live', 'sensex today', 'nifty today', 'opening bell',
        'closing bell'], True),
    ('Private Credit & Distressed Debt', 'Debt / Restructuring', [
        'private credit', 'direct lending', 'nclt', 'chapter 11', 'bond sale',
        'corporate bond', 'corporate bonds', 'bond issuance', 'syndicated loan',
        'refinancing', 'refinance', 'leveraged finance', 'mezzanine', 'insolvency',
        'bankruptcy', 'debt recast', 'debt restructuring', 'loan restructuring', 'distressed']),
    ('IPOs & Block Deals', 'IPO & Block Deals', [
        'ipo', 'ipos', 'sme ipo', 'drhp', 'anchor investor', 'anchor book', 'qip', 'rights issue',
        'fpo', 'follow-on', 'block deal', 'block deals', 'bulk deal', 'bulk deals', 'price band', 'gmp']),
    ('PE Fundraising & Dry Powder', 'PE Fundraising', [
        'dry powder', 'final close', 'first close', 'new fund', 'fund size', 'limited partners',
        'sovereign wealth', 'gic', 'temasek', 'mubadala', 'lp commitment', 'raises fund']),
    ('LBO, Growth & Secondary Buyouts', 'PE & Growth Equity', [
        'private equity', 'pe firm', 'buyout', 'leveraged buyout', 'lbo', 'growth equity',
        'secondary sale', 'minority stake', 'stake sale']),
    ('M&A & Investment Banking', 'M&A / Control Deals', [
        'acquisition', 'acquisitions', 'acquire', 'acquires', 'acquired', 'merger', 'mergers', 'merges', 'majority stake',
        'takeover', 'open offer', 'demerger', 'divest', 'divestment']),
    ('LBO, Growth & Secondary Buyouts', 'PE & Growth Equity', [
        'stake in', 'stake to', 'stake', 'stakes', 'offload', 'offloads']),
    ('LBO, Growth & Secondary Buyouts', 'VC / Startup Funding', [
        'series a', 'series b', 'series c', 'seed funding', 'venture capital',
        'vc funding', 'startup raises', 'startup funding', 'raises ₹', 'raises $', 'raises rs']),
    ('Corporate Actions', None, [
        'buyback', 'buybacks', 'dividend', 'dividends', 'stock split', 'bonus issue', 'delisting', 'order win',
        'bags', 'bags order', 'wins order', 'secures order', 'order inflow', 'capex']),
    ('Broker Calls & Stock Movers', None, [
        'upgrades to', 'upgraded to', 'downgrades to', 'downgraded to', 'upgrade to buy', 'downgrade to sell',
        'initiates coverage', 'retains buy', 'maintains buy', 'retains sell', 'maintains sell', 'retains hold',
        'price target', 'target price', 'brokerage', 'buy rating',
        'sell rating', 'overweight', 'outperform rating', 'underperform rating', 'stocks to watch',
        'stocks to buy', 'stock picks', 'buy or sell', 'top gainers', 'top losers',
        'shares jump', 'shares surge', 'shares rally', 'shares fall', 'shares tumble',
        'shares slump', 'stock jumps', 'stock surges', 'stock falls', 'stock rallies']),
    ('Companies & Earnings', None, [
        'q1', 'q2', 'q3', 'q4', 'results', 'earnings', 'net profit', 'profit after tax', 'pat',
        'profit jumps', 'profit rises', 'profit falls', 'profit drops', 'profit surges',
        'profit declines', 'first quarter', 'second quarter', 'third quarter',
        'fourth quarter', 'guidance']),
    ('Market Pulse & Global Cues', None, [
        'nasdaq', 'dow jones', 'wall street', 'us stocks', 's&p 500', 'nifty', 'sensex',
        'gold', 'silver', 'crude', 'brent', 'european stocks', 'asian markets']),
    ('Macro Indicators', None, [
        'gdp', 'cpi', 'wpi', 'pmi', 'inflation', 'iip', 'jobs data', 'payrolls', 'nonfarm',
        'unemployment', 'fiscal deficit', 'trade deficit', 'gst collections', 'union budget']),
    ('Central Banks & Policy', None, [
        'rbi', 'repo rate', 'monetary policy', 'fed', 'federal reserve', 'ecb',
        'interest rate', 'interest rates', 'rate cut', 'rate cuts', 'rate hike', 'rate hikes', 'liquidity', 'sebi', 'cci',
        'regulatory', 'regulation', 'yield', 'yields', 'g-sec', '10-year']),
]
DEFAULT_DESK = 'Market Pulse & Global Cues'

# Stories that fall into the default desk with low importance are dropped unless they
# contain at least one of these words (removes stray general news).
MARKET_WORDS = [
    'stock', 'stocks', 'market', 'markets', 'share', 'shares', 'nifty', 'sensex', 'rupee',
    'rbi', 'sebi', 'bank', 'banks', 'ipo', 'fund', 'funds', 'investor', 'investors', 'gold',
    'crude', 'oil', 'bond', 'bonds', 'economy', 'gdp', 'inflation', 'tax', 'trading', 'equity',
]

# Order in which desks appear on the page (Top Deals + Deal Radar come first).
DESK_ORDER = [
    'PE Fundraising & Dry Powder',
    'LBO, Growth & Secondary Buyouts',
    'M&A & Investment Banking',
    'IPOs & Block Deals',
    'Private Credit & Distressed Debt',
    'Companies & Earnings',
    'Broker Calls & Stock Movers',
    'Corporate Actions',
    'Central Banks & Policy',
    'Macro Indicators',
    'Market Pulse & Global Cues',
    'Trading Ideas (low priority)',
]
DEAL_DESKS = DESK_ORDER[:5]
RADAR_ORDER = [
    'M&A / Control Deals', 'PE & Growth Equity', 'VC / Startup Funding',
    'PE Fundraising', 'IPO & Block Deals', 'Debt / Restructuring',
]

HIGH_VALUE_DEAL_WORDS = [
    'acquisition', 'acquires', 'acquired', 'merger', 'takeover', 'buyout',
    'private equity', 'ipo', 'drhp', 'qip', 'block deal', 'rights issue',
    'fundraise', 'raises', 'stake sale', 'minority stake', 'insolvency',
    'bond sale', 'refinancing',
]

STAGE_RULES = [  # first match wins
    ('Subscribed', ['subscribed', 'oversubscribed', 'oversubscription']),
    ('IPO Open', ['set to open', 'opens on', 'will open', 'ipo to open', 'bidding opens', 'issue opens']),
    ('Closed', ['closes with', 'closes on', 'subscription closes', 'ipo closes', 'closed with']),
    ('Listed', ['lists on', 'listing today', 'debuts', 'made its debut', 'listing performance']),
    ('Rumor', ['may', 'eyes', 'plans', 'considering', 'reportedly', 'weighs', 'potential']),
]

# "Why it matters" lines, first match wins.
WHY_RULES = [
    (['block deal', 'block deals', 'bulk deal', 'bulk deals'], 'Shows who sold and who bought. Large exits by early backers can create supply overhang and signal how they value the stock.'),
    (['subscribed', 'oversubscribed'], 'High subscription indicates strong investor demand and helps gauge IPO pricing and listing expectations.'),
    (['gmp'], 'GMP reflects unofficial grey-market expectations ahead of listing; it is not a guarantee of returns.'),
    (['anchor'], 'Anchor-book demand shows early institutional interest in the IPO.'),
    (['valuation'], 'Valuation commentary helps judge whether an offering is priced conservatively or aggressively versus peers.'),
    (['bond', 'refinancing'], 'Reflects credit-market conditions, borrowing costs and companies\' ability to raise debt.'),
    (['acquisition', 'acquire', 'acquires', 'merger', 'takeover', 'majority stake'], 'Signals consolidation, valuation trends and likely future deal activity in the sector.'),
    (['private equity', 'buyout', 'venture capital', 'funding', 'raises'], 'Shows investor appetite, financing conditions and valuation trends for private companies.'),
    (['rbi', 'repo', 'inflation', 'gdp', 'fed'], 'Affects interest rates, liquidity, borrowing costs, equity valuations and deal activity.'),
    (['results', 'earnings', 'profit', 'loss'], 'Helps assess business performance, margins, guidance and investment relevance.'),
]
WHY_DEFAULT = ''   # no generic filler: if nothing specific applies, the line is simply not shown
# Used when no keyword rule above matches: one question-led line per desk.
WHY_BY_DESK = {
    'IPOs & Block Deals': 'Check what is being sold (a fresh issue gives the company new money, an offer for sale does not), what the proceeds are used for, valuation versus listed peers, and listing risk.',
    'PE Fundraising & Dry Powder': 'Shows how much capital is available to deploy and which investors are backing fund managers.',
    'LBO, Growth & Secondary Buyouts': 'Look at the stake bought, the price paid, who is selling and how the deal is financed.',
    'M&A & Investment Banking': 'Look at buyer, target, price paid, strategic fit and how the deal is funded.',
    'Private Credit & Distressed Debt': 'Shows lending conditions outside banks and how stressed borrowers are being handled.',
    'Companies & Earnings': 'Look beyond profit: revenue growth, margin direction, cash flow and management guidance.',
    'Broker Calls & Stock Movers': 'Broker views move stocks in the short run; compare the target price with valuation and the reason given.',
    'Corporate Actions': 'Buybacks and dividends return cash to shareholders; check the size relative to market value and why now.',
    'Central Banks & Policy': 'What changed, which sectors gain or lose, and how it feeds into rates, currency and valuations.',
    'Macro Indicators': 'Follow the chain: data, then rate expectations, then yields and currency, then equity valuations.',
}


# ---------- Concepts: name -> (trigger words, beginner definition) ----------
CONCEPTS = {
    'anchor investors': (['anchor investor', 'anchor book'], 'Large institutional investors invited to invest in an IPO before it opens to the public. Their participation signals confidence and provides early demand.'),
    'book building': (['book building', 'price band', 'issue price'], 'The process where investors bid for IPO shares within a price band, helping determine the final issue price.'),
    'IPO valuation': (['ipo valuation', 'valued at'], 'The estimated value of a company at the time of its IPO, usually based on earnings, growth and comparable companies.'),
    'DRHP': (['drhp'], 'Draft Red Herring Prospectus. The preliminary document filed before an IPO containing company financials, risks and offer details.'),
    'IPO': (['ipo'], 'Initial Public Offering. The process by which a private company sells shares to public investors for the first time.'),
    'QIP': (['qip'], 'Qualified Institutional Placement. A way for listed companies to raise money by selling shares to qualified institutional investors.'),
    'block deal': (['block deal', 'block deals', 'bulk deal', 'bulk deals'], 'A large trade executed between two parties, usually institutional investors, through a stock exchange.'),
    'dilution': (['dilution'], 'The reduction in existing shareholders\' ownership percentage when new shares are issued.'),
    'rights issue': (['rights issue'], 'An offer to existing shareholders to buy additional shares, usually at a discount.'),
    'buyback': (['buyback'], 'When a company repurchases its own shares, often to return cash or improve per-share metrics.'),
    'promoter stake': (['promoter stake', 'promoter holding'], 'The ownership held by a company\'s founders, promoters or promoter group.'),
    'control premium': (['majority stake', 'takeover', 'control premium'], 'The extra price paid to acquire a controlling stake in a company.'),
    'minority stake': (['minority stake', 'minority investment'], 'An investment where the investor buys less than 50% ownership and does not gain control.'),
    'private equity': (['private equity', 'pe firm', 'buyout'], 'Investment funds that buy or invest in private companies, often aiming to improve them and exit later.'),
    'venture capital': (['venture capital', 'vc funding', 'series a', 'series b', 'series c'], 'Investment in early or growth-stage companies, usually in exchange for equity.'),
    'fundraising': (['fundraise', 'funding', 'raises'], 'The process of raising capital from investors.'),
    'exit': (['exit', 'stake sale', 'divestment'], 'When an investor sells its ownership in a company, such as through a sale, IPO or secondary transaction.'),
    'valuation multiple': (['valuation', 'valued at'], 'A ratio used to value a company, such as EV/EBITDA or P/E.'),
    'enterprise value': (['enterprise value'], 'The total value of a company, including equity value and net debt.'),
    'LBO financing': (['lbo', 'leveraged buyout'], 'Funding used in a leveraged buyout, where a large part of the purchase price is financed with debt.'),
    'leverage': (['leveraged', 'leverage'], 'The use of borrowed money to finance an investment or acquisition.'),
    'acquisition financing': (['acquisition financing', 'acquisition loan'], 'Debt or equity raised to fund an acquisition.'),
    'refinancing': (['refinancing', 'refinance'], 'Replacing existing debt with new debt, often to reduce cost or extend maturity.'),
    'bond yield': (['bond yield', 'yields'], 'The return an investor earns from a bond, influenced by its price, coupon and maturity.'),
    'credit spread': (['credit spread', 'credit rating'], 'The extra yield investors demand for taking credit risk over a safer benchmark bond.'),
    'repo rate': (['repo rate', 'repo'], 'The rate at which banks borrow short-term funds from the RBI.'),
    'monetary policy': (['monetary policy', 'rbi policy'], 'Central-bank actions that influence interest rates, money supply and liquidity.'),
    'liquidity': (['liquidity'], 'The availability of money or easily tradable assets in the financial system.'),
    'inflation': (['inflation', 'cpi', 'wpi'], 'The rate at which general prices rise over time.'),
    'interest rate': (['interest rate', 'rate cut', 'rate hike'], 'The cost of borrowing money or the return earned on lending money.'),
    'FII flows': (['fii', 'foreign institutional'], 'Net buying or selling by foreign institutional investors.'),
    'DII flows': (['dii', 'domestic institutional'], 'Net buying or selling by domestic institutional investors.'),
    'sector rotation': (['sector rotation', 'rotation'], 'When investors move money from one sector to another based on economic conditions or valuations.'),
    'currency depreciation': (['rupee', 'depreciation'], 'A fall in the value of one currency relative to another.'),
    'commodity prices': (['crude', 'oil', 'gold', 'silver', 'commodity'], 'Prices of raw materials such as crude oil, gold, metals and agricultural goods.'),
    'EBITDA margin': (['ebitda', 'margin'], 'EBITDA divided by revenue; it measures operating profitability.'),
    'operating leverage': (['operating leverage', 'margin expansion'], 'How much a company\'s profits change when revenue changes.'),
    'guidance': (['guidance'], 'Management\'s forecast or outlook for future performance.'),
    'free cash flow': (['free cash flow', 'cash flow'], 'Cash generated by a business after operating expenses and capital expenditure.'),
    'earnings': (['results', 'earnings', 'profit', 'loss'], 'A company\'s reported profit or loss over a period.'),
    'broker call': (['upgrade', 'downgrade', 'price target', 'target price'], 'A brokerage\'s investment recommendation, such as buy, sell, upgrade or downgrade.'),
}

# Concepts shown first when a story matches several (most PE/IB-relevant first).
CONCEPT_PRIORITY = [
    'control premium', 'valuation multiple', 'enterprise value', 'LBO financing',
    'acquisition financing', 'exit', 'private equity', 'venture capital',
    'anchor investors', 'book building', 'IPO valuation', 'DRHP', 'QIP',
    'block deal', 'promoter stake', 'refinancing', 'bond yield',
]


# ---------- Watchlist news matching (headline only, whole words) ----------
# Company name -> words that identify it in a headline. Default is the full lowercase name.
WATCHLIST_ALIASES = {
    'Max Healthcare': ['max healthcare'],
    'Bharat Electronics': ['bharat electronics', 'bel'],
    'Reliance': ['reliance industries', 'reliance retail', 'reliance jio', 'jio platforms', 'ril'],
    'HDFC Bank': ['hdfc bank'],
    'TCS': ['tcs', 'tata consultancy'],
    'Bajaj Finance': ['bajaj finance'],
}

# A story is not counted as a "top deal" if its headline has one of these (commentary, not a transaction).
TOP_DEAL_EXCLUDE = ['why', 'how', 'what', 'explains', 'interview', 'opinion', 'view', 'views']


# ---------- Newspaper page + AI settings ----------
WIRE_ITEMS = 14              # length of the "Latest wire" list
EARNINGS_ROWS_MAX = 8        # results stories sent to the AI for the earnings table
AI_ARTICLES_MAX = 4          # lead story + top deals that get a full-article summary / deal card
AI_ARTICLE_CHARS = 3500      # how much article text the AI reads per story
REFRESH_SECONDS = 300        # open page checks for a newer edition this often

# Names (as in the tables) shown in the scrolling strip under the title.
TICKER = ['Nifty 50', 'Sensex', 'Nifty Bank', 'S&P 500', 'Nasdaq Composite', 'FTSE 100',
          'Nikkei 225', 'Brent crude ($)', 'Gold ($/oz)', 'USD/INR', 'US 10Y yield (%)', 'India VIX']

# ---------- Hard time limits (seconds) so a slow outside service can never hang a build ----------
AI_CALL_TIMEOUT = 40      # per Gemini attempt
AI_TOTAL_BUDGET = 180     # all Gemini work in one run; after this the page is built without more AI
QUOTE_TIMEOUT = 25        # per price lookup
