# dspyteach – DSPy File Teaching Analyzer

---

[![PyPI](https://img.shields.io/pypi/v/dspyteach.svg?include_prereleases&cacheSeconds=60&t=1)](https://pypi.org/project/dspyteach/)
[![Downloads](https://img.shields.io/pypi/dm/dspyteach.svg?cacheSeconds=300)](https://pypi.org/project/dspyteach/)
[![Python](https://img.shields.io/pypi/pyversions/dspyteach.svg?cacheSeconds=300)](https://pypi.org/project/dspyteach/)
[![License](https://img.shields.io/pypi/l/dspyteach.svg?cacheSeconds=300)](LICENSE)
[![TestPyPI](https://img.shields.io/badge/TestPyPI-dspyteach-informational?cacheSeconds=300)](https://test.pypi.org/project/dspyteach/)
[![CI](https://github.com/AcidicSoil/dspy-file/actions/workflows/release.yml/badge.svg)](…)

---

## DSPy-powered CLI that analyzes source files (one or many) and produces teaching briefs

**Each run captures:**

- an overview of the file and its major sections
- key teaching points, workflows, and pitfalls highlighted in the material
- a polished markdown brief suitable for sharing with learners

The implementation mirrors the multi-file tutorial (`tutorials/multi-llmtxt_generator`) but focuses on per-file inference. The program is split into:

- `dspy_file/signatures.py` – DSPy signatures that define inputs/outputs for each step
- `dspy_file/file_analyzer.py` – the main DSPy module that orchestrates overview, teaching extraction, and report composition. It now wraps the final report stage with `dspy.Refine`, pushing for 450–650+ word briefs.
- `dspy_file/file_helpers.py` – utilities for loading files and rendering the markdown brief
- `dspy_file/analyze_file_cli.py` – command line entry point that configures the local model and prints results. It can walk directories, apply glob filters, and batch-generate briefs.

---

## Requirements

- Python 3.10-3.12+
- DSPy installed in the environment
- Ollama running locally with the model `hf.co/Mungert/osmosis-mcp-4b-GGUF:Q4_K_M` available
- (Optional) `.env` file for any additional DSPy configuration; `dotenv` is loaded automatically

Install the Python dependencies if you have not already:
**you dont need all of these commands to correctly install**

### I added multiple install commands and will cleanup later

```bash
uv init

uv venv -p 3.12
source .venv/bin/activate
```

```bash
uv pip install dspy python-dotenv
```

```bash
uv sync
```

#### will add options to use your preferred model of choice later

```bash
ollama pull hf.co/Mungert/osmosis-mcp-4b-GGUF:Q4_K_M
```

```bash
uv pip install dspyteach
```

## Usage

Run the CLI to extract a teaching brief from a single file:

```bash
dspyteach path/to/your_file
```

You can also point the CLI at a directory. The tool will recurse by default:

```bash
dspyteach path/to/project --glob "**/*.py" --glob "**/*.md"
```

Use `--non-recursive` to stay in the top-level directory, add `--glob` repeatedly to narrow the target set, and pass `--raw` to print the raw DSPy prediction object instead of the formatted report.

Need to double-check files before the model runs? Add `--confirm-each` (alias `--interactive`) to prompt before every file, accepting with Enter or skipping with `n`.

To omit specific subdirectories entirely, pass one or more `--exclude-dirs` options. Each value can list comma-separated relative paths (for example `--exclude-dirs "build/,venv/" --exclude-dirs data/raw`). The analyzer ignores any files whose path begins with the provided prefixes.

Prefer short flags? The common options include `-r` (`--raw`), `-m` (`--mode`), `-nr` (`--non-recursive`), `-g` (`--glob`), `-i` (`--confirm-each`), `-ed` (`--exclude-dirs`), and `-o` (`--output-dir`). Mix and match them as needed.

Want to scaffold refactor prompt templates instead of teaching briefs? Switch the mode:

```bash
dspyteach path/to/project --mode refactor --glob "**/*.md"
```

The CLI reuses the same file resolution pipeline but feeds each document through the bundled `dspy-file_refactor-prompt_template.md` instructions (packaged under `dspy_file/prompts/`), saving `.refactor.md` files alongside the teaching reports. Teaching briefs remain the default (`--mode teach`), so existing workflows continue to work unchanged.

When multiple templates live in `dspy_file/prompts/`, the refactor mode surfaces a picker so you can choose which one to use. You can also point at a specific template explicitly with `-p/--prompt`, passing either a bundled name (`-p refactor_prompt_template`) or an absolute path to your own Markdown prompt.

Each run only executes the analyzer for the chosen mode. When you pass `--mode refactor` the teaching inference pipeline stays idle, and you can alias the command (for example `alias dspyrefactor='dspyteach --mode refactor'`) if you prefer refactor templates to be the default in your shell.

To change where reports land, supply `--output-dir /path/to/reports`. When omitted the CLI writes to `dspy_file/data/` next to the module. Every run prints the active model name and the resolved output directory before analysis begins so you can confirm the environment at a glance. For backwards compatibility the installer also registers `dspy-file-teaching` as an alias.

Each analyzed file is saved under the chosen directory with a slugged name (e.g. `src__main.teaching.md` or `src__main.refactor.md`). If a file already exists, the CLI appends a numeric suffix to avoid overwriting previous runs.

The generated brief is markdown that mirrors the source material:

- Overview paragraphs for quick orientation
- Section-by-section bullets capturing the narrative
- Key concepts, workflows, pitfalls, and references learners should review
- A `dspy.Refine` wrapper keeps retrying until the report clears a length reward (defaults scale to ~50% of the source word count, with min/max clamps), so the content tends to be substantially longer than a single LM call.
- If a model cannot honour DSPy's structured-output schema, the CLI prints a `Structured output fallback` notice and heuristically parses the textual response so you still get usable bullets.

Behind the scenes the CLI:

1. Loads environment variables via `python-dotenv`.
2. Configures DSPy with the same local Ollama model used in the tutorial.
3. Resolves all requested files, reads contents, runs the DSPy `FileTeachingAnalyzer` module, and prints a human-friendly report for each.
4. Persists each report to the configured output directory so results are easy to revisit.
5. Attempts to stop the Ollama model when finished, mirroring the fail-safe logic from the tutorial.

## Extending

- Adjust the `TeachingReport` signature or add new chains in `dspy_file/file_analyzer.py` to capture additional teaching metadata.
- Customize the render logic in `dspy_file.file_helpers.render_prediction` if you want richer CLI output or structured JSON.
- Tune `TeachingConfig` inside `file_analyzer.py` to raise `max_tokens`, adjust the `Refine` word-count reward, or add extra LM kwargs.
- Add more signatures and module stages to capture additional metadata (e.g., security checks) and wire them into `FileAnalyzer`.

## Packaging & Publishing

The repository is configured for standard Python packaging via `pyproject.toml` and the `setuptools` backend. A typical release flow with [`uv`](https://docs.astral.sh/uv/guides/package/) looks like:

```bash
# (optional) bump the version before you publish
uv version --bump patch

# build the source distribution and wheel; artifacts land in dist/
uv build --no-sources

# publish to PyPI (or TestPyPI) once you have an API token
UV_PUBLISH_TOKEN=... uv publish
```

If you want to stage a release first, point `uv publish --index testpypi` at the alternate index configured in `pyproject.toml`.

To install the package from a freshly built artifact:

```bash
pip install dist/dspyteach-0.1.1-py3-none-any.whl
```

Once the project is on PyPI, users can install it directly:

```bash
pip install dspyteach
```

After installation, the `dspyteach` console script (plus the legacy `dspy-file-teaching` alias) is available in any environment so you can run analyses outside of this repository or integrate the tool into CI jobs.

### CI Publishing

GitHub Actions users can trigger `.github/workflows/publish-testpypi.yml` to build and push the current checkout to TestPyPI. The workflow:

- Checks out the repository (ensuring `pyproject.toml` is present as required by uv publish).
- Installs uv with Python 3.12.
 - Runs `uv build --no-sources` from the repository root.
- Publishes with `uv publish --index testpypi dist/*` using the `TEST_PYPI_TOKEN` secret.

See the [uv publishing guide](https://docs.astral.sh/uv/guides/package/#publishing-your-package) for the official note about requiring a checkout when using `--index`.

## Troubleshooting

- If the program cannot connect to Ollama, verify that the server is running on `http://localhost:11434` and the requested model has been pulled.
- When you see `ollama command not found`, ensure the `ollama` binary is on your `PATH`.
- For encoding errors, the helper already falls back to `latin-1`, but you can add more fallbacks in `file_helpers.read_file_content` if needed.
