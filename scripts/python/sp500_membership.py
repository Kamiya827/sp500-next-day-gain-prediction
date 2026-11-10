# All membership dates come from one source: the fja05680/sp500 dataset on
# GitHub, Wikipedia is used for names of companies and date left.
#
# A company that changed tickers gets one row per ticker, all with the same
# latest company name. The old ticker's date_ended is the rename date, which is
# also the new ticker's date_added.
#
# Columns:
#   company_name      Most recent name of the company
#   ticker            ticker during current membership
#   date_added        first day in the index under this ticker; 1996-01-02
#                     means "on or before 1996-01-02", since the dataset
#                     starts on that day
#   date_ended        removal or rename date; empty if still a member on 2026-01-01

from io import StringIO

import pandas as pd
import requests

MEMBERSHIP_URL = "https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv"
URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
CHANGES_URL = "https://en.wikipedia.org/wiki/Historical_components_of_the_S%26P_500"
START = pd.Timestamp("2016-01-01")
END = pd.Timestamp("2026-01-01")
OUTPUT = "sp500_historical_membership.csv"

def fetch(url):
    return requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text

membership = pd.read_csv(StringIO(fetch(MEMBERSHIP_URL)), parse_dates=["start_date", "end_date"])
current = pd.read_html(StringIO(fetch(URL)), attrs={"id": "constituents"})[0]
raw_changes = pd.read_html(StringIO(fetch(CHANGES_URL)), attrs={"id": "changes"})[0]

# Corrections to the dataset, each checked against company filings or other sources
membership = membership[membership["ticker"] != "CCEP"].copy()

# Rename dates the dataset has wrong: (old ticker, new ticker, date)
RENAME_DATES = [
    ("KORS", "CPRI", "2019-01-02"),  # CPRI was listed from 2016 while KORS was still a member
    ("HRS", "LHX", "2019-07-01"),    # dataset was a month early
    ("ARNC", "HWM", "2020-04-01"),
    ("PX", "LIN", "2018-10-31"),
]
for old, new, date in RENAME_DATES:
    membership.loc[membership["ticker"] == new, "start_date"] = pd.Timestamp(date)
    membership.loc[(membership["ticker"] == old) & (membership["end_date"] >= START), "end_date"] = pd.Timestamp(date)

# The dataset keeps IR as one row, but the old Ingersoll Rand became Trane (TT)
# and Gardner Denver took the IR name and ticker on this date. (Fix)
IR_SPLIT = pd.Timestamp("2020-03-03")
membership.loc[(membership["ticker"] == "IR") & membership["end_date"].isna(), "end_date"] = IR_SPLIT
membership = pd.concat([membership, pd.DataFrame({"ticker": ["IR"], "start_date": [IR_SPLIT], "end_date": [pd.NaT]})],
                       ignore_index=True)

# Changes table columns: date, added ticker, added name, removed ticker, removed name, reason
changes = pd.DataFrame({
    "date": pd.to_datetime(raw_changes.iloc[:, 0], errors="coerce"),
    "added": raw_changes.iloc[:, 1],
    "added_name": raw_changes.iloc[:, 2],
    "removed": raw_changes.iloc[:, 3],
    "removed_name": raw_changes.iloc[:, 4],
}).dropna(subset=["date"])

current_name = dict(zip(current["Symbol"], current["Security"]))

# Ticker changes (old, new), oldest first. The dataset ends a membership when a
# ticker changes, so these join the old ticker's row onto the new one.
RENAMES = [
    ("KORS", "CPRI"),   # Michael Kors changed to Capri Holdings
    ("PX", "LIN"),      # Praxair + Linde AG changed to Linde plc
    ("HRS", "LHX"),     # Harris + L3 changed to L3Harris
    ("TMK", "GL"),      # Torchmark changed to Globe Life
    ("BHGE", "BKR"),    # Baker Hughes, a GE company changed to Baker Hughes
    ("SYMC", "NLOK"),   # Symantec changed to NortonLifeLock
    ("HCP", "PEAK"),    # HCP changed to Healthpeak
    ("CBS", "VIAC"),    # CBS + Viacom changed to ViacomCBS
    ("BBT", "TFC"),     # BB&T + SunTrust changed to Truist
    ("JEC", "J"),       # Jacobs Engineering changed to Jacobs
    ("IR", "TT"),       # Ingersoll Rand changed to Trane Technologies
    ("UTX", "RTX"),     # United Technologies + Raytheon changed to Raytheon Technologies
    ("ARNC", "HWM"),    # Arconic changed to Howmet Aerospace
    ("CTL", "LUMN"),    # CenturyLink changed to Lumen
    ("MYL", "VTRS"),    # Mylan + Upjohn changed to Viatris
    ("LB", "BBWI"),     # L Brands changed to Bath & Body Works
    ("COG", "CTRA"),    # Cabot Oil & Gas + Cimarex changed to Coterra
    ("WLTW", "WTW"),    # Willis Towers Watson
    ("VIAC", "PARA"),   # ViacomCBS changed to Paramount Global
    ("BLL", "BALL"),    # Ball Corporation
    ("FB", "META"),     # Facebook changed to Meta Platforms
    ("ANTM", "ELV"),    # Anthem changed to Elevance Health
    ("NLOK", "GEN"),    # NortonLifeLock changed to Gen Digital
    ("PKI", "RVTY"),    # PerkinElmer changed to Revvity
    ("FISV", "FI"),     # Fiserv
    ("RE", "EG"),       # Everest Re changed to Everest Group
    ("ABC", "COR"),     # AmerisourceBergen changed to Cencora
    ("CDAY", "DAY"),    # Ceridian changed to Dayforce
    ("PEAK", "DOC"),    # Healthpeak (after Physicians Realty merger)
    ("FLT", "CPAY"),    # FleetCor changed to Corpay
    ("WRK", "SW"),      # WestRock + Smurfit Kappa changed to Smurfit Westrock
    ("PARA", "PSKY"),   # Paramount Global + Skydance changed to Paramount Skydance
    ("FI", "FISV"),     # Fiserv
]

# Names for tickers that appear in neither Wikipedia table
KNOWN_NAMES = {
    "AABA": "Altaba (formerly Yahoo!)",
    "WYND": "Wyndham Worldwide",
    "BK": "Bank of New York Mellon",
    "MMC": "Marsh & McLennan",
    "TAP": "Molson Coors",
    "EQR": "Equity Residential",
    "PSKY": "Paramount Skydance",
}

# Link each old ticker's row to the row that continues it under the new ticker.
# Both rows are kept; they share one company name
successor = {}
for old, new in RENAMES:
    for i, prev in membership[membership["ticker"] == old].dropna(subset=["end_date"]).iterrows():
        nxt = membership[(membership["ticker"] == new)
                         & ((membership["start_date"] - prev["end_date"]).abs() <= pd.Timedelta(days=3))]
        if len(nxt):
            successor[i] = nxt.index[0]
            break

def latest_row(i):
    while i in successor:
        i = successor[i]
    return membership.loc[i]

# Keep only memberships that overlap the window. In the dataset, start_date is
# the first day in the index and end_date is the effective removal date.
in_window = membership[(membership["start_date"] < END)
                       & (membership["end_date"].isna() | (membership["end_date"] > START))
                       & (membership["end_date"].isna() | (membership["end_date"] > membership["start_date"]))]

def company_name(ticker, start, end):
    "Name from the current table, else the Wikipedia change nearest this membership."
    if pd.isna(end) and ticker in current_name:
        return current_name[ticker]
    removals = changes[(changes["removed"] == ticker) & changes["removed_name"].notna()]
    if not pd.isna(end) and len(removals):
        nearest = (removals["date"] - end).abs().idxmin()
        return removals.loc[nearest, "removed_name"]
    additions = changes[(changes["added"] == ticker) & changes["added_name"].notna()]
    if len(additions):
        nearest = (additions["date"] - start).abs().idxmin()
        return additions.loc[nearest, "added_name"]
    return current_name.get(ticker, KNOWN_NAMES.get(ticker, ""))

rows = []
for i, m in in_window.iterrows():
    added, ended = m["start_date"], m["end_date"]
    # Every ticker of a renamed company gets the company's latest name
    latest = latest_row(i)
    rows.append({
        "company_name": company_name(latest["ticker"], latest["start_date"], latest["end_date"]),
        "ticker": m["ticker"],
        "date_added": added.strftime("%Y-%m-%d"),
        # Still a member as of the end of the window = date empty
        "date_ended": "" if pd.isna(ended) or ended > END else ended.strftime("%Y-%m-%d"),
    })

df = pd.DataFrame(rows).sort_values(["date_added", "ticker"])
df.to_csv(OUTPUT, index=False)
print(f"Wrote {len(df)} rows to {OUTPUT}")
