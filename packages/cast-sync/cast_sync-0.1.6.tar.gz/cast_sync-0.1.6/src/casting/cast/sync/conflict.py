"""Conflict resolution for Cast Sync."""

import difflib
import os
import re
from enum import Enum
from io import StringIO
from pathlib import Path

from casting.cast.core.registry import resolve_cast_by_name
from casting.cast.core.yamlio import reorder_cast_fields
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from ruamel.yaml import YAML


class ConflictResolution(Enum):
    """Conflict resolution choices."""

    KEEP_LOCAL = "local"
    KEEP_PEER = "peer"
    SKIP = "skip"


def handle_conflict(
    local_path: Path,
    peer_path: Path | None,
    file_id: str,
    peer_name: str,
    cast_root: Path,
    interactive: bool = True,
    local_content: str | None = None,
    peer_content: str | None = None,
) -> ConflictResolution:
    """
    Handle a sync conflict by creating sidecar files and prompting user.

    Args:
        local_path: Path to local file
        peer_path: Path to peer file (if it exists)
        file_id: ID of the file
        peer_name: Name of the peer cast
        cast_root: Root of the Cast (contains .cast/)
        interactive: Whether to prompt user
        local_content: Optional local content to use instead of reading file
        peer_content: Optional peer content to use instead of reading file

    Returns:
        ConflictResolution choice
    """
    # Preview (side-by-side) with YAML front matter awareness
    console = Console()
    # YAML instance for readable/ordered diffs (must exist before nested functions use it)
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    _yaml.width = 4096
    try:
        local_preview: str = (
            local_content
            if local_content is not None
            else (local_path.read_text(encoding="utf-8") if local_path.exists() else "")
        )
        peer_preview: str = (
            peer_content
            if peer_content is not None
            else (peer_path.read_text(encoding="utf-8") if peer_path and peer_path.exists() else "")
        )
    except Exception:
        local_preview, peer_preview = "", ""

    # Resolve cast-relative paths for clearer UI (names/paths)
    def _local_cast_info(root: Path) -> tuple[str, Path]:
        try:
            cfg = root / ".cast" / "config.yaml"
            data = _yaml.load(cfg.read_text(encoding="utf-8")) or {}
            cast_name = data.get("cast-name", "LOCAL")
            return cast_name, (root / "Cast")
        except Exception:
            return "LOCAL", (root / "Cast")

    cast_name, local_vault_path = _local_cast_info(cast_root)

    def _guess_peer_base(p: Path | None) -> Path | None:
        """
        Try to find a sensible base for 'peer_path' so we can render a pretty relative path.
        Works for both CAST ('.../Cast/...') and CODEBASE ('.../docs/cast/...').
        """
        if p is None:
            return None
        for anc in [p] + list(p.parents):
            nm = anc.name.lower()
            if nm == "cast":
                # catches both '/Cast' and '/docs/cast'
                return anc
        return p.parent

    def _rel_or_name(base: Path | None, p: Path | None) -> str:
        if base is None or p is None:
            return p.name if p else ""
        try:
            return str(p.relative_to(base))
        except Exception:
            return p.name

    # Number of context lines to show around diffs (fold the rest).
    # Can be adjusted per-run via environment variable.
    try:
        ctx = max(0, int(os.environ.get("CAST_DIFF_CONTEXT", "3")))
    except ValueError:
        ctx = 3

    def _split_front_matter(text: str) -> tuple[str | None, str]:
        """
        Split markdown into (yaml_text, body) if front matter exists; else (None, text).
        Recognizes common '---\\n...\\n---' front matter at file start.
        """
        m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", text, re.DOTALL)
        if not m:
            return None, text
        yaml_text = m.group(1)
        body = text[m.end() :]
        return yaml_text, body

    # (already initialized above)

    def _canonicalize_yaml_for_diff(yaml_text: str) -> str:
        """
        For display: parse YAML, reorder so that:
          - 'last-updated' is first,
          - cast-* fields are in canonical order,
          - others follow.
        This includes 'last-updated' (unlike digest).
        """
        try:
            data = _yaml.load(yaml_text) or {}
            if not isinstance(data, dict):
                return yaml_text
            data = reorder_cast_fields(dict(data))
            buf = StringIO()
            _yaml.dump(data, buf)
            return buf.getvalue().rstrip("\n")
        except Exception:
            # Fallback to original if parsing fails
            return yaml_text

    def _norm_lines(s: str) -> list[str]:
        return (s or "").replace("\r\n", "\n").replace("\r", "\n").splitlines()

    def _intraline(left: str, right: str) -> tuple[Text, Text]:
        """
        Produce Text objects with fine-grained highlights for a replace block.
        Deletions in LEFT are red; insertions in RIGHT are green.
        """
        sm = difflib.SequenceMatcher(None, left, right, autojunk=False)
        left_text = Text()
        right_text = Text()
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            lseg = left[i1:i2]
            rseg = right[j1:j2]
            if tag == "equal":
                left_text.append(lseg)
                right_text.append(rseg)
            elif tag == "delete":
                left_text.append(lseg, style="bold red")
            elif tag == "insert":
                right_text.append(rseg, style="bold green")
            elif tag == "replace":
                left_text.append(lseg, style="bold red")
                right_text.append(rseg, style="bold green")
        return left_text, right_text

    def _ln_cell(ln: int | None) -> Text:
        """Format a line-number prefix."""
        s = f"{ln:>4}" if ln is not None else "    "
        return Text(s + " │ ", style="dim")

    def _fold_row(n: int) -> tuple[Text, Text]:
        msg = Text(f"… {n} lines unchanged …", style="dim italic")
        return msg, msg

    def _render_side_by_side(a: str, b: str, title_left: str, title_right: str, context: int) -> Table:
        """
        Render a side-by-side, line-diffed table using Rich.Table with headers,
        line numbers, intraline highlights, and context folding.
        """
        a_lines = _norm_lines(a)
        b_lines = _norm_lines(b)
        sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)

        table = Table(
            expand=True,
            show_edge=False,
            box=box.SIMPLE_HEAD,
            pad_edge=False,
        )
        table.add_column(title_left, ratio=1, overflow="fold", no_wrap=False, min_width=10)
        table.add_column(title_right, ratio=1, overflow="fold", no_wrap=False, min_width=10)

        ln_a = 1
        ln_b = 1

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal" and context > 0:
                block_len = i2 - i1  # equals on both sides
                if block_len > 2 * context:
                    # head
                    for k in range(context):
                        left_txt = a_lines[i1 + k]
                        right_txt = b_lines[j1 + k]
                        left = Text(left_txt, style="dim")
                        right = Text(right_txt, style="dim")
                        table.add_row(_ln_cell(ln_a) + left, _ln_cell(ln_b) + right)
                        ln_a += 1
                        ln_b += 1
                    # folded middle
                    folded = block_len - (2 * context)
                    lmsg, rmsg = _fold_row(folded)
                    table.add_row(_ln_cell(None) + lmsg, _ln_cell(None) + rmsg)
                    # tail
                    for k in range(block_len - context, block_len):
                        left_txt = a_lines[i1 + k]
                        right_txt = b_lines[j1 + k]
                        left = Text(left_txt, style="dim")
                        right = Text(right_txt, style="dim")
                        table.add_row(_ln_cell(ln_a) + left, _ln_cell(ln_b) + right)
                        ln_a += 1
                        ln_b += 1
                    continue  # done with this equal block

            # Non-folded handling (including equal blocks when small)
            span_a = i2 - i1
            span_b = j2 - j1
            span = max(span_a, span_b)
            for k in range(span):
                has_left = k < span_a
                has_right = k < span_b
                left_txt = a_lines[i1 + k] if has_left else ""
                right_txt = b_lines[j1 + k] if has_right else ""

                # Build left/right Text with styles
                if tag == "equal":
                    left_styled = Text(left_txt, style="dim")
                    right_styled = Text(right_txt, style="dim")
                elif tag == "delete":
                    # Line-level background highlight + text styling
                    left_styled = Text(left_txt, style="bold red on rgb(64,32,32)")
                    right_styled = Text(right_txt, style="dim")
                elif tag == "insert":
                    # Line-level background highlight + text styling
                    left_styled = Text(left_txt, style="dim")
                    right_styled = Text(right_txt, style="bold green on rgb(32,64,32)")
                elif tag == "replace":
                    if has_left and has_right:
                        # Get intraline highlights first
                        left_intra, right_intra = _intraline(left_txt, right_txt)
                        # Apply line-level background highlights
                        left_styled = Text()
                        right_styled = Text()
                        for segment in left_intra:
                            if segment.style and "red" in str(segment.style):
                                # Keep character-level red, add line-level background
                                left_styled.append(segment.plain, style="bold red on rgb(64,32,32)")
                            else:
                                # Apply line-level background to unchanged parts
                                left_styled.append(segment.plain, style="on rgb(48,32,32)")
                        for segment in right_intra:
                            if segment.style and "green" in str(segment.style):
                                # Keep character-level green, add line-level background
                                right_styled.append(segment.plain, style="bold green on rgb(32,64,32)")
                            else:
                                # Apply line-level background to unchanged parts
                                right_styled.append(segment.plain, style="on rgb(32,48,32)")
                    elif has_left:  # only left
                        left_styled = Text(left_txt, style="bold red on rgb(64,32,32)")
                        right_styled = Text("", style="dim")
                    else:  # only right
                        left_styled = Text("", style="dim")
                        right_styled = Text(right_txt, style="bold green on rgb(32,64,32)")
                else:
                    left_styled = Text(left_txt)
                    right_styled = Text(right_txt)

                # Prefix with line numbers where applicable
                cell_left = _ln_cell(ln_a if has_left else None) + left_styled
                cell_right = _ln_cell(ln_b if has_right else None) + right_styled

                table.add_row(cell_left, cell_right)

                if has_left:
                    ln_a += 1
                if has_right:
                    ln_b += 1

        return table

    if interactive:
        console.rule("[bold red]Conflict detected[/bold red]")

        # Split both sides into (yaml, body)
        local_yaml, local_body = _split_front_matter(local_preview or "")
        peer_yaml, peer_body = _split_front_matter(peer_preview or "")

        # Compute rel paths & titles for both sides
        # LOCAL
        local_rel = _rel_or_name(local_vault_path, local_path)
        local_title = None
        if local_yaml is not None:
            try:
                y = _yaml.load(local_yaml) or {}
                if isinstance(y, dict):
                    local_title = y.get("title") or y.get("name")
            except Exception:
                pass
        # PEER
        peer_rel = ""
        peer_title = None
        if peer_path:
            try:
                base = _guess_peer_base(peer_path)
                peer_rel = _rel_or_name(base, peer_path)
            except Exception:
                peer_rel = peer_path.name
        if peer_yaml is not None:
            try:
                y = _yaml.load(peer_yaml) or {}
                if isinstance(y, dict):
                    peer_title = y.get("title") or y.get("name")
            except Exception:
                pass

        # Legend panel
        legend = Table.grid(padding=(0, 2))
        legend.add_column(justify="left")
        legend.add_column(justify="left")
        legend.add_row(
            f"[bold]Left:[/bold] LOCAL ([cyan]{cast_name}[/cyan])",
            f"[bold]Right:[/bold] PEER [[magenta]{peer_name}[/magenta]]",
        )
        legend.add_row(
            f"• File: [white]{local_rel}[/white]" + (f"  — title: [white]{local_title}[/white]" if local_title else ""),
            (
                "• File: [white]"
                + (peer_rel or "(missing)")
                + "[/white]"
                + (f"  — title: [white]{peer_title}[/white]" if peer_title else "")
            ),
        )
        legend.add_row("[red]Red[/red]: change/delete in LOCAL", "[green]Green[/green]: add/change in PEER")
        legend.add_row(
            "[dim]Lines with changes have background highlights[/dim]",
            "[dim]Character changes are emphasized within lines[/dim]",
        )
        console.print(Panel(legend, title="Diff legend", expand=True))

        # YAML diff (empty string if missing)
        yaml_left = _canonicalize_yaml_for_diff(local_yaml) if local_yaml is not None else ""
        yaml_right = _canonicalize_yaml_for_diff(peer_yaml) if peer_yaml is not None else ""
        yaml_table = _render_side_by_side(
            yaml_left,
            yaml_right,
            f"LOCAL ({cast_name}) · YAML",
            f"PEER[{peer_name}] · YAML",
            context=ctx,
        )
        console.print(Panel(yaml_table, title="YAML front matter (side‑by‑side diff)", expand=True))

        # Body diff
        body_table = _render_side_by_side(
            (local_body or ""),
            (peer_body or ""),
            f"LOCAL ({cast_name}) · body",
            f"PEER[{peer_name}] · body",
            context=ctx,
        )
        console.print(Panel(body_table, title="Markdown body (side‑by‑side diff)", expand=True))

    if not interactive:
        # Non-interactive: keep local (show rel path if possible)
        try:
            rel = _rel_or_name(local_vault_path, local_path)
        except Exception:
            rel = local_path.name
        console.print(f"[yellow]Conflict in {rel}: keeping LOCAL version[/yellow]")
        return ConflictResolution.KEEP_LOCAL

    # Interactive prompt
    opt_local = f"Keep LOCAL (keep name/path: {_rel_or_name(local_vault_path, local_path)})"
    opt_peer = f"Keep PEER  (adopt name/path: {peer_rel or '(missing)'} )"
    console.print(f"\nOptions:\n  1. {opt_local}\n  2. {opt_peer}\n  3. Skip (resolve later)")

    while True:
        raw = input("\nYour choice [1/2/3 | keep_local | keep_peer | skip]: ").strip()
        choice = raw.lower()
        if choice in ("1", "l", "local", "keep_local", "keep local", "keep-local", "keep"):
            return ConflictResolution.KEEP_LOCAL
        elif choice in ("2", "p", "peer", "keep_peer", "keep peer", "keep-peer"):
            return ConflictResolution.KEEP_PEER
        elif choice in ("3", "s", "skip", "later"):
            return ConflictResolution.SKIP
        else:
            console.print("[red]Invalid choice. Please enter 1, 2, 3, or a named option.[/red]")
