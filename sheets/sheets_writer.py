import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Deal-Flow-Qualifier"
TAB_NAME   = "Deal-Flow-Tracker"

HEADERS = [
    "Timestamp", "Company", "Sector", "Stage",
    "Market Size", "Team", "Traction", "Moat",
    "Business Model", "Capital Efficiency", "Risk",
    "Total Score (/100)", "Verdict",
    "Key Strengths", "Key Concerns", "Next Step"
]

VERDICT_COLORS = {
    "PASS":  {"red": 0.18, "green": 0.80, "blue": 0.44},   # green
    "WATCH": {"red": 1.00, "green": 0.76, "blue": 0.03},   # amber
    "PASS":  {"red": 0.94, "green": 0.27, "blue": 0.23},   # red — overwritten below
}

# Fix: define cleanly
COLORS = {
    "PASS":  {"red": 0.18, "green": 0.80, "blue": 0.44},
    "WATCH": {"red": 1.00, "green": 0.76, "blue": 0.03},
    "NO":    {"red": 0.94, "green": 0.27, "blue": 0.23},
}


def get_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds)


def ensure_tab(sh):
    try:
        ws = sh.worksheet(TAB_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=500, cols=len(HEADERS))

    # Always write/refresh headers
    ws.update([HEADERS], "A1")
    return ws


def score_to_row(r):
    s = r.get("scores", {})
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        ts,
        r.get("company", ""),
        r.get("sector", ""),
        r.get("stage", ""),
        s.get("market_size", ""),
        s.get("team", ""),
        s.get("traction", ""),
        s.get("moat", ""),
        s.get("business_model", ""),
        s.get("capital_efficiency", ""),
        s.get("risk", ""),
        r.get("total_score", ""),
        r.get("verdict", ""),
        r.get("strengths", ""),
        r.get("concerns", ""),
        r.get("next_step", ""),
    ]


def write_results(results):
    gc = get_client()
    sh = gc.open(SHEET_NAME)
    ws = ensure_tab(sh)

    rows = [score_to_row(r) for r in results]
    if not rows:
        return

    # Append after header row
    start_row = 2
    end_col = chr(ord("A") + len(HEADERS) - 1)
    range_str = f"A{start_row}:{end_col}{start_row + len(rows) - 1}"
    ws.update(rows, range_str)

    # Color-code the Verdict column (column M = index 13)
    for i, r in enumerate(results):
        verdict = r.get("verdict", "NO").upper()
        color = COLORS.get(verdict, COLORS["NO"])
        row_num = start_row + i
        ws.format(f"M{row_num}", {
            "backgroundColor": color,
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
        })
