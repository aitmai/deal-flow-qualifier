# Deal Flow Qualifier

AI-powered VC deal screening tool. Add startup data to Google Sheets → Claude scores each deal on 7 weighted criteria → outputs a color-coded scorecard with PASS / WATCH / NO verdicts.

## Stack
- Python + Flask (server + SSE streaming)
- Anthropic Claude API (claude-sonnet-4-6)
- Google Sheets via gspread (input + output)
- Dark dashboard UI with live progress log

## Scoring Criteria (weighted, out of 100)
| Criterion          | Weight | Max Pts | What it measures                        |
|--------------------|--------|---------|-----------------------------------------|
| Market Size        | ×2.0   | 20      | TAM size, growth rate, market timing    |
| Team               | ×2.0   | 20      | Founder background, domain expertise    |
| Traction           | ×2.0   | 20      | Revenue, users, growth signals          |
| Moat               | ×1.5   | 15      | IP, network effects, switching costs    |
| Business Model     | ×1.5   | 15      | Revenue clarity, unit economics         |
| Capital Efficiency | ×0.5   | 5       | Burn vs. revenue ratio                  |
| Risk               | ×0.5   | 5       | Overall risk (10 = lowest risk)         |

**Total: 100 points max**
- ≥ 80 → **PASS**
- 60–79 → **WATCH**
- < 60 → **NO**

---

## Setup

### Step 1 — Create the project folder and subfolders
```bash
mkdir C:\projects\python\deal-flow-qualifier
cd /c/projects/python/deal-flow-qualifier
mkdir agents sheets templates
```

### Step 2 — Place files into the correct subfolders
After downloading all files, move them into place:
```bash
mv qualifier.py agents/
mv sheets_reader.py sheets/
mv sheets_writer.py sheets/
mv dashboard.html templates/
```

Create required `__init__.py` files:
```bash
touch agents/__init__.py
touch sheets/__init__.py
```

Verify structure:
```bash
find . -type f -name "*.py" | sort
```

Should show:
```
./agents/__init__.py
./agents/qualifier.py
./app.py
./seed_deals.py
./sheets/__init__.py
./sheets/sheets_reader.py
./sheets/sheets_writer.py
```

### Step 3 — Copy credentials from competitor-mapper
```bash
cp ../competitor-mapper/credentials.json .
```

### Step 4 — Configure environment
```bash
cp .env.example .env
# Open .env and paste your ANTHROPIC_API_KEY
```

### Step 5 — Create Google Sheet
- Go to Google Drive and create a new sheet named exactly: `Deal-Flow-Qualifier`
- Add a tab named: `Deal-Submissions`
- Add these column headers in row 1 (exact spelling and case):
```
Company Name | Stage | Sector | Founded Year | Team Size | Monthly Revenue | Monthly Burn | Cash on Hand | TAM (billions) | Prior Funding | Notable Investors | Website | Pitch Deck Path | Description | YC Batch
```
- Share the sheet with your service account email from `credentials.json` (Editor access)
- The `Deal-Flow-Tracker` output tab is created automatically on first run

### Step 6 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 7 — Seed the sheet with sample data (optional)
Populates 10 real startups across PASS / WATCH / NO range to test the tool:
```bash
python seed_deals.py
```

### Step 8 — Run the app
```bash
python app.py
```

Open `http://localhost:5050` → click **▶ Run Analysis**

---

## Google Sheet — Deal-Submissions Column Guide
| Column             | Required | Example                                      |
|--------------------|----------|----------------------------------------------|
| Company Name       | Yes      | Acme AI                                      |
| Stage              | Yes      | Seed / Series A / Series B / Pre-Seed        |
| Sector             | Yes      | B2B SaaS / Fintech / Healthcare              |
| Founded Year       | No       | 2022                                         |
| Team Size          | No       | 12                                           |
| Monthly Revenue    | No       | $25K                                         |
| Monthly Burn       | No       | $40K                                         |
| Cash on Hand       | No       | $1.2M                                        |
| TAM (billions)     | No       | 50                                           |
| Prior Funding      | No       | $2M                                          |
| Notable Investors  | No       | Y Combinator, Sequoia                        |
| Website            | No       | acmeai.com                                   |
| Pitch Deck Path    | No       | (leave blank or local file path)             |
| Description        | Yes      | What the company does, traction, team background, why now |
| YC Batch           | No       | W24 / S23 (leave blank if not YC)            |

**Tips for the Description column:**
- Pack in as much signal as possible — Claude reads this field most heavily
- Include: what problem they solve, who the customer is, revenue/user numbers, team background, competitive angle
- Example: *"Acme AI automates invoice processing for SMBs using LLMs. $12K MRR, 3 months, 40 customers. Founder ex-Stripe engineer. Competing with Bill.com on price, 10x faster setup."*

---

## Project Structure
```
deal-flow-qualifier/
├── app.py                    ← Flask server + SSE streaming
├── seed_deals.py             ← populates Google Sheet with 10 sample deals
├── agents/
│   ├── __init__.py
│   └── qualifier.py          ← Claude scoring agent (weighted 100-pt scale)
├── sheets/
│   ├── __init__.py
│   ├── sheets_reader.py      ← reads Deal-Submissions tab
│   └── sheets_writer.py      ← writes Deal-Flow-Tracker tab (color-coded)
├── templates/
│   └── dashboard.html        ← dark analyst dashboard
├── credentials.json          ← Google service account (not committed)
├── .env                      ← API key (not committed)
├── .env.example              ← template
└── requirements.txt
```
