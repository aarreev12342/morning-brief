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
    # Primary sources (regulators). Unverified addresses: if one is wrong or blocks bots it shows under "Did not load".
    'RBI press releases': 'https://www.rbi.org.in/pressreleases_rss.xml',
    'SEBI releases': 'https://www.sebi.gov.in/sebirss.xml',
}

ITEMS_PER_SOURCE = 12      # newest N items taken from each feed
MAX_AGE_HOURS = 48         # ignore anything older than this
MAX_TOP_DEALS = 5
MAX_PER_RADAR_CATEGORY = 6
MAX_PER_DESK = 5
DESK_CAPS = {'Market Pulse & Global Cues': 4}   # per-desk override of MAX_PER_DESK
# Stock-news desks are decided by the headline only (summaries often mention 'upgrades' etc. in passing).
SUMMARY_PASS_SKIP = {'Finance Logic & Market Structure', 'Companies & Earnings', 'Companies & Strategy', 'Broker Calls & Stock Movers', 'Corporate Actions',
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

# Dropped completely when the HEADLINE contains one of these (lifestyle / retail-content noise).
DROP_HEADLINE_WORDS = ["here's how", 'banks open or closed', 'bank holiday', 'wedding',
                       'buys property', 'buys apartment', 'buys flat', 'buys bungalow', 'buys villa', 'buys house',
                       'buys penthouse', 'property purchase', 'purchases property', 'buys luxury']

# ---------- Desk rules (core list) ----------
# Checked top to bottom, first match wins. Each entry: (desk, radar_category, words)
# radar_category is None for desks that are not "deals".
# Headlines are checked first (more reliable); only if nothing matches does it look at the
# longer summary text (and the Earnings desk is skipped in that second pass).
DESK_RULES = [
    ('Finance Logic & Market Structure', None, ['market structure', 'securities law', 'insider trading', 'short seller',
        'short-seller', 'spac', 'tokenised', 'tokenized', 'clearing corporation', 'settlement cycle', 'circuit breaker',
        'index inclusion', 'margin rules', 'sec charges', 'sec sues'], True),
    # Headline-only placement fixes (checked before everything else).
    ('Central Banks & Policy', None, ['money market operations', 'money-market operations', 'reserve money',
        'liquidity adjustment', 'standing deposit facility', 'treasury bills auction', 'auction results'], True),
    ('M&A & Investment Banking', 'M&A / Control Deals', ['cci approves', 'cci approval', 'cci nod', 'cci clears',
        'competition commission'], True),
    ('M&A & Investment Banking', 'PE & Growth Equity', ['to invest up to', 'invest up to', 'strategic investment',
        'to invest $', 'to invest rs', 'to invest ₹'], True),
    ('Companies & Strategy', None, ['naming rights', 'cabin revamp', 'cabin', 'revamp', 'lifestyle', 'sponsorship',
        'brand ambassador', 'scandal', 'jensen huang'], True),
    # Headline-only rules (4th item True): roundups, live blogs and technical-trading noise.
    ('Trading Ideas (low priority)', None, [
        'marubozu', 'rsi trending', 'rsi upswing', 'stockedge', 'technical outlook', 'trade strategy',
        'intraday', 'candlestick', 'breakout stocks', 'support and resistance', 'stock picks',
        'stocks to buy', 'recommends three stocks', 'recommends 3 stocks', 'do you own', 'multibagger',
        'technical experts', 'technical expert', 'volume shocker', 'stock recommendations', 'dividend alert',
        'penny stock', 'stocks under', 'stock under'], True),
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
        'layoffs', 'layoff', 'job cuts', 'retrenchment', 'buyback', 'buybacks', 'dividend', 'dividends', 'stock split', 'bonus issue', 'delisting', 'order win',
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
        'interest rate', 'interest rates', 'rate cut', 'rate cuts', 'rate hike', 'rate hikes', 'liquidity', 'sebi',
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
    'Finance Logic & Market Structure',
    'Companies & Earnings',
    'Companies & Strategy',
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
WHY_RULE_DESKS = {'IPOs & Block Deals'}   # keyword rules above apply only on these desks; other desks use the desk template
# Narrow special cases checked before the desk template: (headline words, line).
WHY_SPECIAL = [
    (['cci approves', 'cci approval', 'cci nod', 'cci clears', 'approval', 'approves', 'approved'],
     'Regulatory approval: check the parties, the stake, whether conditions were attached, and the timeline to completion.'),
    (['layoffs', 'layoff', 'job cuts', 'retrenchment'],
     'Layoffs signal cost pressure or a strategy shift: compare the scale with total headcount and ask whether it reflects weaker demand or an efficiency push.'),
    (['naming rights', 'sponsorship', 'brand ambassador'],
     'Marketing deals are a cash outflow for a brand: judge the cost against the reach gained and how it fits the company\'s growth plans.'),
    (['to invest up to', 'invest up to', 'strategic investment'],
     'Strategic investments show where capital is flowing: look at who is funding whom, what the money buys (capacity, equity, supply) and how dependent each side becomes.'),
]
WHY_DEFAULT = ''   # no generic filler: if nothing specific applies, the line is simply not shown
# Used when no keyword rule above matches: one question-led line per desk.
WHY_BY_DESK = {
    'IPOs & Block Deals': 'Check what is being sold (a fresh issue gives the company new money, an offer for sale does not), what the proceeds are used for, valuation versus listed peers, and listing risk.',
    'Companies & Strategy': 'A company decision that matters only if it changes revenue, costs or competitive position: ask how big it is relative to the business.',
    'PE Fundraising & Dry Powder': 'Shows how much capital is available to deploy and which investors are backing fund managers.',
    'LBO, Growth & Secondary Buyouts': 'Look at the stake bought, the price paid, who is selling and how the deal is financed.',
    'M&A & Investment Banking': 'Look at buyer, target, consideration, strategic logic, synergies, financing and integration risk.',
    'Private Credit & Distressed Debt': 'Shows lending conditions outside banks and how stressed borrowers are being handled: check the borrower, the lender, pricing and security.',
    'Companies & Earnings': 'Look beyond profit: revenue growth, margin direction, cash flow and management guidance.',
    'Broker Calls & Stock Movers': 'Broker views move stocks in the short run; compare the target price with valuation and the reason given.',
    'Corporate Actions': 'Buybacks and dividends return cash to shareholders; check the size relative to market value and why now.',
    'Central Banks & Policy': 'Identify the policy lever, the liquidity impact, which institutions are affected, and how it transmits to markets and rates.',
    'Macro Indicators': 'Follow the chain: data, then rate expectations, then yields and currency, then equity valuations.',
}


# ---------- Concepts: name -> (trigger words, beginner definition) ----------
CONCEPTS = {
    'fresh issue vs offer for sale': (['fresh issue', 'offer for sale', 'ofs', 'all-fresh', 'fresh equity'], 'Fresh issue: the company receives new capital, which can fund growth or repay debt. Offer for sale (OFS): existing shareholders sell their shares and the company receives nothing.'),
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
    'fresh issue vs offer for sale',
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
AI_TOTAL_BUDGET = 200     # all Gemini work in one run; after this the page is built without more AI
QUOTE_TIMEOUT = 25        # per price lookup


# ---------- Upgrade-plan settings ----------
# Why-it-matters is shown for stories at or above this importance (1-5).
WHY_MIN_IMPORTANCE = 3
AI_WHY_MAX = 14              # stories per run that get an AI-written, story-specific "why it matters"

# Your own watchlist notes. Edit these; they are shown exactly as written.
# catalyst = what you are watching for next. thesis = your one-line view (leave '' to hide).
WATCHLIST_NOTES = {
    'Max Healthcare': {'catalyst': 'Occupancy, ARPOB, bed additions', 'thesis': ''},
    'Bharat Electronics': {'catalyst': 'Order inflow, execution, margins', 'thesis': ''},
    'Reliance': {'catalyst': 'O2C margins, Jio, retail', 'thesis': ''},
    'HDFC Bank': {'catalyst': 'Q3 earnings, NIM, credit growth', 'thesis': ''},
    'TCS': {'catalyst': 'Client spending, deal wins', 'thesis': ''},
    'Bajaj Finance': {'catalyst': 'AUM growth, asset quality', 'thesis': ''},
}
# A headline mentioning the company AND one of these words shows as an alert badge next to it.
WATCHLIST_ALERT_WORDS = {
    'Results': ['q1', 'q2', 'q3', 'q4', 'results', 'net profit'],
    'Dividend': ['dividend'],
    'Buyback': ['buyback'],
    'Stake / block deal': ['block deal', 'bulk deal', 'stake'],
    'Broker call': ['target price', 'price target', 'upgrades', 'downgrades', 'upgraded', 'downgraded', 'initiates coverage'],
}

# Source tiers shown as a small badge. Anything not listed is "Press".
SOURCE_TIERS = {
    'RBI press releases': 'Primary', 'SEBI releases': 'Primary',
    'Inc42': 'Startup press',
    'Money Stuff': 'Market structure',
}
DEFAULT_TIER = 'News'

# A "Top deal" headline must contain one of these (a real transaction, not commentary).
TRANSACTION_WORDS = [
    'acquire', 'acquires', 'acquired', 'acquisition', 'merger', 'merges', 'buyout', 'takeover', 'open offer',
    'stake', 'stakes', 'raises', 'raised', 'funding', 'ipo', 'drhp', 'qip', 'rights issue', 'block deal',
    'block deals', 'bulk deal', 'bulk deals', 'offload', 'offloads', 'sells', 'buys', 'invests', 'to invest', 'invest up to',
    'files draft papers', 'bond sale', 'demerger', 'divest', 'divestment', 'to buy', 'to sell']

# Headlines about investor flows (shown together under Markets).
FLOW_WORDS = ['fpi', 'fpis', 'fii', 'fiis', 'dii', 'diis', 'foreign portfolio', 'foreign institutional',
              'institutional flows', 'net bought', 'net sold']
MAX_FLOW_ITEMS = 5

# Topics checked for headlines pointing in opposite directions.
CONFLICT_TOPICS = {
    'Indian bond yields': ['yield', 'yields', 'g-sec', 'bond', 'bonds'],
    'Rupee': ['rupee'],
    'Crude oil': ['crude', 'brent'],
    'Gold': ['gold'],
}
UP_WORDS = ['rise', 'rises', 'rose', 'jump', 'jumps', 'surge', 'surges', 'harden', 'hardens', 'climb',
            'climbs', 'gain', 'gains', 'rally', 'rallies', 'higher', 'firm', 'firms', 'strengthen']
DOWN_WORDS = ['fall', 'falls', 'fell', 'drop', 'drops', 'dips', 'dip', 'slip', 'slips', 'ease', 'eases',
              'decline', 'declines', 'slide', 'slides', 'lower', 'weak', 'weaken', 'plunge', 'tumble', 'slump']

# India macro snapshot. These numbers do not come from any feed: fill in the latest value and date from the
# primary source yourself (RBI, MOSPI, NSDL). Rows with an empty value are hidden. Example row:
#   {'name': 'RBI repo rate', 'value': '', 'as_of': '', 'source': 'https://www.rbi.org.in'},
MACRO_MANUAL = [
    {'name': 'RBI repo rate', 'value': '', 'as_of': '', 'source': 'https://www.rbi.org.in'},
    {'name': 'CPI inflation (India)', 'value': '', 'as_of': '', 'source': 'https://mospi.gov.in'},
    {'name': 'WPI inflation (India)', 'value': '', 'as_of': '', 'source': 'https://eaindustry.nic.in'},
    {'name': 'India 10-year G-sec yield', 'value': '', 'as_of': '', 'source': 'https://www.ccilindia.com'},
    {'name': 'Forex reserves', 'value': '', 'as_of': '', 'source': 'https://www.rbi.org.in'},
    {'name': 'Bank credit growth', 'value': '', 'as_of': '', 'source': 'https://www.rbi.org.in'},
    {'name': 'Deposit growth', 'value': '', 'as_of': '', 'source': 'https://www.rbi.org.in'},
]

# Where to check the facts yourself (shown at the bottom of the Study desk).
PRIMARY_LINKS = [
    ('RBI', 'https://www.rbi.org.in'), ('SEBI', 'https://www.sebi.gov.in'),
    ('NSE announcements', 'https://www.nseindia.com/companies-listing/corporate-filings-announcements'),
    ('BSE announcements', 'https://www.bseindia.com/corporates/ann.html'),
    ('MOSPI', 'https://mospi.gov.in'), ('FPI data (NSDL)', 'https://www.fpi.nsdl.co.in'),
    ('CCIL (G-sec yields)', 'https://www.ccilindia.com'), ('IMF data', 'https://www.imf.org/en/Data'),
]

# Research-question templates used when Gemini is unavailable. {h} is the story headline.
RESEARCH_BY_DESK = {
    'Companies & Strategy': 'In "{h}": is this large enough to change revenue or costs, or is it mainly branding?',
    'IPOs & Block Deals': 'In "{h}": what is being sold (fresh issue or offer for sale), what will the money be used for, and how is it priced against listed peers?',
    'LBO, Growth & Secondary Buyouts': 'In "{h}": who is buying and selling, at what price, and what does it say about how investors value the company?',
    'M&A & Investment Banking': 'In "{h}": what is the buyer paying, how is it funded, and what is the strategic logic?',
    'PE Fundraising & Dry Powder': 'In "{h}": how large is the fund, who are the investors, and where will the capital be deployed?',
    'Private Credit & Distressed Debt': 'In "{h}": who is lending or restructuring, on what terms, and what does it say about credit conditions?',
    'Companies & Earnings': 'In "{h}": did revenue growth or margins drive the profit change, and what did management guide for next quarter?',
    'Corporate Actions': 'In "{h}": how big is the action compared with market value, and why now?',
    'Broker Calls & Stock Movers': 'In "{h}": what reason did the broker give, and does the target price fit the valuation?',
    'Central Banks & Policy': 'In "{h}": through which channel (rates, currency, flows) does this reach Indian equities and bonds?',
    'Macro Indicators': 'In "{h}": which way does this move rate expectations, and who gains or loses?',
}

# ---------- Deal log (kept in your repo so it builds up over time) ----------
DEAL_LOG_PATH = 'data/deals.csv'
DEAL_LOG_MAX_ROWS = 400
DEAL_LOG_SHOW = 25

# ---------- AI reliability ----------
AI_RETRIES = 2               # extra tries (with a short pause) when Gemini answers 503/429/timeout
AI_CACHE_TTL_HOURS = 24      # a good AI answer is reused for this long
EARNINGS_CARDS = 3           # results stories that get the full earnings card (article text is read)


# ---------- Fix pass 2 settings ----------
YIELD_NAMES = {'US 10Y yield (%)'}          # shown as a change in basis points, not a percent change
PROMO_WORDS = ['joins ranks', 'mega ipo', "world's biggest", "world's largest", 'blockbuster', 'historic', 'massive']
WRAP_WORDS = ['futures', 'wall street', 'stocks to watch', 'live updates', 'opening bell']
EVENT_WORDS = {'ipo', 'listing', 'valuation', 'stake', 'acquisition', 'acquire', 'acquires', 'merger', 'buyout',
               'layoffs', 'roadshow', 'drhp', 'approval', 'funding', 'raises', 'invest', 'investment'}


# ---------- Learning layer: Money Stuff, private-markets intelligence, concall watch ----------
# Bloomberg Opinion author feed for Matt Levine (UNVERIFIED address; if it fails it is listed under "Did not load").
MONEY_STUFF = {
    'name': 'Money Stuff',
    'url': 'https://www.bloomberg.com/opinion/authors/ARbTQlRLRjE/matthew-s-levine.rss',
    'page': 'https://www.bloomberg.com/opinion/authors/ARbTQlRLRjE/matthew-s-levine',
}
MONEY_STUFF_BOOST = ['deal', 'deals', 'market', 'markets', 'regulation', 'sec', 'ai', 'ipo', 'private credit', 'merger',
                     'takeover', 'securities', 'stock', 'stocks', 'bond', 'bonds', 'crypto', 'private equity']
CONCALL_LINKS_PATH = 'data/concall_links.csv'      # you fill this in by hand
CONCALL_FIELDS = ['company', 'quarter', 'results_date', 'earnings_release_url', 'presentation_url',
                  'transcript_url', 'investor_relations_url', 'guidance', 'capex', 'key_risks']
CONCALL_GENERIC_LINKS = [('BSE announcements', 'https://www.bseindia.com/corporates/ann.html'),
                         ('NSE announcements', 'https://www.nseindia.com/companies-listing/corporate-filings-announcements')]
PITCHBOOK_PATH = 'data/pitchbook_style_deals.csv'
PITCHBOOK_FIELDS = ['date', 'company', 'investor', 'deal_type', 'sector', 'geography', 'deal_value', 'stake',
                    'valuation', 'stage', 'use_of_proceeds', 'strategic_rationale', 'exit_route', 'source_url']
SECTOR_KEYWORDS = [
    ('NBFC / financial services', ['nbfc', 'finance', 'bank', 'banks', 'insurance', 'lender', 'lending', 'fintech', 'amc']),
    ('Technology / AI', ['ai', 'software', 'tech', 'semiconductor', 'chip', 'chips', 'saas', 'cloud', 'data centre', 'data center']),
    ('Healthcare / pharma', ['pharma', 'hospital', 'hospitals', 'healthcare', 'drug', 'biotech', 'diagnostics']),
    ('Real estate', ['real estate', 'developers', 'realty', 'estates', 'housing']),
    ('Energy / power', ['oil', 'gas', 'power', 'solar', 'renewable', 'energy', 'coal']),
    ('Consumer / retail', ['retail', 'consumer', 'fmcg', 'restaurant', 'jewellery', 'ecommerce', 'e-commerce', 'foods']),
    ('Industrials / infra', ['steel', 'cement', 'infra', 'infrastructure', 'logistics', 'airport', 'port', 'railway', 'defence']),
    ('Telecom / media', ['telecom', 'media', 'broadcast', 'streaming']),
]
EXIT_WORDS = ['exit', 'exits', 'exited', 'sells stake', 'offloads', 'offload', 'divests', 'divest', 'stake sale', 'sells']
IPO_BOUND_WORDS = ['drhp', 'sebi nod', 'sebi approval', 'sebi approves', 'gets sebi', 'files for ipo', 'files ipo',
                   'plans ipo', 'ipo-bound', 'to launch ipo', 'ipo plans', 'ipo roadshow', 'circulated']
