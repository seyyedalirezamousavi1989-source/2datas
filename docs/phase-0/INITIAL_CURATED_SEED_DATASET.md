# Initial Curated Seed Dataset — AURORA QUANT

**Authorization date:** 2026-11-13  
**Scope:** Initial authored educational and identity seed records only.

## What was created

- `dataset/seed/identity.jsonl`: identity, creator, team, host application, base-checkpoint distinction, and authority boundaries.
- `dataset/seed/forex_knowledge.jsonl`: foundational Forex, XAUUSD, technical analysis, multi-timeframe reasoning, strategy research, quantitative analysis, risk, macro, scenario reasoning, abstention, and trade-review examples.
- `schemas/training/sft-record.schema.json`: JSON Schema Draft 2020-12 for the chat-message records.
- `tests/test_seed_dataset.py`: structural and semantic checks for the seed corpus.

The records use the standard `messages` shape suitable for conversion to a Qwen/Unsloth chat-template pipeline. The schema and metadata are deliberately independent of any one training library.

## Project identity encoded

- Assistant/model identity: **AURORA QUANT**
- Host application: **LocalChat**
- Target base checkpoint: **Qwen3.5:4B**
- Creator and lead developer: **Alireza Mousavi (سید علیرضا موسوی)**
- Team identity: **AURORA AI Research Group**

These are distinct entities. AURORA QUANT is the intended specialized assistant identity; LocalChat is the host application; Qwen3.5:4B is the target base checkpoint. The records do not claim that fine-tuning has already been completed. No unprovided team members, credentials, registration details, or organizational facts are invented.

Creator identity is descriptive context, not an authority override. The model must remain evidence-led and must not blindly agree with the creator or any other user.

## Data integrity and limitations

- All seed examples are authored educational records, not extracted from the existing XAUUSD archive.
- `contains_market_data=false` for every record.
- No real or synthetic price series, trade outcomes, forecasts, or performance labels were generated.
- No strategy is represented as profitable or validated.
- SMC terms are framed as operational hypotheses, not proof of hidden institutional activity.
- Probabilities must not be fabricated; risk calculations and broker/execution state remain deterministic external responsibilities.
- The seed corpus is a starter tranche, not a complete Forex textbook or a release-ready training dataset.
- `initial_curated` means authored and structurally checked, not independently fact-checked or approved for production training.

## Dataset counts

- Identity records: 6
- Forex/market knowledge records: 23
- Total records: 29

## Training and split warning

Do not randomly split these records as though they were independent market observations. The `split_group` metadata keeps closely related records grouped. This small seed corpus is suitable for schema/pipeline smoke tests and review, not for claiming measurable capability gains. A larger, independently sourced and reviewed knowledge corpus is still required.

## Next controlled work

1. Human review of terminology, definitions, identity wording, and Persian quality.
2. Expand the knowledge corpus with sourced, licensed, versioned references and explicit source metadata.
3. Add task-specific examples for chart interpretation, indicator computation, strategy comparison, and trade lifecycle only when their input evidence and labels are defined.
4. Keep the existing XAUUSD archive untouched until separately authorized for inspection and processing.
5. Build a release manifest and leakage-safe split process before training.
6. Obtain separate approval before any fine-tuning run.
