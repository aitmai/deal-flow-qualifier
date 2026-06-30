import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Deal-Flow-Qualifier"
TAB_NAME   = "Deal-Submissions"


def get_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    return gspread.authorize(creds)


def read_deals():
    gc = get_client()
    sh = gc.open(SHEET_NAME)
    ws = sh.worksheet(TAB_NAME)

    rows = ws.get_all_records()

    deals = []
    for i, row in enumerate(rows, start=2):
        company = str(row.get("Company Name", "")).strip()
        if not company:
            continue

        deals.append({
            "company":     company,
            "stage":       str(row.get("Stage", "")).strip(),
            "sector":      str(row.get("Sector", "")).strip(),
            "founded":     str(row.get("Founded Year", "")).strip(),
            "team_size":   str(row.get("Team Size", "")).strip(),
            "mrr":         str(row.get("Monthly Revenue", "")).strip(),
            "burn":        str(row.get("Monthly Burn", "")).strip(),
            "cash":        str(row.get("Cash on Hand", "")).strip(),
            "tam":         str(row.get("TAM (billions)", "")).strip(),
            "prior_funding": str(row.get("Prior Funding", "")).strip(),
            "investors":   str(row.get("Notable Investors", "")).strip(),
            "website":     str(row.get("Website", "")).strip(),
            "pitch_deck":  str(row.get("Pitch Deck Path", "")).strip(),
            "summary":     str(row.get("Description", "")).strip(),
            "yc_batch":    str(row.get("YC Batch", "")).strip(),
            "row":         i,
        })

    return deals
