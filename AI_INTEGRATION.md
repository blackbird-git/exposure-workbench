# Local AI diagnostic analysis

This milestone adds read-only Ollama analysis to the existing exposure-workbench project. Keep your existing `ai/sanitize.py` and `ai/__init__.py` unchanged.

## Requirements

- Python 3.10+
- Local Ollama server running on `127.0.0.1:11434`
- `ollama pull qwen3:4b`

## Usage

```bash
python3 ai/analyze.py report.txt
python3 ai/analyze.py report.txt --ai
python3 ai/analyze.py report.txt --ai --json
python3 -m unittest discover -s tests -v
```

The AI path validates the three report sections, sanitizes report content with the existing sanitizer, and sends it to a loopback-only Ollama API. No shell commands are executed by the AI integration. The output is advisory, not a security audit. Sanitization is best-effort and may leave secrets, public IP addresses, or identifiers intact. Do not process confidential production reports without review.

The output includes `summary` and up to five `findings` with title, severity, confidence, evidence, interpretation, and read-only verification steps. Local LLM output may be incorrect or overconfident; verify findings independently.

## Suggested Git checkpoint

```bash
git add ai/analyze.py ai/ollama_client.py tests/test_ai.py README.md
git commit -m "Add read-only local Ollama diagnostic analysis"
git push
```
