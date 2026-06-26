"""
seed_deals.py
Populates the Deal-Submissions tab in Deal-Flow-Qualifier Google Sheet
with 10 real startups spanning PASS / WATCH / NO range.

Run from project root:
    python seed_deals.py
"""

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Deal-Flow-Qualifier"
TAB_NAME   = "Deal-Submissions"

HEADERS = [
    "Company Name", "Stage", "Sector", "Founded Year", "Team Size",
    "Monthly Revenue", "Monthly Burn", "Cash on Hand", "TAM (billions)",
    "Prior Funding", "Notable Investors", "Website", "Pitch Deck Path",
    "Description", "YC Batch"
]

DEALS = [
    {
        "Company Name":     "Stripe",
        "Stage":            "Growth",
        "Sector":           "Fintech / Payments Infrastructure",
        "Founded Year":     "2010",
        "Team Size":        "7000",
        "Monthly Revenue":  "$500M+",
        "Monthly Burn":     "Profitable",
        "Cash on Hand":     "$2B+",
        "TAM (billions)":   "4500",
        "Prior Funding":    "$2.2B",
        "Notable Investors":"Sequoia, Andreessen Horowitz, Founders Fund",
        "Website":          "stripe.com",
        "Pitch Deck Path":  "",
        "Description": (
            "Global payments infrastructure for the internet. Processes hundreds of billions "
            "in annual payment volume across 50+ countries. Developer-first API disrupted "
            "legacy processors. Products span payments, billing, fraud, banking-as-a-service. "
            "Strong moat via network effects and deep platform integrations."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Anduril Industries",
        "Stage":            "Series F",
        "Sector":           "Defense Tech / AI Hardware",
        "Founded Year":     "2017",
        "Team Size":        "3000",
        "Monthly Revenue":  "$200M+",
        "Monthly Burn":     "$50M",
        "Cash on Hand":     "$1B+",
        "TAM (billions)":   "900",
        "Prior Funding":    "$1.5B",
        "Notable Investors":"Founders Fund, a16z, 8VC",
        "Website":          "anduril.com",
        "Pitch Deck Path":  "",
        "Description": (
            "Defense technology company building autonomous systems and AI-powered platforms "
            "for the US military and allies. Products include Lattice AI command software, "
            "autonomous drones, counter-drone systems. $14B valuation. Multi-billion dollar "
            "DoD contracts. Extremely high barriers to entry and government contract moat."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Harvey AI",
        "Stage":            "Series C",
        "Sector":           "Legal Tech / AI",
        "Founded Year":     "2022",
        "Team Size":        "200",
        "Monthly Revenue":  "$8M",
        "Monthly Burn":     "$3M",
        "Cash on Hand":     "$100M",
        "TAM (billions)":   "1000",
        "Prior Funding":    "$206M",
        "Notable Investors":"Sequoia, OpenAI Fund, Kleiner Perkins",
        "Website":          "harvey.ai",
        "Pitch Deck Path":  "",
        "Description": (
            "AI platform for law firms and legal teams. Automates legal research, contract "
            "analysis, due diligence, and document drafting. Clients include Allen & Overy, "
            "PwC Legal, and DOJ. $100M+ ARR run rate. $715M valuation. Founders: ex-Goldman "
            "M&A lawyer and ex-DeepMind researcher. High switching costs once embedded in workflows."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Clipboard Health",
        "Stage":            "Series C",
        "Sector":           "Healthcare Staffing / Marketplace",
        "Founded Year":     "2016",
        "Team Size":        "700",
        "Monthly Revenue":  "$25M",
        "Monthly Burn":     "Profitable",
        "Cash on Hand":     "$80M",
        "TAM (billions)":   "46",
        "Prior Funding":    "$80M",
        "Notable Investors":"a16z, Y Combinator",
        "Website":          "clipboardhealth.com",
        "Pitch Deck Path":  "",
        "Description": (
            "Two-sided marketplace connecting healthcare facilities with per-diem nurses and CNAs. "
            "Addresses chronic nursing shortage. Profitable. $300M+ ARR. Operates in 50 states. "
            "Strong network effects — facility lock-in once integrated into scheduling workflow. "
            "High NPS from workers due to instant pay feature."
        ),
        "YC Batch": "W17",
    },
    {
        "Company Name":     "Bland AI",
        "Stage":            "Series A",
        "Sector":           "AI / Voice Automation",
        "Founded Year":     "2023",
        "Team Size":        "30",
        "Monthly Revenue":  "$500K",
        "Monthly Burn":     "$400K",
        "Cash on Hand":     "$18M",
        "TAM (billions)":   "50",
        "Prior Funding":    "$22M",
        "Notable Investors":"Scale Venture Partners, Y Combinator",
        "Website":          "bland.ai",
        "Pitch Deck Path":  "",
        "Description": (
            "AI phone calling platform automating inbound and outbound calls for enterprises. "
            "Handles sales, support, and scheduling at scale with human-like voice AI. "
            "1M+ calls per day capacity. Strong early traction in healthcare, real estate, "
            "and financial services. Competitive market with Vapi and Retell entering."
        ),
        "YC Batch": "W24",
    },
    {
        "Company Name":     "Part Analytics",
        "Stage":            "Seed",
        "Sector":           "B2B SaaS / Supply Chain",
        "Founded Year":     "2021",
        "Team Size":        "8",
        "Monthly Revenue":  "$167K",
        "Monthly Burn":     "$150K",
        "Cash on Hand":     "$1.5M",
        "TAM (billions)":   "20",
        "Prior Funding":    "$3M",
        "Notable Investors":"Y Combinator",
        "Website":          "partanalytics.com",
        "Pitch Deck Path":  "",
        "Description": (
            "AI-powered component sourcing and supply chain risk platform for hardware manufacturers. "
            "Helps procurement teams find alternative parts, track lead times, and reduce BOM costs. "
            "$2M ARR. Market is large but fragmented with entrenched competitors like IHS Markit. "
            "Founder has prior supply chain ops background at Flex."
        ),
        "YC Batch": "W22",
    },
    {
        "Company Name":     "Captions",
        "Stage":            "Series B",
        "Sector":           "AI / Creator Tools",
        "Founded Year":     "2021",
        "Team Size":        "80",
        "Monthly Revenue":  "$2M",
        "Monthly Burn":     "$1.5M",
        "Cash on Hand":     "$50M",
        "TAM (billions)":   "70",
        "Prior Funding":    "$60M",
        "Notable Investors":"Kleiner Perkins, Index Ventures",
        "Website":          "captions.ai",
        "Pitch Deck Path":  "",
        "Description": (
            "AI-powered video creation and editing app. Features: auto-captions, AI eye contact "
            "correction, teleprompter, short-form video generation. 10M+ downloads. $500M valuation. "
            "Strong consumer traction but thin monetization at $9.99/mo. Heavy competition from "
            "CapCut (ByteDance), Descript, Adobe. Founders ex-Apple and ex-Snapchat."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Turo",
        "Stage":            "Pre-IPO",
        "Sector":           "Marketplace / Mobility",
        "Founded Year":     "2010",
        "Team Size":        "900",
        "Monthly Revenue":  "$73M",
        "Monthly Burn":     "$20M",
        "Cash on Hand":     "$200M",
        "TAM (billions)":   "120",
        "Prior Funding":    "$500M",
        "Notable Investors":"IAC, Kleiner Perkins, August Capital",
        "Website":          "turo.com",
        "Pitch Deck Path":  "",
        "Description": (
            "Peer-to-peer car sharing marketplace — Airbnb for cars. 350,000+ vehicles listed "
            "across US, Canada, UK, Australia, France. Revenue ~$880M (2023). Path to profitability "
            "unclear; high insurance costs and regulatory friction in key markets. Withdrew IPO S-1 "
            "in 2022. Competes with Zipcar and traditional rental incumbents."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Nuvation Bio",
        "Stage":            "Public (NUVB)",
        "Sector":           "Biotech / Oncology",
        "Founded Year":     "2018",
        "Team Size":        "150",
        "Monthly Revenue":  "$0",
        "Monthly Burn":     "$15M",
        "Cash on Hand":     "$300M",
        "TAM (billions)":   "8",
        "Prior Funding":    "$400M",
        "Notable Investors":"Perceptive Advisors, RA Capital",
        "Website":          "nuvationbio.com",
        "Pitch Deck Path":  "",
        "Description": (
            "Clinical-stage biopharmaceutical company focused on oncology. Lead asset taletrectinib "
            "targeting ROS1+ non-small cell lung cancer — NDA filed with FDA 2024. No revenue. "
            "Binary outcome risk on FDA approval. TAM limited to ROS1+ subset (~2% of NSCLC). "
            "David Hung founded Medivation which sold to Pfizer for $14B — strong founder pedigree."
        ),
        "YC Batch": "",
    },
    {
        "Company Name":     "Stealth AI Startup",
        "Stage":            "Pre-Seed",
        "Sector":           "Enterprise SaaS / AI",
        "Founded Year":     "2024",
        "Team Size":        "2",
        "Monthly Revenue":  "$0",
        "Monthly Burn":     "$20K",
        "Cash on Hand":     "$50K",
        "TAM (billions)":   "100",
        "Prior Funding":    "$0",
        "Notable Investors":"None",
        "Website":          "",
        "Pitch Deck Path":  "",
        "Description": (
            "Building an AI tool for enterprise knowledge management. No product. No revenue. "
            "No customers. Founder has 2 years experience as junior software engineer. "
            "Competing with Notion, Confluence, Microsoft SharePoint, and multiple well-funded "
            "AI startups. Pitch deck only. Asking $2M on $10M pre-money cap with zero traction."
        ),
        "YC Batch": "",
    },
]


def seed():
    print("Connecting to Google Sheets...")
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    gc    = gspread.authorize(creds)

    try:
        sh = gc.open(SHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\nERROR: Sheet '{SHEET_NAME}' not found.")
        print("Make sure you:")
        print("  1. Created a Google Sheet named exactly: Deal-Flow-Qualifier")
        print("  2. Shared it with your service account email (Editor access)")
        return

    # Get or create the Deal-Submissions tab
    try:
        ws = sh.worksheet(TAB_NAME)
        print(f"Found existing tab: {TAB_NAME}")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=100, cols=len(HEADERS))
        print(f"Created tab: {TAB_NAME}")

    # Clear existing data, write headers + rows
    ws.clear()
    ws.update([HEADERS], "A1")

    rows = [[d[h] for h in HEADERS] for d in DEALS]
    end_col = chr(ord("A") + len(HEADERS) - 1)
    ws.update(rows, f"A2:{end_col}{1 + len(rows)}")

    # Bold the header row
    ws.format(f"A1:{end_col}1", {"textFormat": {"bold": True}})

    print(f"\nDone. {len(DEALS)} deals written to '{SHEET_NAME} → {TAB_NAME}'")
    print("Open http://localhost:5050 and click ▶ Run Analysis")


if __name__ == "__main__":
    seed()
