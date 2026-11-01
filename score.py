"""
Rules-only scoring step. No AI and no API key needed.
Input: extracted facts (what the AI extraction step would return, after validation).
Output: status, score and ranking for each proposal.
Run: python score.py
"""
import json

CRITERIA = {  # in the real tool this comes from the admin screens (versioned)
    "version": "solar-v1",
    "budget_ceiling": 260000,
    "max_weeks": 16,
    "weights": {"experience": 30, "price": 25, "timeline": 15, "warranty": 15, "team": 15},
    "panel_full_marks_years": 25,
    "workmanship_full_marks_years": 12,
}
assert sum(CRITERIA["weights"].values()) == 100


def mandatory_ok(p):
    return p["licence_held"] is True and p["wsib"] is True and p["insurance_5m"] is True


def experience_score(n):
    if n >= 10: return 100
    if n >= 5:  return 70
    if n >= 1:  return 40
    return 0


def warranty_score(p, c):
    panel = min(p["panel_years"] / c["panel_full_marks_years"], 1) * 100
    work = min(p["workmanship_years"] / c["workmanship_full_marks_years"], 1) * 100
    return 0.5 * panel + 0.5 * work


def team_score(p):
    items = ["named_lead", "crew_stated", "safety_plan", "monitoring_plan"]
    return 25 * sum(1 for i in items if p[i])


def run(data, c=CRITERIA):
    results = {}
    # 1) status checks
    for k, p in data.items():
        if not mandatory_ok(p):
            results[k] = {"status": "ineligible", "why": "failed a mandatory pass/fail criterion"}
        elif p["price"] > c["budget_ceiling"] or (p["weeks"] is not None and p["weeks"] > c["max_weeks"]):
            results[k] = {"status": "ineligible", "why": "over budget ceiling or over 16 weeks"}
        elif p["suspicious_instructions"]:
            results[k] = {"status": "flagged", "why": "embedded instruction aimed at the reviewing system"}
        elif p["weeks"] is None:
            results[k] = {"status": "flagged", "why": "completion time not stated"}
        else:
            results[k] = {"status": "ranked", "why": ""}

    # 2) pool for relative scores = everything that passed the mandatory gate and hard limits
    #    (flagged ones stay in the pool so clearing a flag later does not change other scores)
    pool = [k for k, r in results.items() if r["status"] != "ineligible"]
    best_price = min(data[k]["price"] for k in pool)
    weeks_known = [data[k]["weeks"] for k in pool if data[k]["weeks"] is not None]
    best_weeks = min(weeks_known)

    # 3) weighted scores
    w = c["weights"]
    for k in pool:
        p = data[k]
        parts = {
            "experience": experience_score(p["installs_100kw_5yr"]),
            "price": best_price / p["price"] * 100,
            "timeline": 0 if p["weeks"] is None else best_weeks / p["weeks"] * 100,
            "warranty": warranty_score(p, c),
            "team": team_score(p),
        }
        total = sum(parts[n] * w[n] / 100 for n in parts)
        results[k].update({"parts": {n: round(v, 1) for n, v in parts.items()}, "score": round(total, 1)})

    # 4) rank only the clean ones; tie-break = higher experience, then lower price
    ranked = sorted([k for k, r in results.items() if r["status"] == "ranked"],
                    key=lambda k: (-results[k]["score"], -results[k]["parts"]["experience"], data[k]["price"]))
    for i, k in enumerate(ranked, 1):
        results[k]["rank"] = i
    return results


if __name__ == "__main__":
    with open("extracted_sample.json") as f:
        out = run(json.load(f))
    for k in sorted(out):
        print(k, json.dumps(out[k]))
