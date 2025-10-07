import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Iterable, Sequence, Set

import click

from fourdigits_cli.utils.git import Git, GitException

logger = logging.getLogger(__name__)


@click.group(help="Mypy helper commands")
def group():
    """Namespace for mypy related helpers."""
    pass


@group.command(
    help="Run mypy and report issues limited to lines changed in the diff",
    context_settings={"ignore_unknown_options": True},
)
@click.option(
    "--diff-file",
    type=click.Path(path_type=Path, dir_okay=False, readable=True),
    help="Path to an existing unified diff to use instead of generating one with git.",
)
@click.option(
    "--base-ref",
    default="origin/main",
    show_default=True,
    help="Git ref to diff against when generating a patch (ignored when --diff-file is used).",  # noqa: E501
)
@click.option(
    "--source-prefix",
    default="src",
    show_default=True,
    help="Prefix to apply to mypy reported file paths before matching against the diff.",  # noqa: E501
)
@click.argument("mypy_args", nargs=-1, type=click.UNPROCESSED)
def diff(
    diff_file: Path | None, base_ref: str, source_prefix: str, mypy_args: Sequence[str]
):
    diff_text = _load_diff(diff_file, base_ref)
    if not diff_text.strip():
        return

    context = _parse_diff(diff_text)
    if not context:
        return

    results = _get_mypy_results(mypy_args, source_prefix)
    filtered = _filter_results(results, context)

    if not filtered:
        return

    for item in filtered:
        path = item.get("file") or item.get("path")
        line_no = item.get("line") or 0
        col_no = item.get("column") or 0
        message = item.get("message", "")
        code = item.get("code")
        severity = item.get("severity") or ""

        parts = [f"{path}:{line_no}:{col_no}:"]
        if severity:
            parts.append(f" {severity}:")
        parts.append(f" {message}")
        if code:
            parts.append(f"  [{code}]")

        click.echo("".join(parts))

    raise click.exceptions.Exit(1)


def _load_diff(diff_path: Path | None, base_ref: str) -> str:
    if diff_path:
        if not diff_path.exists():
            raise click.ClickException(f"Diff file '{diff_path}' does not exist")
        return diff_path.read_text(encoding="utf-8")

    return _generate_git_diff(base_ref)


def _generate_git_diff(base_ref: str) -> str:
    git = Git()
    combined_diff = []

    try:
        for arg in [None, "--staged", f"{base_ref}..HEAD"]:
            combined_diff.append(
                git.run(list(filter(None, ["diff", arg]))).strip().rstrip("\n")
            )
    except GitException as exc:
        raise click.ClickException(f"Unable to run git diff: {exc}") from exc

    return "\n".join(combined_diff)


def _parse_diff(diff_text: str) -> Dict[str, Set[int]]:
    """
    Parse a unified diff and return a mapping of file paths to sets of modified
    line numbers.
    """
    changes: Dict[str, Set[int]] = {}
    current_file: str | None = None
    lines = diff_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        # '+++ ' header indicates the new file path
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            # Skip deleted files
            if path != "/dev/null":
                current_file = os.path.normpath(path)
                changes.setdefault(current_file, set())
            else:
                current_file = None

        # Parse hunk headers for added lines
        elif line.startswith("@@ ") and current_file is not None:
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            if match:
                new_line_no = int(match.group(1))
                i += 1
                # Process lines in this hunk
                while i < len(lines) and lines[i] and lines[i][0] in (" ", "+", "-"):
                    prefix = lines[i][0]
                    if prefix == " ":
                        new_line_no += 1
                    elif prefix == "+":
                        changes[current_file].add(new_line_no)
                        new_line_no += 1
                    # '-' lines are removals; skip without increment
                    i += 1
                continue

        i += 1

    return changes


def _get_mypy_results(mypy_args: Sequence[str], source_prefix: str) -> list[dict]:
    """
    Run mypy with JSON output and return a list of result dicts,
    normalizing file paths by prefixing with source_prefix.
    """
    command = ["mypy", "--output", "json", *mypy_args]
    try:
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise click.ClickException("mypy executable not found") from exc

    output = proc.stdout or ""
    stderr = proc.stderr or ""

    if not output.strip() and proc.returncode not in (0, 1):
        message = stderr.strip() or f"mypy exited with status {proc.returncode}"
        raise click.ClickException(message)

    results: list[dict] = []
    for line in output.splitlines():
        try:
            result = json.loads(line)
        except json.JSONDecodeError:
            if "errors prevented further checking" in line:
                if output.strip():
                    click.echo(output.strip())
                if stderr.strip():
                    click.echo(stderr.strip(), err=True)
                raise click.exceptions.Exit(1)
            continue

        file_path = result.get("file")
        if file_path:
            path_obj = Path(file_path)
            if not path_obj.is_absolute() and source_prefix:
                prefix = Path(source_prefix)
                if prefix.parts and path_obj.parts[: len(prefix.parts)] != prefix.parts:
                    path_obj = prefix / path_obj
            result["file"] = os.path.normpath(str(path_obj))

        results.append(result)

    if stderr.strip():
        logger.debug(f"mypy stderr: {stderr.strip()}")

    return results


def _filter_results(
    mypy_results: Iterable[dict], context: Dict[str, Set[int]]
) -> list[dict]:
    """
    Filter the list of mypy result dicts, keeping only errors where
    the file path and line number appear in the context mapping.
    """
    filtered: list[dict] = []
    for item in mypy_results:
        path = item.get("file")
        if not path:
            continue

        normalized = os.path.normpath(path)
        line_no = item.get("line")
        if normalized in context and line_no in context[normalized]:
            filtered.append(item)

    return filtered
