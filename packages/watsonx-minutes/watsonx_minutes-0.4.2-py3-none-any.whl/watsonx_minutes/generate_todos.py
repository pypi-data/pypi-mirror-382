import argparse
from pathlib import Path
import sys

from .wx_client import generate_todos_from_text, DEFAULT_MODEL_ID

# Rich UI
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
from rich.theme import Theme

console_err = Console(stderr=True, theme=Theme({
    "title": "bold cyan",
    "ok": "bold green",
    "warn": "yellow",
    "err": "bold red",
    "muted": "bright_black",
}))

CHUNK_BYTES = 128 * 1024

def _read_minutes_with_progress(minutes_path: Path, show_progress: bool) -> str:
    suffix = minutes_path.suffix.lower()
    total = minutes_path.stat().st_size
    if not show_progress:
        if suffix == ".rtf":
            from striprtf.striprtf import rtf_to_text
            raw = minutes_path.read_text(encoding="utf-8", errors="ignore")
            return rtf_to_text(raw)
        return minutes_path.read_text(encoding="utf-8", errors="ignore")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
        console=console_err,
    ) as progress:
        t = progress.add_task("Reading minutes…", total=total or 1)
        data = bytearray()
        with open(minutes_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_BYTES)
                if not chunk:
                    break
                data.extend(chunk)
                progress.update(t, advance=len(chunk))
        raw_text = data.decode("utf-8", errors="ignore")

    if suffix == ".rtf":
        from striprtf.striprtf import rtf_to_text
        return rtf_to_text(raw_text)
    return raw_text

def _ensure_md_path(path: Path) -> Path:
    if path.suffix == "":
        return path.with_suffix(".md")
    if path.suffix.lower() == ".txt":
        return path.with_suffix(".md")
    return path

def _fallback_markdown(language: str) -> str:
    return (
        "Summarization:\n- (No content extracted)\n\n"
        "TODOs:\n\n"
        "| what to do | who is in charge | deadline | others |\n"
        "|---|---|---|---|\n"
        "| TBD | TBD | TBD | TBD |\n"
    )

def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize minutes and produce TODOs via watsonx.ai")
    parser.add_argument("--f", "--file", dest="file", required=True, help="Path to minutes file (.txt or .rtf)")
    parser.add_argument("--apikey", dest="apikey", required=False, help="IBM Cloud IAM API key for watsonx.ai")
    parser.add_argument("--url", dest="url", required=False, help="Service URL, e.g. https://us-south.ml.cloud.ibm.com")
    parser.add_argument("--p", "--project-id", dest="project_id", required=False, help="watsonx.ai Project ID")
    parser.add_argument("--l", "--language", dest="language", required=True, help="Output language, e.g. English, Japanese")
    parser.add_argument("--model-id", dest="model_id", default=DEFAULT_MODEL_ID, help=f"Model ID (default: {DEFAULT_MODEL_ID})")
    parser.add_argument("--out", dest="out", help="Path to save output (defaults to <input>_todos.md; extension defaults to .md)")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout instead of saving to a file")
    parser.add_argument("--tee", action="store_true", help="Print to stdout AND save to file")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress UI (useful for CI/scripts)")
    parser.add_argument("--debug", action="store_true", help="Verbose logs to stderr (input size, sample, response shape)")

    args = parser.parse_args(argv)

    minutes_path = Path(args.file)
    if not minutes_path.exists():
        console_err.print(f"[err]File not found:[/err] {minutes_path}")
        sys.exit(2)

    console_err.print(Panel.fit(f"[title]watsonx_minutes[/title]\n[muted]Model:[/muted] {args.model_id}    [muted]Language:[/muted] {args.language}", title="Start", border_style="cyan"))

    minutes_text = _read_minutes_with_progress(minutes_path, show_progress=not args.no_progress)
    if args.debug:
        head = minutes_text[:160].replace("\n", " ")
        console_err.print(f"[muted]Input size:[/muted] {len(minutes_text)} chars — preview: {head!r}")

    # Generate
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=console_err,
    ) as progress:
        t = progress.add_task("Generating with watsonx.ai…", total=None)
        md = generate_todos_from_text(
            minutes_text,
            language=args.language,
            api_key=args.apikey,
            url=args.url,
            project_id=args.project_id,
            model_id=args.model_id,
        )
        progress.update(t, completed=1)

    if args.debug:
        console_err.print(f"[muted]Output size:[/muted] {len(md.strip())} chars")

    if not md or not md.strip():
        console_err.print("[warn]Model returned empty output. Writing a fallback template instead.[/warn]")
        md = _fallback_markdown(args.language)

    # Decide print/save behavior
    stdout_redirected = not sys.stdout.isatty()
    do_print = args.stdout or args.tee or (not args.out and stdout_redirected)
    do_save = (not args.stdout) or args.tee  # save unless user asked for stdout-only

    if do_print:
        console_err.print(Panel.fit("[ok]Generation complete[/ok] — printing Markdown below", title="Done", border_style="green"))
        print(md)

    if do_save:
        if args.out:
            out_path = _ensure_md_path(Path(args.out).expanduser())
        else:
            out_path = minutes_path.with_name(minutes_path.stem + "_todos.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        console_err.print(Panel.fit(f"[ok]Saved to[/ok] {out_path}", title="Done", border_style="green"))

if __name__ == "__main__":
    main()
