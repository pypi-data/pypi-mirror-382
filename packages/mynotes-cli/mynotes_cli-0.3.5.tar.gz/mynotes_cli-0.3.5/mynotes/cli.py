
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

APP_NAME = "mynotes"
STORE_PATH = Path(os.environ.get("MYNOTES_PATH", Path.home() / ".mynotes.json"))
TAGS_PATH = Path(os.environ.get("MYNOTES_TAGS_PATH", Path.home() / ".mynotes_tags.json"))

# ANSI fallback colors (also used to map to Rich colors)
ANSI_COLORS = {
    "black": 30, "red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
    "bright_black": 90, "bright_red": 91, "bright_green": 92, "bright_yellow": 93, "bright_blue": 94,
    "bright_magenta": 95, "bright_cyan": 96, "bright_white": 97
}

RICH_COLOR_MAP = {
    "black": "black",
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "blue": "blue",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
    "bright_black": "grey70",
    "bright_red": "bright_red",
    "bright_green": "bright_green",
    "bright_yellow": "bright_yellow",
    "bright_blue": "bright_blue",
    "bright_magenta": "bright_magenta",
    "bright_cyan": "bright_cyan",
    "bright_white": "white"
}

DEFAULT_TAGS = {
    "skola": "bright_blue",
    "fll": "bright_magenta",
    "ftc": "bright_cyan"
}

def _load_notes() -> List[Dict[str, Any]]:
    if not STORE_PATH.exists():
        return []
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def _save_notes(items: List[Dict[str, Any]]) -> None:
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def _load_tags() -> Dict[str, str]:
    if TAGS_PATH.exists():
        try:
            with open(TAGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    # initialize with defaults
    _save_tags(DEFAULT_TAGS)
    return DEFAULT_TAGS.copy()

def _save_tags(tags: Dict[str, str]) -> None:
    with open(TAGS_PATH, "w", encoding="utf-8") as f:
        json.dump(tags, f, ensure_ascii=False, indent=2)

def _ansi_colorize(text: str, color_name: str) -> str:
    code = ANSI_COLORS.get(color_name, None)
    if code is None:
        return text
    return f"\033[{code}m{text}\033[0m"

def _relative(ts: Optional[str]) -> str:
    if not ts:
        return "-"
    try:
        dt = datetime.fromisoformat(ts)
        delta = datetime.now() - dt
        secs = int(delta.total_seconds())
        if secs < 60:
            return f"před {secs}s"
        mins = secs // 60
        if mins < 60:
            return f"před {mins} min"
        hrs = mins // 60
        if hrs < 24:
            return f"před {hrs} h"
        days = hrs // 24
        return f"před {days} d"
    except Exception:
        return ts

def add_note(text: str, tags: Optional[List[str]] = None) -> None:
    items = _load_notes()
    note_id = (max((it.get("id", 0) for it in items), default=0) + 1) if items else 1
    items.append({
        "id": note_id,
        "text": text,
        "tags": sorted(list(set(tags or []))),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": None
    })
    _save_notes(items)
    print(f"✅ Přidáno #{note_id}: {text}")

def _render_tags_badges(tags: List[str], palette: Dict[str, str], rich_mode: bool):
    # Contrast-aware badges: bright bg -> black text, dark bg -> white text
    def fg_for(color_name: str) -> str:
        bright_set = {"bright_white", "white", "yellow", "bright_yellow"}
        return "black" if color_name in bright_set else "white"

    if rich_mode:
        from rich.text import Text
        t = Text()
        for tag in tags:
            base = palette.get(tag, "bright_black")
            bg = RICH_COLOR_MAP.get(base, "grey70")
            fg = fg_for(base)
            t.append(f" {tag} ", style=f"bold {fg} on {bg}")
            t.append(" ")
        return t
    # ANSI fallback: just colored text in brackets
    parts = []
    for tag in tags:
        color = palette.get(tag, "bright_black")
        parts.append(_ansi_colorize(f"[{tag}]", color))
    return " ".join(parts)

def list_notes(filter_tag: Optional[str] = None, plain: bool=False) -> None:
    items = _load_notes()
    tags_palette = _load_tags()
    if filter_tag:
        items = [it for it in items if filter_tag in it.get("tags", [])]
    if not items:
        print("Žádné poznámky zatím nejsou.")
        return

    if not plain:
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import box
            console = Console()
            table = Table(title="📒 mynotes", box=box.SIMPLE_HEAVY)
            table.add_column("ID", style="bold cyan", justify="right", no_wrap=True)
            table.add_column("Poznámka", style="white")
            table.add_column("Tagy", style="dim")
            table.add_column("Vytvořeno", style="dim", no_wrap=True)
            table.add_column("Upraveno", style="dim", no_wrap=True)
            for it in items:
                badge = _render_tags_badges(it.get("tags", []), tags_palette, rich_mode=True)
                created = _relative(it.get("created_at"))
                updated = _relative(it.get("updated_at"))
                table.add_row(str(it.get("id")), it.get("text",""), badge, created, updated)
            console.print(table)
            return
        except Exception:
            pass

    # ANSI/plain fallback
    for it in items:
        tag_badges = _render_tags_badges(it.get("tags", []), tags_palette, rich_mode=False)
        upd = f" (upd {it.get('updated_at')})" if it.get("updated_at") else ""
        print(f"[{it.get('id')}] {it.get('text')}  {tag_badges}  ({it.get('created_at')}){upd}")

def delete_note(note_id: int) -> None:
    items = _load_notes()
    new_items = [it for it in items if it.get("id") != note_id]
    if len(new_items) == len(items):
        print(f"⚠️ Poznámka s ID {note_id} nenalezena.")
        return
    _save_notes(new_items)
    print(f"🗑️ Smazáno #{note_id}.")

def edit_note(note_id: int, new_text: Optional[str], add_tags: Optional[List[str]], remove_tags: Optional[List[str]]) -> None:
    items = _load_notes()
    for it in items:
        if it.get("id") == note_id:
            if new_text:
                it["text"] = new_text
            if add_tags:
                it["tags"] = sorted(list(set((it.get("tags") or []) + add_tags)))
            if remove_tags:
                it["tags"] = [t for t in (it.get("tags") or []) if t not in remove_tags]
            it["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save_notes(items)
            print(f"✏️ Upraveno #{note_id}.")
            return
    print(f"⚠️ Poznámka s ID {note_id} nenalezena.")

# ------ Tag management ------
def tag_list(plain: bool=False) -> None:
    tags = _load_tags()
    if not tags:
        print("Nenastaveny žádné tagy.")
        return
    if not plain:
        try:
            from rich.console import Console
            from rich.table import Table
            from rich import box
            console = Console()
            table = Table(title="🏷️ Tagy", box=box.SIMPLE_HEAVY)
            table.add_column("Tag", style="bold")
            table.add_column("Barva")
            for name, color in tags.items():
                rich_color = RICH_COLOR_MAP.get(color, "grey70")
                table.add_row(f"[bold {rich_color}]{name}[/]", color)
            console.print(table)
            return
        except Exception:
            pass
    print("Tagy (název: barva):")
    for name, color in tags.items():
        print(f" - {name}: {color}")

def tag_add(name: str, color: str) -> None:
    tags = _load_tags()
    tags[name] = color
    _save_tags(tags)
    print(f"✅ Přidán tag '{name}' s barvou '{color}'.")

def tag_edit(name: str, new_name: Optional[str], color: Optional[str]) -> None:
    tags = _load_tags()
    if name not in tags:
        print(f"⚠️ Tag '{name}' neexistuje.")
        return
    final_name = new_name or name
    final_color = color or tags[name]
    # rename key if needed
    if final_name != name:
        tags[final_name] = final_color
        del tags[name]
        # also update notes referencing this tag
        items = _load_notes()
        for it in items:
            if "tags" in it and name in it["tags"]:
                it["tags"] = [final_name if t == name else t for t in it["tags"]]
        _save_notes(items)
    else:
        tags[final_name] = final_color
    _save_tags(tags)
    print(f"✏️ Upraven tag '{final_name}' (barva: {final_color}).")

def tag_delete(name: str) -> None:
    tags = _load_tags()
    if name not in tags:
        print(f"⚠️ Tag '{name}' neexistuje.")
        return
    del tags[name]
    _save_tags(tags)
    print(f"🗑️ Smazán tag '{name}'. (Pozn.: z poznámek se neodebrán automaticky)")

# ------ Export ------
def export_notes(fmt: str, out_path: Path, filter_tag: Optional[str]) -> None:
    items = _load_notes()
    if filter_tag:
        items = [it for it in items if filter_tag in it.get("tags", [])]

    if fmt.lower() == "txt":
        content = "\n".join([f"[{it['id']}] {it['text']}  (tags: {', '.join(it.get('tags', []))})" for it in items])
        out_path.write_text(content, encoding="utf-8")
        print(f"📄 Export hotov: {out_path}")
    elif fmt.lower() == "md":
        lines = ["# Notes export", ""]
        for it in items:
            tags = " ".join([f"`{t}`" for t in it.get("tags", [])])
            lines.append(f"- **#{it['id']}** {it['text']}  — _{it['created_at']}_  {tags}")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"📝 Markdown export hotov: {out_path}")
    elif fmt.lower() == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            c = canvas.Canvas(str(out_path), pagesize=A4)
            width, height = A4
            y = height - 20*mm
            c.setFont("Helvetica-Bold", 14)
            c.drawString(20*mm, y, "Notes export")
            y -= 10*mm
            c.setFont("Helvetica", 11)
            for it in items:
                line = f"#{it['id']} {it['text']}"
                c.drawString(20*mm, y, line[:110])
                y -= 6*mm
                tags = ", ".join(it.get("tags", []))
                meta = f"({it.get('created_at')}) tags: {tags}"
                c.setFont("Helvetica-Oblique", 9)
                c.drawString(22*mm, y, meta[:120])
                c.setFont("Helvetica", 11)
                y -= 8*mm
                if y < 25*mm:
                    c.showPage()
                    y = height - 20*mm
            c.save()
        except Exception:
            _export_pdf_simple(items, out_path)
        print(f"📕 PDF export hotov: {out_path}")
    else:
        print("⚠️ Nepodporovaný formát. Použij: txt | md | pdf")

def _export_pdf_simple(items: List[Dict[str, Any]], out_path: Path) -> None:
    # Minimalist single-page PDF (fallback)
    y = 800
    lines = [f"Notes export ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"]
    for it in items:
        tags = ", ".join(it.get("tags", []))
        lines.append(f"#{it['id']} {it['text']} (tags: {tags}) [{it['created_at']}]")
    content_ops = ["BT /F1 12 Tf 50 %d Td ({} ) Tj" % y]
    first = True
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if first:
            content_ops[0] = f"BT /F1 12 Tf 50 {y} Td ({safe}) Tj"
            first = False
        else:
            y -= 16
            content_ops.append(f"0 -16 Td ({safe}) Tj")
    content_ops.append("ET")
    content_stream = "\n".join(content_ops).encode("latin-1", "ignore")
    objects = []
    def add(obj: bytes): objects.append(obj)
    add(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    add(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    add(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n")
    add(f"4 0 obj << /Length {len(content_stream)} >> stream\n".encode("ascii") + content_stream + b"\nendstream endobj\n")
    add(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref_pos = len(pdf)
    pdf += b"xref\n0 %d\n" % (len(objects)+1)
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += b"%010d 00000 n \n"
    pdf += b"trailer << /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objects)+1, xref_pos)
    out_path.write_bytes(pdf)

# ------- Completion helpers (argcomplete) -------
def _complete_tags(prefix, **kwargs):
    tags = _load_tags().keys()
    return [t for t in tags if t.startswith(prefix)]

def _complete_note_ids(prefix, **kwargs):
    try:
        ids = [str(it["id"]) for it in _load_notes()]
        return [i for i in ids if i.startswith(prefix)]
    except Exception:
        return []

def main():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Jednoduché poznámky v terminálu (JSON v ~/.mynotes.json)."
    )
    sub = parser.add_subparsers(dest="cmd")

    # ---- notes subcommands ----
    p_add = sub.add_parser("add", help="Přidá novou poznámku")
    p_add.add_argument("text", help="Text poznámky", nargs="+")
    p_add.add_argument("--tags", nargs="*", help="Seznam tagů, např.: --tags skola fll").completer = _complete_tags

    p_list = sub.add_parser("list", help="Vypíše poznámky v pěkné tabulce (Rich)")
    p_list.add_argument("--tag", help="Filtrovat podle tagu").completer = _complete_tags
    p_list.add_argument("--plain", action="store_true", help="Vynutit prostý výstup (bez Rich)")

    p_del = sub.add_parser("delete", help="Smaže poznámku dle ID")
    p_del.add_argument("id", type=int, help="ID poznámky").completer = _complete_note_ids

    p_edit = sub.add_parser("edit", help="Upraví poznámku")
    p_edit.add_argument("id", type=int, help="ID poznámky").completer = _complete_note_ids
    p_edit.add_argument("--text", nargs="+", help="Nový text")
    p_edit.add_argument("--add-tags", nargs="*", help="Tagy, které se mají přidat").completer = _complete_tags
    p_edit.add_argument("--remove-tags", nargs="*", help="Tagy, které se mají odebrat").completer = _complete_tags

    p_export = sub.add_parser("export", help="Export poznámek do txt/pdf/md")
    p_export.add_argument("--format", choices=["txt", "pdf", "md"], required=True)
    p_export.add_argument("--out", required=True, help="Cílový soubor (např. notes.pdf)")
    p_export.add_argument("--tag", help="Filtrovat podle tagu").completer = _complete_tags

    # ---- tag subcommands ----
    p_tag = sub.add_parser("tag", help="Správa tagů")
    tag_sub = p_tag.add_subparsers(dest="tag_cmd")

    p_tag_list = tag_sub.add_parser("list", help="Vypsat tagy")
    p_tag_list.add_argument("--plain", action="store_true", help="Vynutit prostý výstup")

    p_tag_add = tag_sub.add_parser("add", help="Přidat tag")
    p_tag_add.add_argument("name", help="Název tagu")
    p_tag_add.add_argument("--color", required=True, help=f"Barva (např. {'|'.join(ANSI_COLORS.keys())})")

    p_tag_edit = tag_sub.add_parser("edit", help="Upravit tag (přejmenovat / změnit barvu)")
    p_tag_edit.add_argument("name", help="Původní název tagu").completer = _complete_tags
    p_tag_edit.add_argument("--new-name", help="Nový název tagu")
    p_tag_edit.add_argument("--color", help=f"Nová barva (např. {'|'.join(ANSI_COLORS.keys())})")

    p_tag_del = tag_sub.add_parser("delete", help="Smazat tag")
    p_tag_del.add_argument("name", help="Název tagu k odstranění").completer = _complete_tags

    # backward compatible flags like: mynotes --d, --a, --l
    parser.add_argument("--a", "--add", dest="flag_add", nargs="+", help="Přidá poznámku (ekvivalent subpříkazu add)")
    parser.add_argument("--l", "--list", dest="flag_list", action="store_true", help="Vypíše poznámky (ekvivalent subpříkazu list)")
    parser.add_argument("--d", "--delete", dest="flag_delete", type=int, help="Smaže poznámku dle ID (ekvivalent subpříkazu delete)")

    # Enable argcomplete if available
    try:
        import argcomplete  # type: ignore
        argcomplete.autocomplete(parser)
    except Exception:
        pass

    args = parser.parse_args()

    # Handle flags first (for cases like: mynotes --d 3)
    if getattr(args, "flag_add", None):
        add_note(" ".join(args.flag_add))
        return
    if getattr(args, "flag_list", False):
        list_notes()
        return
    if getattr(args, "flag_delete", None) is not None:
        delete_note(args.flag_delete)
        return

    # Subcommands
    if args.cmd == "add":
        add_note(" ".join(args.text), tags=args.tags)
    elif args.cmd == "list":
        list_notes(filter_tag=args.tag, plain=args.plain)
    elif args.cmd == "delete":
        delete_note(args.id)
    elif args.cmd == "edit":
        new_text = " ".join(args.text) if args.text else None
        edit_note(args.id, new_text, args.add_tags, args.remove_tags)
    elif args.cmd == "export":
        out_path = Path(args.out).expanduser().resolve()
        export_notes(args.format, out_path, args.tag)
    elif args.cmd == "tag":
        if args.tag_cmd == "list":
            tag_list(plain=args.plain)
        elif args.tag_cmd == "add":
            tag_add(args.name, args.color)
        elif args.tag_cmd == "edit":
            tag_edit(args.name, args.new_name, args.color)
        elif args.tag_cmd == "delete":
            tag_delete(args.name)
        else:
            print("Použij: mynotes tag [list|add|edit|delete] ...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
