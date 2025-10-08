# watsonx_minutes

Summarize a Minutes of Meeting file with **IBM watsonx.ai** and emit standardized TODOs.
Includes a modern progress UI (Rich).

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

## CLI (saves to .md by default, but prints when piping)
```bash
# default: saves <input>_todos.md (shows progress on stderr)
watsonx_minutes.generate_todos --f path/to/minutes.rtf --l "Japanese"

# piping? we auto-detect redirection and print to stdout instead
watsonx_minutes.generate_todos --f path/to/minutes.rtf --l "Japanese" > todos.md

# force a path (adds .md if missing)
watsonx_minutes.generate_todos --f path/to/minutes.rtf --l "Japanese" --out ~/todos.md

# print only (no file)
watsonx_minutes.generate_todos --f path/to/minutes.rtf --l "Japanese" --stdout

# both print AND save
watsonx_minutes.generate_todos --f path/to/minutes.rtf --l "Japanese" --out ~/todos.md --tee
```

**Flags**:
- `--out <file>` pick output path (defaults to `.md` extension)
- `--stdout` print to stdout (ignores `--out` unless `--tee` is present)
- `--tee` print to stdout **and** save to file
- `--no-progress` disable progress UI
- `--debug` extra info to stderr

**Note:** Progress UI is sent to **stderr**, so it remains visible with `>` redirection.
