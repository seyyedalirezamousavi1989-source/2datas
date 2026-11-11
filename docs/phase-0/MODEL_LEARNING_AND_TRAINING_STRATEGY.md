# Model Learning Strategy and Training Architecture — Phase 0

## 1. Purpose and authorization boundary

Define a conservative strategy for converting approved, high-integrity XAUUSD examples into model capabilities.

**Design only.** This document does not select or download a base model, inspect local model files, prepare training data, run benchmarks, install dependencies, configure GPUs, fine-tune, or modify AURORA QUANT. No training or compute-intensive experiment is authorized.

The governing objective is reliable capability improvement per unit of verified information and compute—not model size, training duration, number of methods, or benchmark spectacle.

## 2. Decide what should be learned versus computed

Do not train a language model to imitate functions that should remain exact, deterministic, or connected to live authoritative state.

### Learned capabilities (candidate scope)
- Interpret point-in-time market structure and multi-timeframe evidence.
- Explain agreement, conflict, missing context and uncertainty.
- Interpret explicitly defined forecast outputs without changing their semantics.
- Compare conditional scenarios and identify triggers/invalidation.
- Select or explain policy actions only within a frozen policy contract.
- Interpret deterministic risk outputs and identify inconsistent inputs.
- Reason over chronological position/lifecycle events.
- Summarize evidence concisely with traceable references.
- Abstain when information is missing, stale, contradictory or outside scope.

### Deterministic or externally authoritative capabilities
- Price/quote retrieval and timestamp normalization.
- Indicator/feature calculation where exact reproducibility is required.
- Position sizing, tick/contract/currency calculations, margin and risk limits.
- Broker order submission, modification, cancellation and fill state.
- Account balances, current positions and execution reconciliation.
- Hard policy gates, kill switches and permission checks.
- Dataset split, label generation and quality-control logic.

The model may request a calculation or explain its result; it must not invent or override it. Any live decision authority remains outside this dataset project and requires separate system-level approval.

## 3. Training readiness prerequisites

No training recipe is final until all of the following are known:
1. Accepted Stage 5 compatibility audit, after that project is independently completed.
2. Approved source feasibility and licensing.
3. Frozen canonical schemas and task input/output contracts.
4. Frozen target and annotation definitions with reliability evidence.
5. Leakage-safe chronological split manifests.
6. Baseline results and minimum useful capability definitions.
7. Representative task examples, including difficult and abstention cases.
8. Resource budget and reproducible training/evaluation environment.
9. Independent approval to begin training.

A large corpus cannot compensate for missing target validity or an untested evaluation design.

## 4. Base-model selection principles

Select the base model only after the task mix and data contract are stable.

Compare candidates on the same representative, held-out task suite:
- causal interpretation and timestamp discipline;
- structured input/output reliability;
- reasoning over conflicting timeframes;
- probability semantics and calibrated language;
- abstention and unknown-state handling;
- numerical faithfulness when interpreting tool outputs;
- chronological event-sequence reasoning;
- Persian and English technical comprehension if both are deployment requirements;
- latency, memory, context use, throughput and operational stability;
- license, redistribution and fine-tuning permissions.

Use a small, representative feasibility evaluation before any expensive run. Record exact model ID, weight revision, tokenizer, quantization, context configuration, inference parameters, hardware/software environment and license.

Do not select solely by parameter count, leaderboard position, fluent prose or one aggregate score. Quantized inference behavior must be tested separately from the full-precision or training checkpoint when relevant.

## 5. Training method selection: least complex method that works

Use an evidence ladder; do not assume every method is needed.

### Level 0 — Prompt/tool/schema improvements
Before training, determine whether failures are caused by unclear instructions, missing context, poor retrieval, invalid schemas, or unavailable tools. Fixing these may be more effective and safer than changing weights. This project may specify the interface but does not modify the external agent.

### Level 1 — Supervised fine-tuning (SFT)
Primary candidate when there are enough high-quality demonstrations with stable inputs, targets and policy semantics. Train task behavior, structured outputs, evidence-grounded explanations and correct abstention.

SFT examples must not teach fabricated account facts, unsupported certainty, hindsight labels or behavior that conflicts with deterministic constraints.

### Level 2 — Parameter-efficient fine-tuning (PEFT)
Consider LoRA/adapters when supported by the selected model and tooling, particularly for low-cost task experiments. Compare against full fine-tuning only if resource and quality evidence justify it. Adapter merge, quantization and deployment compatibility require separate tests.

### Level 3 — Continued pretraining/domain adaptation
Consider only if there is a demonstrated language/domain knowledge gap that cannot be addressed with task demonstrations or retrieval, and a sufficiently large, licensed, clean corpus exists. Raw OHLC rows are not automatically useful language-model pretraining material. Prevent contamination and evaluate forgetting.

### Level 4 — Preference optimization
DPO or another preference method is not a default. It requires reliable, policy-consistent preference pairs or rankings, reviewer agreement, clear comparison criteria and controls against stylistic preference overriding correctness. Do not manufacture preference pairs from model self-judgment.

### Level 5 — Reinforcement learning or online adaptation
Out of initial scope. It requires a valid reward aligned with risk-adjusted objectives, realistic execution simulation, robust safety constraints, independent evaluation and strong governance. Trading P&L alone is a noisy and exploitable reward. No online self-training or live-market weight updates are approved.

## 6. Multi-task architecture without task confusion

Prefer one coherent model with clearly typed task contracts only if it performs reliably across the task suite. Do not create a separate model per task without evidence.

Use explicit task identifiers and versioned schemas. Each example must specify:
- task ID and task version;
- input schema/version;
- output schema/version;
- permitted evidence sources;
- required abstention conditions;
- prohibited claims/actions;
- target/annotation provenance;
- split and episode identifiers.

Keep outcome forecasting, market-state interpretation, policy decision, risk interpretation, lifecycle management and post-trade review semantically distinct. They may share encoders or a base model, but must not share ambiguous target fields.

Post-trade review examples must be isolated from decision-time tasks. A model responding to a decision-time snapshot must never see later fills, realized P&L, post-trade explanations or future-confirmed labels in its input.

## 7. Recommended learning sequence

This is a proposed curriculum order, subject to task feasibility and ablation—not an automatic training schedule.

### Stage A — Schema and evidence discipline
Teach the model to parse canonical observations, timestamps, units, source status, missingness and provenance. Correctly distinguish observed, derived, estimated, unknown, unavailable, stale, ambiguous and not-yet-observable.

### Stage B — Market state and structure
Teach concise descriptions of current state, confirmed versus provisional structure, regime uncertainty and operationally defined events. Avoid overloading the model with unvalidated SMC taxonomies.

### Stage C — Multi-timeframe synthesis
Teach as-of alignment, completed versus partial bars, conflict detection and the rule that higher timeframe does not automatically override lower timeframe evidence.

### Stage D — Forecast interpretation
Teach target-specific probability semantics, horizon, calibration, censoring and uncertainty. Never conflate directional probability, barrier probability and probability of net profitable trade.

### Stage E — Conditional scenarios and abstention
Teach alternative paths, triggers, invalidation, expiry, evidence for/against and explicit NO_TRADE/WATCH/WAIT decisions. Include cases where abstention is the correct response.

### Stage F — Risk interpretation
Teach reading and validating deterministic calculator outputs, identifying missing/stale inputs and refusing unsupported arithmetic. Do not make the model the authoritative position-sizing engine.

### Stage G — Lifecycle and management
Teach event sequences, position state, partial fills, acknowledged versus requested modifications, cost-aware break-even, trailing/partial exits and reconciliation uncertainty.

### Stage H — Integrated task evaluation
Evaluate end-to-end reasoning over the same point-in-time evidence while preserving each subtask's separate metrics and hard safety gates.

Do not proceed to a later stage merely because the earlier stage's training loss decreases. Each stage must pass its own held-out behavioral evaluation.

## 8. Data mixture and sampling

Build a task mixture from verified independent episodes, not raw row counts.

- Preserve natural prevalence in validation and test.
- Use train-only sampling/weighting when a task is underrepresented.
- Do not fabricate rare market events or duplicate examples to meet quotas.
- Limit repeated adjacent snapshots from one episode.
- Retain distinct decision points when they represent different states or actions.
- Include difficult, contradictory, incomplete and abstention cases only when their semantics are defensible.
- Keep synthetic examples in a separate, unmistakably tagged development set; never report them as real market evidence.
- Track task, episode, regime, period, source and label versions for every training record.

Mixture weights are not set in this phase. They must be justified by task importance, effective sample size, deployment prevalence and validation results.

## 9. Output constraints and structured generation

For tasks requiring structured outputs:
- use a versioned schema and strict parsing/validation;
- enumerate allowed action/status values;
- distinguish absent, unknown, unavailable and not applicable;
- require units, horizon and probability event definitions;
- require evidence references for material claims;
- reject extra unsupported fields or values outside policy;
- separate model-proposed actions from tool-confirmed state.

A syntactically valid JSON response is not necessarily factually correct. Measure schema validity and semantic correctness independently.

## 10. Prevent memorization, leakage and catastrophic forgetting

Controls include:
- group by episode/source/time before splitting;
- keep paraphrases, crops, augmentations and derived views with their parent;
- prevent future target text and post-trade artifacts entering decision-time prompts;
- deduplicate near-identical demonstrations across splits;
- freeze validation/test before training;
- compare against the base model and prior approved checkpoint;
- retain a broad general-language regression suite if general chat capability matters;
- measure performance by task, time period, regime and source;
- use early stopping based on validation, not test;
- version checkpoints and preserve a reproducible rollback path.

Training loss and fluent responses are not proof of generalization. Watch for memorized timestamps, repeated phrases, spurious indicator shortcuts and overconfident outputs.

## 11. Evaluation gates after each learning stage

Evaluate:
- task-level correctness and per-class errors;
- calibration and probability semantics;
- abstention quality and coverage;
- evidence citation/traceability;
- temporal causality and stale/partial data handling;
- deterministic calculator agreement;
- event-sequence reconstruction and state consistency;
- robustness under missing, conflicting and perturbed inputs;
- latency, memory and context consumption;
- regression on previously passed tasks and general capabilities.

Compare base model, prompt-only baseline, deterministic baseline and candidate fine-tune under identical inputs and compute budgets. Use chronological validation; reserve the final test for one frozen evaluation protocol.

A critical hallucination about account, broker, order, fill or risk state blocks promotion even if average task scores improve.

## 12. Model release and governance

Every candidate release must record:
- base model and exact revision;
- training method and hyperparameters;
- dataset, schema, feature, label and split versions;
- source and licensing provenance;
- training code/configuration and environment hashes;
- random seeds and checkpoint lineage;
- training curves and failed runs;
- per-task evaluation and uncertainty;
- safety/regression results;
- known limitations and intended-use restrictions.

Do not overwrite the prior accepted model. A candidate remains a research artifact until independently reviewed and explicitly accepted.

## 13. Resource-aware experiment policy

Begin with low-cost evaluation and the smallest experiment capable of answering one question. Estimate memory, context, storage and training time before execution. Avoid parallel experiments that compete for limited hardware or make results irreproducible.

No model size, quantization, sequence length, batch size, epoch count, learning rate, adapter rank or training duration is prescribed here. These depend on the eventual base model, tooling, dataset size and measured hardware constraints.

## 14. Promotion gate

A training strategy is ready for a separately authorized experiment only when:
1. Stage 5 compatibility has been independently audited;
2. source rights and data feasibility are accepted;
3. task schemas and target semantics are frozen;
4. annotation reliability is demonstrated;
5. leakage-safe splits and baselines are available;
6. representative task suite and safety gates are frozen;
7. base-model candidates are compared fairly;
8. the method is justified by a specific measured gap;
9. resource budget and rollback plan are approved;
10. the user explicitly authorizes the experiment.

## 15. Explicit non-decisions

This document does not choose a model, prescribe hyperparameters, commit to SFT/LoRA/DPO/RL, set task mixture ratios, define a production serving architecture, or authorize training. It is a decision framework for later evidence-based choices.
