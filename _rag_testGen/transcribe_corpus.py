"""
transcribe_corpus.py — Batch transcriber for domainRag corpus ingestion.

Transcribes all MP4 files in an input folder using local Whisper (faster-whisper).
No external API calls are made at any stage.

Usage:
    python transcribe_corpus.py --input-dir "C:/path/to/mp4s"
    python transcribe_corpus.py --input-dir "C:/path/to/mp4s" --output-dir "C:/path/to/txts"

If --output-dir is omitted, .txt files are written alongside the source MP4s.
Already-transcribed files (existing .txt) are skipped unless --force is passed.
"""

import argparse
import os
import sys
from pathlib import Path


def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"


def print_progress(current, total):
    pct = min(current / total, 1.0) if total > 0 else 0
    bar_len = 40
    filled = int(bar_len * pct)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r  [{bar}] {fmt_time(current)} / {fmt_time(total)}  ({pct*100:.1f}%)",
          end="", flush=True)


def load_model():
    from faster_whisper import WhisperModel
    try:
        print("Trying CUDA...")
        model = WhisperModel("small", device="cuda", compute_type="float16")
        print("Using GPU.\n")
    except Exception as e:
        print(f"CUDA unavailable ({e}), falling back to CPU.\n")
        model = WhisperModel("small", device="cpu", compute_type="int8")
    return model


def transcribe_file(model, mp4_path: Path, out_path: Path) -> None:
    print(f"Transcribing: {mp4_path.name}")
    print(f"Output:       {out_path}")

    segments, info = model.transcribe(str(mp4_path), language="en")
    duration = info.duration

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for segment in segments:
            line = f"[{fmt_time(segment.start)}] {segment.text.strip()}\n"
            f.write(line)
            f.flush()
            print_progress(segment.end, duration)

    print(f"\n  Done: {out_path.name}\n")


def main():
    parser = argparse.ArgumentParser(description="Batch MP4 transcriber for domainRag corpus")
    parser.add_argument("--input-dir",  required=True, help="Folder containing .mp4 files")
    parser.add_argument("--output-dir", default=None,  help="Where to write .txt files (default: same as input)")
    parser.add_argument("--force",      action="store_true", help="Re-transcribe even if .txt already exists")
    args = parser.parse_args()

    input_dir  = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir

    if not input_dir.is_dir():
        print(f"Error: --input-dir '{input_dir}' not found.")
        sys.exit(1)

    mp4_files = sorted(input_dir.glob("*.mp4"))
    if not mp4_files:
        print(f"No .mp4 files found in '{input_dir}'.")
        sys.exit(0)

    print(f"\nFound {len(mp4_files)} MP4 file(s) in: {input_dir}")
    print(f"Output dir: {output_dir}\n")

    to_process = []
    for mp4 in mp4_files:
        out = output_dir / (mp4.stem + ".txt")
        if out.exists() and not args.force:
            print(f"  [skip] {mp4.name}  (transcript exists, use --force to redo)")
        else:
            to_process.append((mp4, out))

    if not to_process:
        print("\nAll files already transcribed.")
        return

    print(f"\nTo transcribe: {len(to_process)} file(s)\n")
    model = load_model()

    for i, (mp4, out) in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] ", end="")
        transcribe_file(model, mp4, out)

    print(f"Batch complete. {len(to_process)} transcript(s) written to: {output_dir}")


if __name__ == "__main__":
    main()
