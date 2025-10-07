"""Command-line interface for PatchAI."""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from .editor import PatchAI
from .diff import print_diff, print_summary


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PatchAI - AI-powered structured file editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  patchai data.json
  
  # Single edit
  patchai data.json -e "Fix all typos"
  
  # With reference image
  patchai data.json -e "Compare with image and fix errors" --image doc.jpg
  
  # YAML file
  patchai config.yaml --format yaml -e "Update database host to localhost"
  
  # Save to new file
  patchai data.json -e "Clean up formatting" -o clean.json
  
  # Use OpenAI
  patchai data.json --provider openai --model gpt-4o -e "Fix typos"
        """
    )
    
    parser.add_argument(
        "file",
        type=Path,
        help="Input file to edit (JSON or YAML)"
    )
    
    parser.add_argument(
        "-e", "--edit",
        type=str,
        help="Edit instruction (if not provided, enters interactive mode)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: overwrites input)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "yaml"],
        help="File format (auto-detected from extension if not specified)"
    )
    
    parser.add_argument(
        "--image",
        type=Path,
        help="Reference image for visual comparison"
    )
    
    parser.add_argument(
        "--diff",
        type=str,
        choices=["unified", "side-by-side"],
        default="unified",
        help="Diff visualization style"
    )
    
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Don't include image in AI request (faster)"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini", "openai", "anthropic"],
        default="gemini",
        help="LLM provider to use"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Model name (provider-specific, e.g., 'gpt-4o', 'claude-sonnet-4-20250514', 'gemini-2.0-flash-exp')"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for LLM provider (or set via environment variable: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)"
    )
    
    args = parser.parse_args()
    
    console = Console()
    
    # Validate input file
    if not args.file.exists():
        console.print(f"[red]Error: File not found: {args.file}[/red]")
        sys.exit(1)
    
    # Auto-detect format
    if not args.format:
        if args.file.suffix == ".json":
            args.format = "json"
        elif args.file.suffix in [".yaml", ".yml"]:
            args.format = "yaml"
        else:
            console.print("[red]Error: Could not detect format. Use --format[/red]")
            sys.exit(1)
    
    try:
        # Initialize editor
        console.print(f"[cyan]Loading {args.file}...[/cyan]")
        editor = PatchAI(
            data=args.file,
            format=args.format,
            image_path=args.image,
            api_key=args.api_key,
            model=args.model,
            provider=args.provider
        )
        
        if args.edit:
            # Single edit mode
            _run_single_edit(editor, args, console)
        else:
            # Interactive mode
            _run_interactive(editor, args, console)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _run_single_edit(editor: PatchAI, args, console: Console):
    """Run single edit and save."""
    console.print(f"\n[cyan]Instruction:[/cyan] {args.edit}\n")
    console.print("[yellow]Processing...[/yellow]")
    
    original = editor.get_original()
    
    try:
        editor.edit(args.edit, include_image=not args.no_image)
        
        # Show changes
        console.print()
        print_diff(original, editor.get_current(), editor.format, args.diff)
        print_summary(original, editor.get_current())
        
        # Save
        output_path = args.output or args.file
        editor.save(output_path)
        console.print(f"\n[green]✓ Saved to {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Edit failed: {e}[/red]")
        sys.exit(1)


def _run_interactive(editor: PatchAI, args, console: Console):
    """Run interactive editing session."""
    console.print(Panel.fit(
        "[bold cyan]PatchAI Interactive Mode[/bold cyan]\n\n"
        "Commands:\n"
        "  • Type instruction to edit\n"
        "  • 'undo' - undo last edit\n"
        "  • 'reset' - reset to original\n"
        "  • 'save' - save and exit\n"
        "  • 'quit' - exit without saving\n"
        "  • 'diff' - show current changes",
        border_style="cyan"
    ))
    
    while True:
        try:
            instruction = Prompt.ask("\n[cyan]Instruction[/cyan]").strip()
            
            if not instruction:
                continue
                
            instruction_lower = instruction.lower()
            
            if instruction_lower == "quit":
                if editor.has_changes:
                    if Confirm.ask("You have unsaved changes. Quit anyway?"):
                        console.print("[yellow]Exiting without saving[/yellow]")
                        break
                else:
                    break
                    
            elif instruction_lower == "save":
                output_path = args.output or args.file
                editor.save(output_path)
                console.print(f"[green]✓ Saved to {output_path}[/green]")
                break
                
            elif instruction_lower == "undo":
                if editor.undo():
                    console.print("[green]✓ Undone[/green]")
                else:
                    console.print("[yellow]Nothing to undo[/yellow]")
                    
            elif instruction_lower == "reset":
                if Confirm.ask("Reset all changes?"):
                    editor.reset()
                    console.print("[green]✓ Reset to original[/green]")
                    
            elif instruction_lower == "diff":
                print_diff(editor.get_original(), editor.get_current(), editor.format, args.diff)
                print_summary(editor.get_original(), editor.get_current())
                
            else:
                # Execute edit
                console.print("[yellow]Processing...[/yellow]")
                original = editor.get_current()
                
                try:
                    editor.edit(instruction, include_image=not args.no_image)
                    console.print()
                    print_diff(original, editor.get_current(), editor.format, args.diff)
                    print_summary(original, editor.get_current())
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()