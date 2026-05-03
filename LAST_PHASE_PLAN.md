# Last Phase Plan

Purpose:
- close out the large `domainRag` study in a clean, trustworthy repo-local state
- remove transitional clutter from `analytics`
- prepare the repo for smaller repeatable study runs
- define a strict local-only operating mode for confidential corpus work

## Current State

Completed:
- Claude review complete: `1200/1200`
- Codex review complete: `1200/1200`
- Claude lane metadata repaired in:
  - `analytics\claude_aigenticHumanReview\claude_review_workdir\claude_review_decisions.json`
- workbook and review-analysis outputs regenerate cleanly from repaired lane data
- active review charts all render into one folder:
  - `analytics\merged\review_analysis\charts`
- final review chart surface pruned down to the core lane and shared comparison charts
- large-run transient storage is repo-local when active:
  - `analytics\runs`
- actual archived study sources remain:
  - `analytics\example1_local-local`
  - `analytics\example1_haikuPermutations`
  - `analytics\example1_gptBaseline`

Resolved tonight:
- Claude raw review file was missing metadata from row `351` onward; repaired by key from `claude_review_input.json`
- GPT rows in both review lanes now correctly carry:
  - `reviewer_decision = None`
  - `agrees_with_reviewer = None`
- reviewer-baseline charts now state that they are non-GPT / reviewer-baseline-only views
- `run_batches.py` archive routing was corrected back to:
  - `analytics\example1_local-local`
  - `analytics\example1_haikuPermutations`

## Active Folder Semantics

Keep treating these as active:
- `analytics\example1_local-local`
  - archived source runs for `local/local`
- `analytics\example1_haikuPermutations`
  - archived source runs for `local/haiku`, `haiku/local`, `haiku/haiku`
- `analytics\example1_gptBaseline`
  - GPT source workbook inputs
- `analytics\merged`
  - derived workbook and merged outputs
- `analytics\merged\review_analysis`
  - derived review-analysis exports
- `analytics\merged\review_analysis\charts`
  - active final chart surface
- `analytics\claude_aigenticHumanReview`
  - Claude lane workflow surface
- `analytics\codex_aigenticHumanReview`
  - Codex lane workflow surface

Treat this as transient only:
- `analytics\runs`
  - staging/work-in-progress scratch during unattended batch execution
  - should be empty or absent between finished studies

## Remaining Work

### 1. Analytics Root Cleanup

Goal:
- make `analytics` readable without knowing the project history

Tasks:
- keep only active code, active lane folders, active archive roots, and active merged outputs at top level
- move or archive noisy historical study-control artifacts if they are no longer part of the canonical path
- keep `analytics\runs` transient instead of letting it accumulate old study duplicates

### 2. Small Study Mode

Goal:
- support future smaller `50-100` item studies without polluting the large exploratory study surfaces

Target shape:
- one study root per run
- clear split between:
  - inputs
  - generation outputs
  - review outputs
  - lane workdirs

Preferred direction:
- `analytics\studies\<study_id>\...`

### 3. Operator Flow Simplification

Goal:
- reduce the real operator path to a short reproducible sequence

Tasks:
- define canonical commands for:
  - generate/archive
  - dual review
  - finalization
- decide which wrappers remain canonical and which are compatibility shims

### 4. No External Endpoints Mode

Goal:
- support a study mode where a corpus never leaves local disk or local model/runtime boundaries

Requirements:
- corpus inputs must resolve only to local folders
- no hosted API, browser workflow, or external endpoint may see corpus content
- corpus-bearing temp files should route through `C:\Users\kadek\secrets` wherever practical
- once transferred into secrets-backed local handling, any git-space copies should be removed promptly
- corpus-bearing paths must be protected by `.gitignore` before any run begins, even if the operator believes the files are temporary

Tasks:
- identify every step that can currently send corpus text outside local boundaries
- define one canonical config/profile for local-only study runs
- separate safe tracked analytics artifacts from untracked corpus-bearing artifacts
- make cleanup/transfer steps explicit so repo copies do not linger

## Immediate Next Recommendation

Next session should start with:
1. simplify top-level analytics surfaces
2. scaffold the first clean small-study path
3. define the first no-external-endpoints study profile
4. separate historical study-control folders from canonical active roots

## Done Condition

The repo should end up with:
- repo-local workflow state
- repo-local archived study sources
- one trustworthy merged review-analysis surface
- transient staging that does not linger after studies
- a small-study path that feels lighter than this large exploratory run
- a documented local-only mode for confidential corpora
