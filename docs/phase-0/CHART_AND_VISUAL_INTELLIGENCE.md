# Chart and Visual Market Intelligence — Phase 0

## 1. Purpose and status

Define whether and how chart images may add useful information to the XAUUSD intelligence dataset beyond structured market data.

**Design only.** No chart image, source archive, or market data has been inspected or generated for this document. No image model, visual feature extractor, annotation pipeline, dataset, or training run is authorized.

The governing principle is evidence efficiency: retain visual learning only when it provides measurable, robust information that cannot be represented more accurately, cheaply, and reproducibly by structured data.

## 2. Separate the information modalities

Keep these input modalities explicit and independently traceable:

- **Structured market data:** OHLC, bid/ask, ticks, spread, volume with documented semantics, and timestamps.
- **Derived analytical state:** causal features, confirmed/provisional structure, volatility, session and event context, with definition versions.
- **Rendered chart image:** a deterministic visual rendering of a precisely identified market snapshot.
- **Human/model visual annotation:** a subjective interpretation tied to the image and annotator/method version.

Do not treat a chart image as a new independent market observation if it is merely a rendering of the same OHLC data. It may help a vision model recognize spatial patterns, but it does not add source information by itself.

## 3. Canonical chart snapshot contract

Every image must reference an immutable chart snapshot manifest containing:

- snapshot_id and image_id;
- instrument and exact provider symbol;
- source dataset/version and source record references;
- price basis (bid, ask, mid, last, or documented OHLC convention);
- timeframe and bar interval boundaries;
- first and last included bar timestamps;
- image creation timestamp and decision cutoff;
- per-bar availability and completion status;
- renderer name/version and configuration hash;
- image dimensions, format and checksum;
- axis scale, visible price range and time range;
- candle/body/wick and missing-bar rendering rules;
- overlays, indicators, annotations and their source/version;
- whether the last bar is partial;
- any crop, resize, compression or augmentation lineage.

The image and its manifest must be reproducibly linked. If the underlying data or renderer changes, produce a new snapshot identity rather than silently replacing the old image.

## 4. Point-in-time and visual leakage rules

A chart shown for a decision at time t may include only observations available by t under the same source-availability contract as structured tasks.

Prohibit:
- candles after the decision cutoff;
- future-confirmed swing points plotted at their historical pivot without indicating that they were not yet known;
- zones or levels drawn using later reactions;
- future labels, trade outcomes, entry/exit markers, or post-event annotations;
- titles, filenames, captions, or overlays that reveal the target;
- axes or chart extents selected using future extrema;
- image crops that encode whether a future target was hit;
- augmentations that move or remove information in a way that changes the underlying label semantics.

A pivot may be drawn retrospectively only in a hindsight-analysis task explicitly marked as such. It must not appear in a point-in-time decision image as if it were already confirmed.

## 5. Rendering policy

Use a small, frozen set of chart templates. Avoid decorative chart variation that adds pixels but not evidence.

For each template, define:
- dimensions and aspect ratio;
- candle width, spacing and color semantics;
- background and grid policy;
- axis labels and tick density;
- time/price scaling and normalization;
- visible lookback selection;
- treatment of weekends, session gaps and missing bars;
- indicator/overlay set and exact causal definitions;
- handling of partial bars and source corrections.

Keep price-scale information interpretable. If normalization is used, store the transform and preserve the ability to recover original prices. Do not normalize each image in a way that hides economically meaningful absolute price, spread, tick or volatility context unless the task specifically requires relative geometry.

No overlay should be included merely because it is visually popular. Every overlay must have a declared consumer task and incremental-value rationale.

## 6. Multi-timeframe visual inputs

A multi-timeframe image group must be a synchronized snapshot, not a collage of charts captured at unrelated times.

For each panel, preserve its timeframe, last eligible completed bar, partial-bar status, source availability and snapshot cutoff. The group manifest must identify the shared decision timestamp and the as-of rule for every panel.

If panels use different price scales or lookback durations, record those differences. Do not let layout, panel size or ordering imply a certainty or priority that is not present in the underlying data.

Compare at least:
- structured MTF inputs only;
- independent single-timeframe images;
- synchronized multi-panel images;
- combined structured + image inputs.

## 7. Visual task families

Potential tasks, subject to evidence and separate admission, include:
- identify visible candle/price geometry and chart quality issues;
- describe a visible pattern without asserting hidden causes;
- compare image-visible structure with a causal structured assessment;
- identify discrepancies between chart rendering and source data;
- summarize alignment/conflict across synchronized panels;
- identify whether the image is insufficient, stale, partial or ambiguous.

Do not use visual-only labels for exact financial calculations, broker specifications, risk sizing, or execution status. Those require authoritative structured inputs and deterministic calculation.

## 8. Annotation contract

Any visual annotation must reference the exact image snapshot and include:
- task and label-definition version;
- annotator type (human, model, or rule);
- annotator/model identity and version where permitted;
- annotation timestamp;
- evidence region or coordinates when meaningful;
- label status (confirmed, provisional, ambiguous, unavailable);
- confidence semantics and calibration status;
- disagreement/adjudication history;
- whether the annotator had access to structured data or future outcomes.

For subjective concepts such as chart patterns, BOS/CHoCH, order blocks or liquidity sweeps, maintain operational guidelines and independent annotation where feasible. Measure inter-annotator agreement and disagreement by timeframe/regime. Do not treat model-generated captions as ground truth simply because they are fluent.

## 9. Image-to-data consistency

Every chart image must be testable against its source snapshot.

Checks should cover:
- candle count and interval alignment;
- OHLC values and price basis;
- timestamp order and timezone;
- missing bars and session gaps;
- partial candle status;
- axis bounds and scaling;
- overlays and indicator values;
- annotations' source events and availability times;
- renderer determinism and image checksum.

A mismatch must invalidate or quarantine the image rather than silently retaining a misleading visual example.

## 10. Dataset pairing and duplication

When image and structured data describe the same snapshot, link them with stable IDs. Do not duplicate the same market episode across train/validation/test merely because it has different crops, colors, resolutions, or panel layouts.

Split by chronological market episode and source lineage before generating derived image variants. All crops/augmentations from one source snapshot must remain in the same split. Near-duplicate detection should include underlying time/price window identity, not only image pixel similarity.

Avoid storing many visually redundant charts. Prefer representative snapshots that add a distinct state, transition, ambiguity, or task-relevant context.

## 11. Evaluation and modality ablation

Image use must earn its complexity through controlled ablation on identical chronological samples and target definitions.

Compare:
1. structured-data baseline;
2. image-only model;
3. structured + image model;
4. structured model with equivalent derived features;
5. where useful, human/annotator reference performance.

Report:
- task-appropriate predictive and calibration metrics;
- incremental value and confidence intervals;
- performance by regime, timeframe, session and image quality;
- robustness to renderer/template changes;
- sensitivity to resolution, crop and scale;
- inference latency, VRAM/RAM, storage and preprocessing cost;
- failure and abstention rates.

If image inputs do not provide stable incremental value, omit them from the core dataset or keep them as a separately versioned research track. Do not keep image data solely because it makes the project appear more advanced.

## 12. Augmentation restrictions

Augmentation must preserve task semantics and be recorded. Potentially safe transformations require empirical validation; none is automatically approved.

Do not apply horizontal flips to time series, arbitrary rotations, vertical flips, or transformations that reverse chronology or price direction. Avoid color changes that invert bullish/bearish semantics unless the model is explicitly trained to be invariant and this is validated. Cropping/resizing must not remove critical context or leak labels.

Every derived image must retain parent snapshot ID, transformation name/version and parameters. Original canonical images remain immutable.

## 13. Privacy, licensing and provenance

For internally rendered charts, verify rights to the underlying market data and any third-party fonts/assets. For externally supplied chart screenshots, verify source, ownership, redistribution and model-training rights, and whether platform UI or account information exposes sensitive data.

Do not assume a chart screenshot may be used for training merely because it is publicly viewable. Avoid capturing broker account identifiers, balances, personal details or credentials.

## 14. Promotion gate

Visual data may enter a later approved dataset only when:
1. a specific task requires visual representation;
2. the source data and point-in-time snapshot are traceable;
3. rendering is deterministic and versioned;
4. no future information is visible or inferable from metadata;
5. image/data consistency checks pass;
6. annotation quality is measured;
7. split lineage prevents near-duplicate leakage;
8. structured-vs-visual ablation demonstrates incremental value;
9. resource and licensing costs are justified;
10. Stage 5 compatibility and source feasibility are reviewed;
11. the user separately approves image inspection/generation and the next phase.

## 15. Explicit non-decisions

This document does not select a vision model, image resolution, renderer, chart template, indicator overlay set, annotation vendor, augmentation policy, or image dataset size. It does not authorize inspecting XAUUSD.zip, creating chart images, processing market data, labeling, implementation or training.

Those decisions remain open until the relevant evidence and approvals exist.
