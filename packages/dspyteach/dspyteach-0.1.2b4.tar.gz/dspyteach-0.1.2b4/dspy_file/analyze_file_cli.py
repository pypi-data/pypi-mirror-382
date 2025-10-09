# analyze_file_cli.py - command line entry point for DSPy file analyzer
from __future__ import annotations

import argparse
import sys
import subprocess
from pathlib import Path

import dspy
from dotenv import load_dotenv

from .file_analyzer import FileTeachingAnalyzer
from .file_helpers import collect_source_paths, read_file_content, render_prediction

MODEL_NAME = "hf.co/unsloth/Qwen3-4B-Thinking-2507-GGUF:Q4_K_M"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "data"


def configure_local_model() -> None:
    """Configure DSPy to talk to the local Ollama model."""

    lm = dspy.LM(
        f"ollama_chat/{MODEL_NAME}",
        api_base=OLLAMA_BASE_URL,
        api_key="",
        streaming=False,
        cache=False,
    )
    dspy.configure(lm=lm)
    print(f"Configured DSPy LM: {MODEL_NAME}")


def stop_ollama_model(model_name: str) -> None:
    """Stop the Ollama model to free server resources."""

    try:
        subprocess.run(
            ["ollama", "stop", model_name],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - warn only
        print(f"Warning: Failed to stop model {model_name}: {exc}")
    except FileNotFoundError:
        print("Warning: ollama command not found while attempting to stop the model.")


def _write_output(
    source_path: Path,
    content: str,
    *,
    root: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Persist analyzer output under the data directory with de-duplicated file names."""

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        relative_path = source_path.relative_to(root) if root else Path(source_path.name)
    except ValueError:
        relative_path = Path(source_path.name)

    slug_parts = [part.replace("/", "_") for part in relative_path.with_suffix("").parts]
    slug = "__".join(slug_parts) if slug_parts else source_path.stem
    base_name = f"{slug}.teaching.md"
    output_path = output_dir / base_name

    counter = 1
    while output_path.exists():
        output_path = output_dir / f"{slug}.teaching-{counter}.md"
        counter += 1

    if not content.endswith("\n"):
        content = content + "\n"
    output_path.write_text(content, encoding="utf-8")
    return output_path



def _confirm_analyze(path: Path) -> bool:
    """Prompt the user for confirmation before analyzing a file."""

    prompt = f"Analyze {path}? [Y/n]: "
    while True:
        try:
            response = input(prompt)
        except EOFError:
            print("No input received; skipping.")
            return False

        normalized = response.strip().lower()
        if normalized in {"", "y", "yes"}:
            return True
        if normalized in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a single file using DSPy signatures and modules",
    )
    parser.add_argument("path", help="Path to the file to analyze")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw DSPy prediction repr instead of formatted text",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="When path is a directory, only analyze files in the top-level directory",
    )
    parser.add_argument(
        "--glob",
        action="append",
        dest="include_globs",
        default=None,
        help=(
            "Optional glob pattern(s) applied relative to the directory. Repeat to combine."
        ),
    )
    parser.add_argument(
        "--confirm-each",
        "--interactive",
        action="store_true",
        dest="confirm_each",
        help="Prompt for confirmation before analyzing each file.",
    )
    parser.add_argument(
        "--exclude-dirs",
        action="append",
        dest="exclude_dirs",
        default=None,
        help=(
            "Comma-separated relative directory paths to skip entirely when scanning."
        ),
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=None,
        help=(
            "Directory to write teaching reports into (default: module data directory)."
        ),
    )
    return parser


def analyze_path(
    path: str,
    *,
    raw: bool,
    recursive: bool,
    include_globs: list[str] | None,
    confirm_each: bool,
    exclude_dirs: list[str] | None,
    output_dir: Path,
) -> int:
    """Run the DSPy pipeline and render results to stdout for one or many files."""

    resolved = Path(path).expanduser().resolve()
    targets = collect_source_paths(
        path,
        recursive=recursive,
        include_globs=include_globs,
        exclude_dirs=exclude_dirs,
    )

    if not targets:
        print(f"No files found under {resolved}")
        return 0

    analyzer = FileTeachingAnalyzer()
    root: Path | None = resolved if resolved.is_dir() else None

    exit_code = 0
    for target in targets:
        if confirm_each and not _confirm_analyze(target):
            print(f"Skipping {target} at user request.")
            continue

        try:
            content = read_file_content(target)
        except (FileNotFoundError, UnicodeDecodeError) as exc:
            print(f"Skipping {target}: {exc}")
            exit_code = 1
            continue

        print(f"\n=== Analyzing {target} ===")
        prediction = analyzer(file_path=str(target), file_content=content)

        if raw:
            output_text = repr(prediction)
            print(output_text)
        else:
            output_text = render_prediction(prediction)
            print(output_text, end="")

        output_path = _write_output(
            target,
            output_text,
            root=root,
            output_dir=output_dir,
        )
        print(f"Saved report to {output_path}")

    return exit_code


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    configure_local_model()

    parser = build_parser()
    args = parser.parse_args(argv)

    exit_code = 0
    try:
        output_dir = (
            Path(args.output_dir).expanduser().resolve()
            if args.output_dir
            else DEFAULT_OUTPUT_DIR
        )
        print(f"Writing reports to {output_dir}")
        exclude_dirs = None
        if args.exclude_dirs:
            parsed: list[str] = []
            for entry in args.exclude_dirs:
                parsed.extend(
                    segment.strip()
                    for segment in entry.split(",")
                    if segment.strip()
                )
            exclude_dirs = parsed or None
        exit_code = analyze_path(
            args.path,
            raw=args.raw,
            recursive=not args.non_recursive,
            include_globs=args.include_globs,
            confirm_each=args.confirm_each,
            exclude_dirs=exclude_dirs,
            output_dir=output_dir,
        )
    except (FileNotFoundError, IsADirectoryError) as exc:
        parser.print_usage(sys.stderr)
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        exit_code = 2
    except KeyboardInterrupt:
        exit_code = 1
    finally:
        stop_ollama_model(MODEL_NAME)

    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
