# Graph Report - C:\Users\kadek\source\repos\domainRag\_orchestration\context-map\graphify  (2026-07-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 619 nodes · 1313 edges · 34 communities (30 shown, 4 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 212 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dbac5fe1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 23
- Community 24
- Community 25
- Community 27
- Community 28

## God Nodes (most connected - your core abstractions)
1. `style_ax()` - 42 edges
2. `generate_from_db()` - 30 edges
3. `_run_custom_batch()` - 26 edges
4. `main()` - 22 edges
5. `run_merged_mode()` - 22 edges
6. `generate_baseline()` - 19 edges
7. `run_batch_mode()` - 19 edges
8. `call_llm()` - 18 edges
9. `run_pipeline()` - 18 edges
10. `build_exports()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `_call_configured_review()` --calls--> `call_llm()`  [INFERRED]
  analytics/claude_aigenticHumanReview/aigenticHumanReview.py → _rag_testGen/llm_client.py
- `main()` --calls--> `load_config_from_env()`  [INFERRED]
  _rag_testGen/cli.py → _rag_testGen/config.py
- `main()` --calls--> `ingest_domain()`  [INFERRED]
  _rag_testGen/cli.py → _rag_testGen/ingest.py
- `main()` --calls--> `generate_baseline()`  [INFERRED]
  _rag_testGen/cli.py → _rag_testGen/pipeline.py
- `main()` --calls--> `generate_from_db()`  [INFERRED]
  _rag_testGen/cli.py → _rag_testGen/pipeline.py

## Import Cycles
- None detected.

## Communities (34 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (83): _analytics_root(), _analytics_script(), _api_model_family(), _BatchBack, _BatchExit, _build_batch_plan_interactive(), _build_batch_row_interactive(), _build_env() (+75 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (60): accept_vs_match(), agreement_bar(), decision_heatmap(), decisions_bar(), flag_bar(), qc_flags_bar(), radar_by_condition(), reject_breakdown() (+52 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (51): _chunk_id(), _extract_api_pdf(), _extract_api_text(), extract_knowledge_chunks(), _extract_local_pdf(), _extract_local_text(), ingest_domain(), _is_pdf() (+43 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (45): main(), domainRag Run Quality + Cost Dashboard ====================================== Pe, boxplot(), chart_accept_vs_match(), chart_api_cost(), chart_decisions(), chart_heatmap(), chart_mean_quality() (+37 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (43): append_batch(), _call_anthropic_review(), _call_configured_review(), _config_env_path(), _config_value(), _enrich_decisions_with_input(), export_items(), _extract_json_object() (+35 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (34): chunks_rowcount(), clear_chunks(), clear_corpus(), _column_exists(), DBConfig, ensure_schema(), get_db_snapshot_per_doc(), get_db_snapshot_summary() (+26 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (31): _answer_key_rows(), _boolish(), build_exports(), _build_long_rows(), _build_wide_rows(), _condition_difficulty_rows(), _correct_key_anomaly_rows(), _difficulty_match_pass() (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (24): _hdr(), main(), finalize_study.py — Finalize a domainRag comparative study.  Orchestrates the en, Import review_workflow at call time so sys.path manipulation is localised., _review_progress(), _run(), bootstrap(), main() (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (26): _build_chunk_preview_rows(), _build_quality_meta(), _cap_text(), _checkpoint_items(), _checkpoint_review(), generate_baseline(), generate_from_db(), _infer_embedding_dim_from_db() (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (21): _is_spoken_math_transcript(), load_document(), load_docx(), load_mp4(), load_pdf(), load_pptx(), load_text_file(), preprocess_text() (+13 more)

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (17): ArgumentParser, build_parser(), _default_run_id(), main(), IngestConfig, LoadedDoc, A loaded document with stable identity for traceability and idempotent upserts., BaselineConfig (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (18): _batch_dest(), _capture_docker_logs(), _capture_lmstudio_logs(), load_config(), main(), _masked_input(), post_all(), post_batch() (+10 more)

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (10): _default_out_dir(), _env(), _env_bool(), _env_int(), load_config_from_env(), Path, Loads all configuration from environment variables., Fully-resolved configuration loaded from environment variables. (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (15): Runs reviewer LLM and returns (rev_clean, elapsed_seconds)., _run_reviewer(), clean_generator_text(), enforce_hygiene_on_review(), extract_first_json_obj(), hard_trim_after_difficulty(), normalize_decision(), Any (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.21
Nodes (14): _batch_root(), find_run_files(), main(), merge_gpt_baselines(), merge_quality_metrics(), merge_sheet(), Path, merge_runs.py — Merge all batch XLSX runs into a single master file.  Scans an (+6 more)

### Community 15 - "Community 15"
Cohesion: 0.29
Nodes (12): Acquire-SupervisorLock(), ConvertTo-HashtableSafe(), Get-DecisionsMeta(), Get-InboxCount(), Get-JsonCount(), Get-JsonObject(), Invoke-SupervisorTick(), New-RuntimeState() (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.42
Nodes (8): create_study(), _local_only_template(), main(), Path, _slugify(), _study_gitignore(), _study_readme(), _write_if_missing()

### Community 17 - "Community 17"
Cohesion: 0.28
Nodes (8): Chunk, chunk_text(), _normalize_ws(), note: A chunk is a contiguous segment of text used as the unit of embedding and, note: Normalizes whitespace for more stable overlap behavior and downstream hash, note: Creates boundary-aware overlap by taking up to max_sentences from the end,, note: Chunks text by paragraph-like blocks, then packs into roughly chunk_chars, _tail_overlap()

### Community 18 - "Community 18"
Cohesion: 0.46
Nodes (7): fmt_time(), load_model(), main(), print_progress(), Path, transcribe_corpus.py — Batch transcriber for domainRag corpus ingestion.  Transc, transcribe_file()

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (5): decisions_json_path(), input_json_path(), Path, review_dir(), review_output_root()

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (5): decisions_json_path(), input_json_path(), Path, review_dir(), review_output_root()

### Community 21 - "Community 21"
Cohesion: 0.47
Nodes (5): embed_texts(), EmbedConfig, note: Configuration for LM Studio OpenAI-compatible embeddings endpoint., note: Calls LM Studio /v1/embeddings and returns embeddings in the same order as, _infer_embedding_dim()

### Community 23 - "Community 23"
Cohesion: 0.60
Nodes (4): main(), Path, _read_rows(), _style()

## Knowledge Gaps
- **1 isolated node(s):** `_run_testGen.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `call_llm()` connect `Community 2` to `Community 8`, `Community 4`, `Community 13`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `_call_configured_review()` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `ingest_domain()` connect `Community 2` to `Community 0`, `Community 5`, `Community 9`, `Community 10`, `Community 21`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `style_ax()` (e.g. with `accept_vs_match()` and `agreement_bar()`) actually correct?**
  _`style_ax()` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `generate_from_db()` (e.g. with `main()` and `chunks_rowcount()`) actually correct?**
  _`generate_from_db()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `assess_run.py — Programmatic quality check for a completed run XLSX.  Usage: p`, `note: A chunk is a contiguous segment of text used as the unit of embedding and`, `note: Normalizes whitespace for more stable overlap behavior and downstream hash` to the rest of the system?**
  _108 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.060527825588066554 - nodes in this community are weakly interconnected._