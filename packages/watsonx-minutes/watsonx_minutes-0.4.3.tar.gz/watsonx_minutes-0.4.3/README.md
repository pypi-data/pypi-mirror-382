# watsonx_minutes

Summarize a Minutes of Meeting file with **IBM watsonx.ai** and emit standardized TODOs.
Includes a modern progress UI (Rich) and **multi-format input**.

## Supported inputs
- Plain text: `.txt`, `.md`, `.markdown`, `.log`, `.json`, `.yaml` (treated as text)
- Rich Text Format: `.rtf`
- HTML: `.html`, `.htm` (text extracted via BeautifulSoup)
- PDF: `.pdf` (text extracted via pypdf)
- Word: `.docx` (text extracted via python-docx)
- PowerPoint: `.pptx` (text extracted via python-pptx)
- Others: best-effort UTF‑8 decode with errors ignored

## Install

```bash
pip install -U watsonx-minutes
# or for local dev
pip install -e .
```

## Credentials
Provide via flags **or** environment variables:

- `WATSONX_APIKEY` – your IBM Cloud IAM API key
- `WATSONX_URL` – e.g. `https://us-south.ml.cloud.ibm.com` (your region)
- `WATSONX_PROJECT_ID` – your project id

## CLI (saves to .md by default; prints when piping)
```bash
watsonx_minutes.generate_todos --f path/to/minutes.any --l "Japanese"
# => writes path/to/minutes_todos.md by default

# piping auto-prints to stdout (still shows progress on stderr)
watsonx_minutes.generate_todos --f path/to/minutes.any --l "Japanese" > todos.md

# choose an output path (adds .md if missing)
watsonx_minutes.generate_todos --f path/to/minutes.any --out ~/todos.md

# print only (no file) or both:
watsonx_minutes.generate_todos --f path/to/minutes.any --stdout
watsonx_minutes.generate_todos --f path/to/minutes.any --out ~/todos.md --tee
```

**Flags**:
- `--out <file>` pick output path (defaults to `.md` extension)
- `--stdout` print to stdout (ignores `--out` unless `--tee`)
- `--tee` print to stdout **and** save to file
- `--no-progress` disable progress UI
- `--debug` extra info to stderr

## Python API

```python
from watsonx_minutes import generate_todos_from_text

minutes = open("minutes.txt", encoding="utf-8").read()
md = generate_todos_from_text(
    minutes,
    language="English",
    api_key="...",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="...",
)
print(md)
```
