import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior venture capital analyst with 15 years of experience across early-stage and growth investments.
You evaluate startups with precision, skepticism, and clarity. You do not hype. You do not over-penalize.
You score objectively based only on the information provided, and you flag what is missing.

You must respond ONLY with a valid JSON object — no preamble, no markdown, no explanation outside the JSON."""

SCORING_PROMPT = """Evaluate this startup submission and return a VC scorecard as JSON.

STARTUP DATA:
Company:           {company}
Stage:             {stage}
Sector:            {sector}
Founded:           {founded}
Team Size:         {team_size}
Monthly Revenue:   {mrr}
Monthly Burn:      {burn}
Cash on Hand:      {cash}
TAM (billions):    ${tam}B
Prior Funding:     {prior_funding}
Notable Investors: {investors}
Website:           {website}
YC Batch:          {yc_batch}

Description:
{summary}

Score each criterion from 1–10. Be honest. A 7 is good. A 9 is exceptional. A 3 means real concerns.
Each criterion has a weight — the weighted score is (raw score × weight). Total is out of 100.

CRITERIA & WEIGHTS:
1. market_size        (weight 20) — TAM size, growth rate, and market timing
2. team               (weight 20) — Founder background, relevant experience, domain expertise
3. traction           (weight 20) — Revenue, users, growth rate, retention signals
4. moat               (weight 15) — Defensibility: IP, network effects, switching costs, data advantage
5. business_model     (weight 15) — Revenue model clarity, unit economics, path to profitability
6. capital_efficiency (weight  5) — How well they deploy capital; burn vs. revenue ratio
7. risk               (weight  5) — Overall risk level (10 = lowest risk, 1 = highest risk)

WEIGHTED SCORE FORMULA:
(market_size × 2) + (team × 2) + (traction × 2) + (moat × 1.5) + (business_model × 1.5) + (capital_efficiency × 0.5) + (risk × 0.5)
Max possible = 100.

VERDICT RULES:
- Score >= 80: PASS
- Score 60-79: WATCH
- Score < 60: NO

Respond ONLY with this exact JSON structure:
{{
  "scores": {{
    "market_size": <1-10>,
    "team": <1-10>,
    "traction": <1-10>,
    "moat": <1-10>,
    "business_model": <1-10>,
    "capital_efficiency": <1-10>,
    "risk": <1-10>
  }},
  "total_score": <weighted total out of 100, rounded to 1 decimal>,
  "verdict": "<PASS|WATCH|NO>",
  "strengths": "<2-3 sentence summary of strongest signals>",
  "concerns": "<2-3 sentence summary of biggest red flags or missing info>",
  "next_step": "<one specific recommended action>"
}}"""


def qualify_deal(deal, log_fn=None):
    prompt = SCORING_PROMPT.format(
        company=      deal.get("company",      "Unknown"),
        stage=        deal.get("stage",        "Not specified"),
        sector=       deal.get("sector",       "Not specified"),
        founded=      deal.get("founded",      "Not specified"),
        team_size=    deal.get("team_size",    "Not specified"),
        mrr=          deal.get("mrr",          "Not specified"),
        burn=         deal.get("burn",         "Not specified"),
        cash=         deal.get("cash",         "Not specified"),
        tam=          deal.get("tam",          "Not specified"),
        prior_funding=deal.get("prior_funding","Not specified"),
        investors=    deal.get("investors",    "Not specified"),
        website=      deal.get("website",      "Not provided"),
        yc_batch=     deal.get("yc_batch",     "N/A"),
        summary=      deal.get("summary",      "No description provided."),
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)

        # Attach metadata
        parsed["company"] = deal["company"]
        parsed["sector"]  = deal.get("sector", "")
        parsed["stage"]   = deal.get("stage", "")

        # Recalculate weighted total server-side
        s = parsed.get("scores", {})
        weighted = (
            s.get("market_size", 0)        * 2.0 +
            s.get("team", 0)               * 2.0 +
            s.get("traction", 0)           * 2.0 +
            s.get("moat", 0)               * 1.5 +
            s.get("business_model", 0)     * 1.5 +
            s.get("capital_efficiency", 0) * 0.5 +
            s.get("risk", 0)               * 0.5
        )
        parsed["total_score"] = round(weighted, 1)

        # Re-apply verdict rules server-side
        t = parsed["total_score"]
        if t >= 80:
            parsed["verdict"] = "PASS"
        elif t >= 60:
            parsed["verdict"] = "WATCH"
        else:
            parsed["verdict"] = "NO"

        if log_fn:
            log_fn(f"  → {deal['company']}: {parsed['verdict']} (score: {parsed['total_score']}/100)")

        return parsed

    except Exception as e:
        if log_fn:
            log_fn(f"  ERROR qualifying {deal['company']}: {e}")
        return {
            "company":     deal["company"],
            "sector":      deal.get("sector", ""),
            "stage":       deal.get("stage", ""),
            "scores":      {},
            "total_score": 0,
            "verdict":     "ERROR",
            "strengths":   "",
            "concerns":    str(e),
            "next_step":   "Retry with more complete data",
        }
