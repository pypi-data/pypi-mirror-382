"""Diff utilities for PatchAI."""

import difflib
import json
from typing import Dict, List
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.columns import Columns

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def serialize(data: Dict, format: str = "json") -> str:
    """Serialize data to string."""
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "yaml" and HAS_YAML:
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    return str(data)


def generate_unified_diff(original: Dict, modified: Dict, format: str = "json") -> str:
    """Generate unified diff between two data structures."""
    original_str = serialize(original, format)
    modified_str = serialize(modified, format)
    
    diff = difflib.unified_diff(
        original_str.splitlines(keepends=True),
        modified_str.splitlines(keepends=True),
        fromfile='original',
        tofile='modified',
        lineterm=''
    )
    
    return ''.join(diff)


def print_diff(original: Dict, modified: Dict, format: str = "json", style: str = "unified", console: Console = None):
    """
    Print colored diff to console.
    
    Args:
        original: Original data
        modified: Modified data
        format: Data format ('json' or 'yaml')
        style: Diff style ('unified' or 'side-by-side')
    """
    console = console or Console()
    
    if style == "unified":
        _print_unified_diff(console, original, modified, format)
    elif style == "side-by-side":
        _print_side_by_side_diff(console, original, modified, format)
    else:
        raise ValueError(f"Unknown diff style: {style}")


def _print_unified_diff(console: Console, original: Dict, modified: Dict, format: str):
    """Print unified diff."""
    diff_text = generate_unified_diff(original, modified, format)
    
    if not diff_text:
        console.print("[green]✓ No changes[/green]")
        return
    
    # Color the diff lines
    lines = []
    for line in diff_text.split('\n'):
        if line.startswith('+++') or line.startswith('---'):
            lines.append(f"[bold cyan]{line}[/bold cyan]")
        elif line.startswith('@@'):
            lines.append(f"[bold blue]{line}[/bold blue]")
        elif line.startswith('+'):
            lines.append(f"[green]{line}[/green]")
        elif line.startswith('-'):
            lines.append(f"[red]{line}[/red]")
        else:
            lines.append(line)
    
    console.print(Panel('\n'.join(lines), title="[bold]Changes[/bold]", border_style="blue"))


def _print_side_by_side_diff(console: Console, original: Dict, modified: Dict, format: str):
    """Print side-by-side diff."""
    original_str = serialize(original, format)
    modified_str = serialize(modified, format)
    
    # Create syntax-highlighted panels
    original_syntax = Syntax(
        original_str, 
        format, 
        theme="monokai", 
        line_numbers=True
    )
    modified_syntax = Syntax(
        modified_str, 
        format, 
        theme="monokai", 
        line_numbers=True
    )
    
    original_panel = Panel(
        original_syntax, 
        title="[red]Original[/red]", 
        border_style="red"
    )
    modified_panel = Panel(
        modified_syntax, 
        title="[green]Modified[/green]", 
        border_style="green"
    )
    
    console.print(Columns([original_panel, modified_panel], equal=True))


def get_changed_fields(original: Dict, modified: Dict, prefix: str = "") -> List[str]:
    """Get list of changed field paths."""
    changes = []
    
    def compare(orig, mod, path):
        if isinstance(orig, dict) and isinstance(mod, dict):
            all_keys = set(orig.keys()) | set(mod.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key not in orig:
                    changes.append(f"+ {new_path}")
                elif key not in mod:
                    changes.append(f"- {new_path}")
                elif orig[key] != mod[key]:
                    if isinstance(orig[key], dict) or isinstance(mod[key], dict):
                        compare(orig[key], mod[key], new_path)
                    else:
                        changes.append(f"~ {new_path}")
        elif orig != mod:
            changes.append(f"~ {path}")
    
    compare(original, modified, prefix)
    return changes


def print_summary(original: Dict, modified: Dict):
    """Print summary of changes."""
    console = Console()
    changes = get_changed_fields(original, modified)
    
    if not changes:
        console.print("[green]✓ No changes detected[/green]")
        return
    
    console.print(f"\n[bold]Changed fields ({len(changes)}):[/bold]")
    for change in changes:
        if change.startswith('+'):
            console.print(f"  [green]{change}[/green]")
        elif change.startswith('-'):
            console.print(f"  [red]{change}[/red]")
        else:
            console.print(f"  [yellow]{change}[/yellow]")