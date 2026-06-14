<!-- v1.0 | propose changes in chat before editing -->

# evals/CLAUDE.md

## Owns
Quality evaluation scripts for AI agent outputs. These are NOT unit tests.
Evals measure output quality against rubrics, not code correctness.

## Does not
- Run in CI pipeline (manual quality assessment)
- Mock Gemini/Tavily (evals run with real API calls)
- Replace tests/ (different purpose entirely)

## Structure
```
evals/
├── golden_examples.json      # Input goals + expected outputs
├── eval_segment_accuracy.py  # Analyst output quality
├── eval_message_quality.py   # Strategist output quality
├── eval_end_to_end.py        # Full pipeline quality
└── results/                   # Evaluation outputs (gitignored)
```

## Contracts
Receives from: backend/agents/ (pipeline)
Receives from: golden_examples.json (test cases)
Produces for: Manual review (quality reports)
External: Real Gemini and Tavily API calls

## Evaluation Dimensions

### Analyst (segment_accuracy)
1. **Filter validity**: Does filter_rules match schema?
2. **Intent alignment**: Does segment match the goal intent?
3. **Customer coverage**: Reasonable count (not 0, not all)?

### Strategist (message_quality)
1. **Grammar/typos**: Free of errors
2. **Tone appropriateness**: Matches brand (Tana & Co.)
3. **Cultural fit**: Indian D2C fashion context
4. **Personalization tokens**: {name}, {city} used correctly
5. **Variant diversity**: Are A/B/C meaningfully different?

### End-to-end (pipeline_quality)
1. **Proposal completeness**: All fields present
2. **Reasoning coherence**: Does reasoning support choices?
3. **Channel appropriateness**: Channel matches audience

## Golden Examples Schema
```json
[
  {
    "id": "golden_001",
    "goal": "Get repeat purchases from customers who bought ethnic wear last festive season",
    "expected_segment_intent": "customers with kurta/saree orders in Oct-Mar timeframe",
    "expected_message_style": "festive",
    "expected_channel": "whatsapp"
  }
]
```
Target: 15-20 golden examples covering diverse scenarios.

## Running Evals
```bash
cd evals
python eval_end_to_end.py --samples 10 --output results/run_2026_06_11.json
```

## Scoring
Each eval outputs a score 0-100 per sample.
Manual review of low-scoring outputs required.

---
Pending: Create golden_examples.json
Changelog: v1.0 Jun 2026 initial
