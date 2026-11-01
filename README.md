# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** [KAMLESH KUMAR]
- **Reference:** MATACS-TH-2026-02
- **Time actually spent:**

## How I used AI tools

 You must include one place where you disagreed with or corrected the AI, and why. Example of the kind of thing to write (only use it if it is true for you): "I used Claude to help draft the extraction prompt and check my scoring maths. It first suggested letting the AI write the final score for each proposal; I changed this to code-only scoring because I wanted the same input to always give the same ranking.

## Files

- [WRITEUP.md](WRITEUP.md): answers to the five questions
- [diagram/process-flow.png](diagram/process-flow.png): flow from upload to ranked output
- [PROMPTS.md](PROMPTS.md): the extraction prompt, as I would send it
- [ranking.json](ranking.json): expected ranking of proposals A-E
- [prototype/](prototype/): optional. `score.py` is the rules-only scoring step; it needs no API key. Run `python score.py` inside the folder to reproduce the numbers in `ranking.json`.

## Short summary

AI reads each proposal and fills a fixed form with quotes as evidence. Code does everything else (pass/fail checks, scoring, ranking). A person reviews flagged items and makes the final decision. Result: A first, E second, B ineligible, C and D flagged for a human.
