# Dataset Composition and Redundancy Control — Phase 0

## 1. Objective

Specify how a future release should select a compact set of informative examples without inflating row count through repeated snapshots, paraphrased explanations, overlapping windows, or artificial class balancing.

This is a selection policy, not permission to materialize or generate examples.

## 2. Unit of information

The primary unit is not a text row. It is a **decision-time information state**:

- one canonical instrument and decision timestamp;
- one point-in-time MarketSnapshot;
- a known set of available observations and features;
- zero or more independently defined task targets;
- provenance, quality, and evaluation metadata.

Multiple tasks may reference the same snapshot only when they have genuinely distinct targets. Repeated copies of the same snapshot with cosmetic wording changes do not create new information.

## 3. Example admission gates

A candidate example is eligible only if all applicable gates pass:

1. **Source validity:** provenance, instrument mapping, time basis, and source limitations are known.
2. **Causal validity:** every input was available at decision time.
3. **Target validity:** target definition, horizon, confirmation, costs and ambiguity rules are frozen.
4. **Quality validity:** no unresolved corruption, invalid price path, or unsupported field.
5. **Distinctness:** not a duplicate or near-duplicate under the task-specific rule.
6. **Task value:** supports a distinct capability and has a defined evaluation.
7. **Split safety:** can be assigned to a chronological split without contaminating another example's target window.
8. **Coverage value:** contributes useful time/regime/source coverage rather than merely increasing counts.

A failed gate results in exclusion or a typed unresolved status—not silent repair or fabricated certainty.

## 4. Redundancy classes

Detect and report at least these categories separately:

- **Exact source duplicate:** same source identity and revision.
- **Exact semantic duplicate:** same instrument, event/time interval, price basis, and source revision after canonicalization.
- **Near-duplicate window:** highly overlapping observation windows with effectively the same target event.
- **Repeated task paraphrase:** same snapshot, task definition, target, and answer semantics with changed wording only.
- **Feature duplication:** deterministic restatement or near-equivalent transform with no separate consumer.
- **Cross-source corroboration:** similar observations from independent providers; not automatically a duplicate and may be valuable for robustness.
- **Repeated event sampling:** many adjacent decision timestamps describing one continuous market move.

Do not collapse cross-source corroboration into one record. Preserve source identity and decide whether it belongs in robustness analysis or a source-specific task.

## 5. Overlapping windows and effective sample size

Adjacent time windows often share most of their candles and may share the same future target interval. They are not independent observations.

For every task/horizon, record:
- input window start/end;
- decision timestamp;
- target start/end or event interval;
- overlap group/cluster identifier where windows materially overlap;
- split/purge relationship.

Selection and evaluation must account for clusters of overlapping windows. Raw row count must never be presented as the number of independent examples.

Do not set a universal sampling interval before studying decision cadence, horizon, market activity, and label overlap. A fixed one-minute row cadence can create huge volumes of near-identical states.

## 6. Event-centered coverage

Prefer a defensible mix of informative market states rather than uniform duplication of every timestamp. Candidate coverage dimensions include:
- trend, range, transition, and unresolved conditions;
- volatility expansion/contraction and unusual volatility;
- session and session-transition context;
- meaningful structure breaks/failures under frozen definitions;
- spread/liquidity/execution conditions where trustworthy data exists;
- scheduled macro-event windows where point-in-time archives are reliable;
- scenario activation, invalidation, and expiry;
- trades, rejected setups, NO_TRADE decisions, and management events.

Event-centered selection must not become hindsight cherry-picking. Event definitions and selection rules must be frozen without inspecting final test outcomes. Retain representative ordinary conditions as well as rare events.

## 7. Class imbalance and abstention

Do not synthetically balance the natural market distribution by duplicating rare examples or deleting ordinary conditions.

For each task, report:
- natural prevalence by chronological period and regime;
- count and effective count per class/event;
- missing, ambiguous, censored, and abstention rates;
- concentration by source, session, date, and market episode.

If training requires weighting or sampling, preserve an untouched natural-distribution evaluation set and record the transformation. Never let oversampling copies cross split boundaries.

NO_TRADE, unresolved, and unavailable states must not be collapsed into one negative class. They represent different reasons and may have different downstream uses.

## 8. Negative and hard-negative examples

A negative example is meaningful only relative to a precise target definition.

Useful candidates include:
- apparent breakout that fails under the frozen rule;
- plausible setup that lacks activation confirmation;
- attractive directional forecast blocked by risk constraints;
- setup invalidated before entry;
- rejected/requoted/partial-fill execution where the broker evidence is available;
- chart pattern whose structured data does not support the visual interpretation.

Do not create hard negatives by selecting examples because a model previously failed on them and then evaluating on the same examples. Keep mining/curation procedures separate from the final test set.

## 9. Text and explanation economy

Use compact structured evidence references by default. Add natural-language explanation only when it teaches a distinct skill:
- separating facts from inference;
- explaining conflicting evidence;
- stating invalidation and uncertainty;
- interpreting a deterministic risk result;
- explaining why abstention is appropriate.

Do not create many paraphrases of one ideal answer as a substitute for diverse market evidence. If language variation is ever used, it must not be counted as additional independent market examples.

## 10. Sampling and split order

The future process should:
1. establish canonical source identity and deduplication;
2. form point-in-time snapshots;
3. resolve target windows and overlap groups;
4. assign chronological train/validation/test partitions;
5. apply purge/embargo constraints;
6. perform any train-only sampling or weighting;
7. verify no related episode/duplicate/overlap crosses partitions;
8. report both raw record counts and effective independent coverage.

Do not randomly split individual JSONL rows after paraphrasing or expanding examples.

## 11. Release-level composition report

Every future release should publish:
- counts by task, target, status, source, timeframe and period;
- duplicate and near-duplicate rates by category;
- overlapping-window and episode-cluster statistics;
- class/event prevalence and effective sample estimates;
- coverage across sessions/regimes/volatility periods;
- exclusion counts and reason codes;
- missing/ambiguous/censored rates;
- split sizes, date boundaries, purged records and embargo intervals;
- any train-only weighting/sampling configuration.

## 12. Removal rule

Remove or merge examples when they add no new source evidence, target outcome, independent episode, or distinct reasoning capability. Retain an example when it provides independent corroboration, a meaningful edge case, a new regime/period, or a separately testable target—even if its numeric values resemble another example.

The governing test is not “does this row look different?” but “does this example contribute reliable, non-leaking information that is not already represented?”
