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
}

ITEMS_PER_SOURCE = 12      # newest N items taken from each feed
MAX_AGE_HOURS = 48         # ignore anything older than this
MAX_TOP_DEALS = 5
MAX_PER_RADAR_CATEGORY = 6
MAX_PER_DESK = 10
AI_MAX_STORIES = 4         # how many top stories get Gemini-written concepts
GEMINI_MODEL = 'gemini-3.8-flash'   # change here if Google renames the model

# ---------- Market tables (name -> Yahoo Finance symbol) ----------
INDIA = {
    'Nifty 50': '^NSEI',
    'Sensex': '^BSESN',
    'Nifty Bank': '^NSEBANK',
    'India VIX': '^INDIAVIX',
}

WORLD = {
    'S&P 500': '^GSPC',
    'Nasdaq': '^IXIC',
    'FTSE 100': '^FTSE',
    'Nikkei 225': '^N225',
    'US 10Y yield (%)': '^TNX',
    'USD/INR': 'INR=X',
    'Brent crude ($)': 'BZ=F',
    'Gold ($/oz)': 'GC=F',
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
    'data breach claims', 'labour law',
]

# ---------- Desk rules (core list) ----------
# Checked top to bottom, first match wins. Each entry: (desk, radar_category, words)
# radar_category is None for desks that are not "deals".
DESK_RULES = [
    ('Private Credit & Distressed Debt', 'Debt / Restructuring', [
        'private credit', 'direct lending', 'nclt', 'chapter 11', 'bond sale', 'bonds',
        'bond issuance', 'syndicated loan', 'refinancing', 'refinance', 'leveraged finance',
        'mezzanine', 'insolvency', 'bankruptcy', 'debt recast', 'restructuring', 'distressed']),
    ('IPOs & Block Deals', 'IPO & Block Deals', [
        'ipo', 'sme ipo', 'drhp', 'anchor investor', 'anchor book', 'qip', 'rights issue',
        'fpo', 'follow-on', 'block deal', 'bulk deal', 'price band', 'gmp']),
    ('PE Fundraising & Dry Powder', 'PE Fundraising', [
        'dry powder', 'final close', 'first close', 'new fund', 'fund size', 'limited partners',
        'sovereign wealth', 'gic', 'temasek', 'mubadala', 'lp commitment', 'raises fund']),
    ('LBO, Growth & Secondary Buyouts', 'PE & Growth Equity', [
        'private equity', 'pe firm', 'buyout', 'leveraged buyout', 'lbo', 'growth equity',
        'secondary sale', 'minority stake', 'stake sale', 'stake to', 'stake in']),
    ('LBO, Growth & Secondary Buyouts', 'VC / Startup Funding', [
        'series a', 'series b', 'series c', 'seed funding', 'venture capital',
        'vc funding', 'startup raises', 'startup funding', 'raises ₹', 'raises $', 'raises rs']),
    ('M&A & Investment Banking', 'M&A / Control Deals', [
        'acquisition', 'acquire', 'acquires', 'acquired', 'merger', 'merges',
        'takeover', 'open offer', 'demerger', 'divest', 'divestment']),
    ('Companies & Earnings', None, [
        'q1', 'q2', 'q3', 'q4', 'results', 'earnings', 'profit', 'loss',
        'revenue', 'guidance', 'margin', 'buyback', 'dividend']),
    ('Central Banks & Policy', None, [
        'rbi', 'repo rate', 'monetary policy', 'fed', 'federal reserve', 'ecb',
        'interest rate', 'rate cut', 'rate hike', 'liquidity', 'sebi', 'cci',
        'regulatory', 'regulation', 'yield', 'g-sec']),
    ('Macro Indicators', None, [
        'gdp', 'cpi', 'wpi', 'pmi', 'inflation', 'iip', 'jobs data', 'unemployment',
        'fiscal deficit', 'trade deficit', 'gst collections', 'budget']),
]
DEFAULT_DESK = 'Market Pulse & Global Cues'

# Order in which desks appear on the page (Top Deals + Deal Radar come first).
DESK_ORDER = [
    'PE Fundraising & Dry Powder',
    'LBO, Growth & Secondary Buyouts',
    'M&A & Investment Banking',
    'IPOs & Block Deals',
    'Private Credit & Distressed Debt',
    'Companies & Earnings',
    'Central Banks & Policy',
    'Macro Indicators',
    'Market Pulse & Global Cues',
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
    (['subscribed', 'oversubscribed'], 'High subscription indicates strong investor demand and helps gauge IPO pricing and listing expectations.'),
    (['gmp'], 'GMP reflects unofficial grey-market expectations ahead of listing; it is not a guarantee of returns.'),
    (['anchor'], 'Anchor-book demand shows early institutional interest in the IPO.'),
    (['valuation'], 'Valuation commentary helps judge whether an offering is priced conservatively or aggressively versus peers.'),
    (['bond', 'refinancing'], 'Reflects credit-market conditions, borrowing costs and companies\' ability to raise debt.'),
    (['acquisition', 'acquires', 'merger', 'takeover'], 'Signals consolidation, valuation trends and likely future deal activity in the sector.'),
    (['private equity', 'buyout', 'venture capital', 'funding', 'raises'], 'Shows investor appetite, financing conditions and valuation trends for private companies.'),
    (['rbi', 'repo', 'inflation', 'gdp', 'fed'], 'Affects interest rates, liquidity, borrowing costs, equity valuations and deal activity.'),
    (['results', 'earnings', 'profit', 'loss'], 'Helps assess business performance, margins, guidance and investment relevance.'),
]
WHY_DEFAULT = 'Relevant for understanding current market, corporate or macro trends.'

# ---------- Concepts: name -> (trigger words, beginner definition) ----------
CONCEPTS = {
    'anchor investors': (['anchor investor', 'anchor book'], 'Large institutional investors invited to invest in an IPO before it opens to the public. Their participation signals confidence and provides early demand.'),
    'book building': (['book building', 'price band', 'issue price'], 'The process where investors bid for IPO shares within a price band, helping determine the final issue price.'),
    'IPO valuation': (['ipo valuation', 'valued at'], 'The estimated value of a company at the time of its IPO, usually based on earnings, growth and comparable companies.'),
    'DRHP': (['drhp'], 'Draft Red Herring Prospectus. The preliminary document filed before an IPO containing company financials, risks and offer details.'),
    'IPO': (['ipo'], 'Initial Public Offering. The process by which a private company sells shares to public investors for the first time.'),
    'QIP': (['qip'], 'Qualified Institutional Placement. A way for listed companies to raise money by selling shares to qualified institutional investors.'),
    'block deal': (['block deal', 'bulk deal'], 'A large trade executed between two parties, usually institutional investors, through a stock exchange.'),
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
    'leverage': (['leveraged', 'borrowing', 'debt'], 'The use of borrowed money to finance an investment or acquisition.'),
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
    'guidance': (['guidance', 'outlook'], 'Management\'s forecast or outlook for future performance.'),
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
