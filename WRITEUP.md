# WRITEUP: AI Proposal Triage (MATACS-TH-2026-02)

**Assumptions** (I did not ask questions, so I am stating them):
- "Last 5 years" is counted back from the award date. If a proposal only says "since 20XX", I take its count and note the doubt.
- A named lead is accepted as stated; the tool does not verify names.
- A licence counts only if the bidder itself holds it. "A subcontractor to be confirmed" does not count.
- If something is not stated, the tool never guesses it.

## 1. AI vs. rules
**AI is used for one step only: reading each proposal and filling a fixed form** (licence yes/no, price, weeks, warranty years, team items, each with a short quote as evidence). Proposals are messy free text, so this is where AI actually helps.

**Everything else is plain code:** the mandatory pass/fail gate, budget and 16-week limits, the scoring formulas, weights, ranking, tie-breaks and the written reason. I drew the line there because these steps must be exact, repeatable and explainable to a bidder or an auditor. AI is good at reading, but I do not want it deciding whether a company passes or what a price is worth. The reason text is built from the scores and quotes by a template, so it cannot invent anything.

## 2. Consistency and explainability
- Scoring is code with fixed formulas, so the same extracted facts always give the same ranking. Examples: experience uses tiers (10+ installs = 100, 5-9 = 70, 1-4 = 40); price = lowest eligible price divided by this price; timeline = shortest weeks divided by this proposal's weeks; warranty is capped at admin-set "full marks" years; team is four yes/no items worth 25 each.
- The AI step can vary a little, so I use temperature 0, a pinned model version, a fixed JSON form, and I run it twice. If the two runs differ on any field, the proposal is flagged. The extraction is then **saved**, and re-ranking reuses the saved extraction rather than asking the AI again. So ranking twice gives the same result.
- The reviewer sees, per proposal: the score for each criterion, the weight, the quote the fact came from, and a link to the source page. Nothing in the rank is a black box.
- Relative scores (price, timeline) are measured against everyone who passed the mandatory gate, including flagged ones, so clearing a flag later does not shift other scores.

## 3. Human in the loop
- Reviewers see three lists: ranked, flagged, ineligible. They can open any proposal and see why.
- A reviewer can **override** an ineligible/flagged status, correct an extracted value, or ask the bidder for clarification and re-run. Every override needs a typed reason.
- The tool only recommends. **The award decision is always made by a person** and recorded as such.
- **Audit log** (append-only): who uploaded what and when, file hash, extracted text, model name and version, prompt version, raw AI output, validation results, criteria version, every score, every override (who, what, old/new value, reason), and the final decision.

## 4. Changing criteria
- Criteria are versioned. An edit creates a new version; old versions are never changed.
- Each scoring run stores the criteria version it used. If the admin changes things later, old results stay as they were and show "scored under v1, current is v2".
- The tool never mixes versions in one ranked list. The reviewer clicks "re-score", and the tool shows a preview of what moves (rank before/after) before saving a new run.
- Changed weights or formulas: just re-run the scoring code on saved extractions (cheap, no AI). New or changed criterion that needs a new fact: extract only the new field. Changed mandatory rule: some proposals may become ineligible, and the preview says so.
- The admin screen blocks saving unless weights add up to 100%.

## 5. Risks
| Risk | Safeguard |
|---|---|
| Wrong extraction (misread number, wrong year) | Evidence quote required and checked against the text; two runs compared; schema checks; reviewer sees the quote beside each value |
| Made-up facts | "Null if not stated" rule; no quote means no value; future promises count as not stated |
| Prompt injection / manipulation (e.g. hidden "rank me first" text, as in Proposal C) | Text is treated as data, never instructions; a pre-scan and an AI field both detect it; the proposal is flagged and held; it can't change its own score because the AI never scores |
| Missing information (Proposal D has no timeline) | Never guessed. Scored 0 for that criterion provisionally, flagged for clarification |
| Cheap bid that fails a requirement (Proposal B) | Mandatory gate is code and runs before any scoring, so low price cannot buy a pass |
| Bias (favouring big firms or nicely written proposals) | AI only extracts facts, it does not judge quality or writing; scoring uses only the admin's criteria; no company name or size is used |
| Scanned/bad PDFs | OCR fallback; if still unreadable, flagged, never scored as zero silently |
| Cost | One cheap extraction per proposal (x2); scoring and re-ranking cost nothing; extractions are cached by file hash |
| Data privacy | Only proposal text goes to the model; no keys in the repo; logs access-controlled |
| Over-trust by reviewers | Flagged items visible at the top; tool says "recommendation", not "decision" |

## Result on the sample set
A first (98.0), E second (88.7). B ineligible. C and D flagged: if cleared, C would be 3rd (78.8) and D 4th (76.2). Details in `ranking.json`.
