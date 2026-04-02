# domainRag: Methodology Evaluation

## Project Goal

domainRag is a systematic study tool for evaluating whether Retrieval-Augmented Generation (RAG) improves the quality of multiple-choice assessment items generated from domain-specific source documents. It compares RAG-enabled generation against baseline generation from a frontier model to determine if grounding outputs in retrieved context produces measurably comparable items.

---

## Core Methodology

### 1. Document Ingestion

The system ingests source documents (PDF, PPTX, DOCX, TXT) and extracts "knowledge chunks" using an LLM. These chunks are embedded via LM Studio (local) and stored in PostgreSQL with pgvector for similarity search.

**Methodological assumption:** Chunk quality is the first gate. If the ingestion stage produces poor chunks, downstream generation has no hope of quality. Chunks are held constant and for best results handled by a frontier model - API costing was ~$0.5 and time to chunk was neglible.

**Critical question not fully addressed:** How is "chunk quality" measured before generation? The system retrieves chunks during generation, but there's no pre-flight validation that chunks adequately represent the source document's conceptual landscape.

### 2. Retrieval-Augmented Generation

For each item to generate:
1. The system retrieves top-K chunks from pgvector based on similarity to the item prompt
2. Retrieved chunks are packed into the LLM context window 
3. The generator LLM produces a multiple-choice item

**The comparison framework:** The system generates the same item prompts under two conditions:
- local or api haiku
	- haiku costs are neglible as compared to frontier model at fractions of a cent for complete study generation of 400 questions each from reviewer AND generator agent roles
**RAG condition:** chunks are included in context

This is the right experimental design. However, the prompt used for generation is identical between conditions—only the retrieved context differs. This controls for prompt wording as a confound.

### 3. Item Review (Second Pass)

Generated items pass through a reviewer LLM that evaluates:
- Stem clarity
- Distractor plausibility
- Correct answer correctness
- Difficulty alignment with target (easy/medium/hard)
- Reason codes for failures

**Methodological strength:** The two-pass generation+review is sound. It mirrors real-world item writing where an author produces a draft and an editor revises.

**Weakness:** The reviewer sees the same retrieved chunks as the generator. If the chunks are biased or incomplete, the reviewer may approve poor items that happen to be consistent with bad source material. There's no "independent" reviewer who evaluates the item against the *source document directly*—only against the chunks.

### 4. Difficulty Targeting

The system allows targeting easy/medium/hard difficulty. This is implemented via prompt engineering (instructions to the generator).

**Critical gap:** There's no validated difficulty metric. The system *assumes* difficulty based on target labels, but doesn't independently verify that easy items are actually easier than hard items for the intended audience. The "difficulty_match" field in review output is self-reported correctness of the generator's attempt, not an empirical measure.

### 5. Condition Permutations

The system supports mixing local and API providers across stages:
- Ingest (local or API)
- Generate (local or API)
- Review (local or API)

This creates a combinatorial design:
- local-local-local
- local-local-api
- api-local-api
- etc.

**Value:** This allows isolating the effect of each stage's provider. Does RAG help more when using API generation? Does local review align with API review?

**Weakness:** Each permutation multiplies runs. At 50 items × 3 difficulties × N conditions, studies become expensive in compute and time. The system doesn't have formal power analysis or sample size justification.

---

## Evaluation Process

### 1. Automated Metrics

The system outputs XLSX workbooks with:
- Traceability (item → chunks → source)
- Quality metrics from reviewer
- Decision codes

### 2. Human/Agent Review

After automated generation, items are exported for human or agent review. Reviewers make binary accept/revise decisions and provide reason codes.

**Current status (from session 37):** Two parallel review lanes exist:
- Claude review lane
- Codex review lane

These operate independently with separate decision stores. The plan is to reconcile them later.

**Critical risk:** Two independent reviewers with different LLMs may produce conflicting accept/revise decisions. There's no documented protocol for resolving conflicts. The system defers this to "downstream consumption" without a concrete decision rule.

### 3. Study Aggregation

The system merges runs into master workbooks and renders charts comparing conditions.

**Weakness:** The analytics code (`analyticsVizs.py`) has historically accumulated study-specific logic. The DEVOPS notes acknowledge this as a known weakness. Charts may not generalize across different corpus types or item counts.

---

## Strengths

1. **Controlled comparison design.** The RAG vs baseline split is the right experimental question, properly controlled.

2. **Provider routing flexibility.** The ability to swap local vs API at each stage enables causal claims about what each component contributes.

3. **Checkpointing.** The system can resume from chunk review, item review, or reviewer flag stages—important for long batch runs.

4. **Audit trail.** Each item tracks back to specific chunks and source documents. This is essential for defensible assessment.

5. **Local-first embeddings.** All embeddings stay local via LM Studio, addressing privacy concerns for sensitive corpora.

---

## Weaknesses and Criticisms

### 1. No Ground Truth for Quality

The system generates items and reviews them, but there's no external criterion for "good." The reviewer LLM's opinion is the only metric. Without human subject matter experts validating items, there's no guarantee the system produces usable assessment content.

### 2. Retrieval Quality is Opaque

The system retrieves chunks by vector similarity but doesn't evaluate:
- Whether retrieved chunks actually contain the knowledge needed
- Whether irrelevant chunks introduce noise
- Whether the TOP_K setting is optimal for the given corpus

A retrieval could be "successful" (found chunks) but "wrong" (found irrelevant chunks). The generation may still produce a plausible-sounding item that isn't actually grounded in correct source material.

### 3. Reviewer Alignment is Unvalidated

The reviewer evaluates items *given the same chunks the generator used*. If retrieval failed, the reviewer has no independent source to catch it. The system doesn't measure **reviewer-source alignment**—whether the reviewer would make the same decision if it saw the full source document instead of just retrieved chunks.

### 4. Difficulty is Label, Not Measure

"Easy/medium/hard" targets are prompt instructions, not validated constructs. There's no evidence that:
- Easy items actually test simpler concepts
- Hard items actually require multi-step reasoning
- The difficulty spread is meaningful

### 5. No Inter-Rater Reliability

Multiple review lanes (Claude, Codex) produce independent decisions. The system hasn't established:
- What agreement rate is expected
- How to weight disagreeing decisions
- Whether lane-specific biases exist (e.g., Claude more lenient on stem clarity)

### 6. Combinatorial Explosion

With 3 difficulty levels × N provider permutations × variable TOP_K × variable chunk strategies, the parameter space is huge. The system doesn't guide users toward which comparisons are *worth running* vs. redundant.

### 7. Hardware Dependency

The DEVOPS notes acknowledge GTX 1650 is weak for local PDF vision. This creates a systematic bias:
- Local-only runs on weak hardware may underperform
- API runs on better infrastructure may have unfair advantage
- The local/API comparison is confounded by compute quality

### 8. No Statistical Rigor

The system produces item counts and pass rates but doesn't compute:
- Confidence intervals
- Effect sizes for RAG vs baseline
- Significance tests

A study could show "RAG had 60% acceptance vs baseline 55%" but not tell you if that's meaningful or noise.

---

## Questions for Evaluation

An agent evaluating this project should ask:

1. **What is the unit of analysis?** Individual items? Runs? Full studies? The system produces all three but treats them inconsistently.

2. **What constitutes a "successful" study?** Is the goal to prove RAG works? To find conditions where it works best? To produce acceptable items at scale?

3. **Who is the audience for generated items?** If human learners, have human experts validated any outputs?

4. **What's the retry policy?** When generation fails or review rejects, does the system retry automatically? With same or different prompts?

5. **How stable are results?** If you run the same configuration twice, how much do accept rates vary? The system doesn't document reproducibility.

6. **What's the throughput?** How long to generate 50 items × 3 difficulties under one condition? This matters for planning studies.

7. **What happens to rejected items?** Are they discarded? Fed back as feedback? The current flow appears to be: generate → review → if REVISE, mark as revision_needed but no auto-regeneration.

---

## Summary

domainRag implements a sound comparative methodology for evaluating RAG in assessment item generation. Its strengths are controlled experimental design, flexible provider routing, and auditability. Its weaknesses are reliance on LLM self-evaluation rather than ground truth, unvalidated difficulty constructs, no statistical rigor in result interpretation, and unresolved inter-rater reliability for multi-lane reviews.

The project is useful as a **generation pipeline** but incomplete as a **validation system**. It answers "can we generate items this way?" but not "are these items any good for their intended purpose?"

---

## Files for Reference

- Main pipeline: `_rag_testGen/`
- Analytics: `analytics/`
- Human review: `analytics/*_aigenticHumanReview/`
- Config: `C:\Users\kadek\secrets\domainRag\config.env`
