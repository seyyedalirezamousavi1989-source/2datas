# Task Catalog and Priority — Phase 0

## Purpose

Define the smallest coherent set of learning objectives that covers the intended capability without multiplying near-identical tasks. This is a design catalog, not authorization to create examples or labels.

A task is retained only if it has:
- a distinct user-facing or research purpose;
- a target that can be defined and evaluated independently;
- point-in-time-valid inputs;
- a baseline against which incremental value can be measured.

## Priority tiers

Priorities are provisional design priorities, not a commitment to implementation order. Source feasibility and the accepted Stage 5 interface may change them.

### Tier 1 — Core decision intelligence

| ID | Task | Input focus | Output/target concept | Why it earns a place |
|---|---|---|---|---|
| T01 | Price/structure state assessment | Recent price action, market structure and return context; volatility features may be context only | Trend, range, structural transition or indeterminate price/structure state | Provides the current structural context without owning a volatility-regime target |
| T02 | Multi-timeframe synthesis | As-of snapshots of selected timeframes | Alignment, conflict, dominant context, and missing/partial context | Prevents isolated timeframe reasoning |
| T03 | Probabilistic outcome forecast | Causal market state and explicit horizon | Probabilities for a defined future event space | Separates forecasting from trading policy |
| T04 | Conditional setup decision | T01–T03 evidence plus verified constraints | LONG, SHORT, WATCH, WAIT_FOR_CONFIRMATION, NO_TRADE, or ABSTAIN with conditions and invalidation | Teaches disciplined action and abstention |
| T05 | Risk-plan interpretation | Deterministic calculator outputs and broker/account facts | Explain feasibility, constraints, and risk warnings | Connects analysis to risk without asking the model to calculate authoritative values |
| T06 | Trade lifecycle reasoning | Ordered, timestamped trade/market events | Hold, reduce, protect, exit, or no-action rationale | Covers management after entry, not just entry selection |

### Tier 2 — Supporting capabilities

| ID | Task | Input focus | Output/target concept | Retention condition |
|---|---|---|---|---|
| T07 | Structure-event interpretation | Price history and a frozen operational definition | Confirmed/provisional swing, break, failure, invalidation | Retain only if labeling reliability and incremental value are demonstrated |
| T08 | Execution-cost interpretation | Bid/ask, spread, slippage, commission, fills, order constraints | Cost/quality assessment and execution-state explanation | Requires trustworthy quote/fill history |
| T09 | Volatility-regime characterization | Causally available range/return/volatility features and their temporal context | Volatility state, expansion/contraction, clustering and volatility transition | Keep separate only as a distinct volatility target with an independent consumer and incremental value; otherwise merge/defer |
| T10 | News-context interpretation | Point-in-time published facts and source metadata | Fact/expectation/interpretation separation and relevance | Requires licensed archives with actual publication/availability timestamps |
| T11 | Visual chart reasoning | Chart image synchronized with canonical numeric snapshot | Evidence extraction and consistency check | Retain only if controlled tests show value beyond structured inputs |

### Tier 3 — Research candidates, not default dataset tasks

- SMC-specific concepts (liquidity pools, sweeps, FVG, order blocks, premium/discount).
- Fine-grained pattern taxonomy.
- Large indicator libraries.
- Long-form narrative explanations.
- Synthetic market scenarios beyond schema and software tests.

These candidates must pass a definition/reliability study and an incremental-value test before promotion. Familiar terminology is not evidence of objective ground truth.

## Shared context vs task-specific target

Avoid building one full duplicated sample for every task. Represent:
- one canonical as-of market snapshot;
- one reusable set of validated feature references;
- task-specific target and evaluation metadata;
- only the minimal task-specific context needed to interpret the target.

T01 and T09 may reference some of the same causal volatility features, but T01 owns price/structure-state outputs while T09 owns volatility-regime outputs. Do not duplicate a shared label or create two task rows for one target; T09 remains conditional on independent value. T03 forecast probabilities must not be copied into T04 as if they were observed facts; T04 may consume a versioned forecast output as an input to a separately defined policy decision.

## Output contract principles

All task outputs must distinguish:
1. evidence references;
2. observed facts;
3. derived measurements;
4. interpretation;
5. forecast (if applicable);
6. action/policy decision (if applicable);
7. uncertainty and abstention reason;
8. invalidation or next observation condition.

Do not require verbose prose when a compact structured answer carries the same information. Natural-language explanations are included only when they add a separately testable reasoning capability.

## Dataset value tests

A task is a candidate for removal or merger if:
- its target is a deterministic restatement of another target;
- it has no distinct evaluation metric or downstream consumer;
- it is mostly repeated text over the same market snapshot;
- annotation agreement is poor and cannot be improved with a precise definition;
- it adds no stable incremental value over simpler tasks;
- its source requirements cannot be met reliably.

## Open design questions

- Which decision cadence and horizon are primary for intended XAUUSD use?
- Which timeframe set is actually needed at that cadence?
- Should T01 and T09 be one task or separate targets after empirical definition?
- Which T07 concepts can be labeled consistently without hindsight?
- Does T11 add value after controlling for identical numeric context?
