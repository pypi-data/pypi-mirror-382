"""
Interactive Jupyter/Colab UI for PatchAI.

This provides the beautiful widget-based interface from your original code.
"""

try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output, Image
    HAS_JUPYTER = True
except ImportError:
    HAS_JUPYTER = False

import json
import difflib
from pathlib import Path
from typing import Optional, Union
from .editor import PatchAI


class JupyterEditor:
    """Interactive Jupyter interface for PatchAI."""
    
    def __init__(
        self, 
        data: Union[dict, str, Path],
        format: str = "json",
        image_path: Optional[Union[str, Path]] = None,
        api_key: Optional[str] = None
    ):
        """
        Create interactive Jupyter editor.
        
        Args:
            data: Input data (dict, file path, or JSON string)
            format: Data format ('json' or 'yaml')
            image_path: Optional reference image
            api_key: Gemini API key
        """
        if not HAS_JUPYTER:
            raise ImportError(
                "Jupyter UI requires ipywidgets and IPython.\n"
                "Install with: pip install patchai[jupyter]"
            )
        
        self.editor = PatchAI(data, format=format, image_path=image_path, api_key=api_key)
        self.image_path = Path(image_path) if image_path else None
        
        # Create UI components
        self._create_widgets()
        self._show_initial_view()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Instruction input
        self.instruction_input = widgets.Textarea(
            value='Compare the JSON with the document image and correct any formatting errors.',
            placeholder='Type your instruction here...',
            description='',
            layout=widgets.Layout(width='100%', height='80px')
        )
        
        # Buttons
        self.send_button = widgets.Button(
            description="🚀 Send", 
            button_style="primary",
            tooltip="Apply edit instruction"
        )
        self.undo_button = widgets.Button(
            description="↩️ Undo", 
            button_style="warning",
            tooltip="Undo last edit"
        )
        self.reset_button = widgets.Button(
            description="🔄 Reset", 
            button_style="danger",
            tooltip="Reset to original"
        )
        self.save_button = widgets.Button(
            description="💾 Save", 
            button_style="success",
            tooltip="Save to file"
        )
        
        # Options
        self.include_image_checkbox = widgets.Checkbox(
            value=True,
            description='Include image in request',
            indent=False
        )
        
        self.diff_style_dropdown = widgets.Dropdown(
            options=[('Unified', 'unified'), ('Side-by-Side', 'side-by-side')],
            value='unified',
            description='Diff view:',
            style={'description_width': 'auto'}
        )
        
        self.output_area = widgets.Output()
        
        # Connect event handlers
        self.send_button.on_click(self._on_send)
        self.undo_button.on_click(self._on_undo)
        self.reset_button.on_click(self._on_reset)
        self.save_button.on_click(self._on_save)

    def _show_initial_view(self):
        """Display initial view with image and JSON side-by-side."""
        with self.output_area:
            clear_output()
            print("📊 Initial State\n")
            
            # Create side-by-side layout
            left_output = widgets.Output(layout=widgets.Layout(width='50%', padding='10px'))
            right_output = widgets.Output(layout=widgets.Layout(width='50%', padding='10px'))
            
            # Left side - Image
            with left_output:
                print("📷 Original Document")
                print("-" * 40)
                if self.image_path and self.image_path.exists():
                    display(Image(filename=str(self.image_path)))
                else:
                    print("⚠️ No image available")
            
            # Right side - JSON
            with right_output:
                print("📄 Current JSON")
                print("-" * 40)
                json_str = json.dumps(self.editor.get_current(), indent=2)
                html = [
                    '<div style="font-family: monospace; font-size: 12px; '
                    'white-space: pre-wrap; word-wrap: break-word; color: #000; '
                    'max-height: 600px; overflow-y: auto;">'
                ]
                for line in json_str.splitlines():
                    html.append(f'<div>{line}</div>')
                html.append('</div>')
                display(HTML(''.join(html)))
            
            # Display side by side
            display(widgets.HBox([left_output, right_output], layout=widgets.Layout(width='100%')))
    
    def _on_send(self, b):
        """Handle send button click."""
        with self.output_area:
            clear_output(wait=True)
            instruction = self.instruction_input.value.strip()
            
            if not instruction:
                print("⚠️ Please enter an instruction")
                return
            
            print(f"💬 You: {instruction}")
            print("\n🔄 Processing...\n")
            
            # Store previous state for diff
            previous_data = self.editor.get_current()
            
            # Make edit
            try:
                self.editor.edit(instruction, include_image=self.include_image_checkbox.value)
                current_data = self.editor.get_current()
                
                # Check if there are changes
                if previous_data != current_data:
                    print("📝 Changes made:\n")
                    
                    # Show diff based on selected style
                    if self.diff_style_dropdown.value == 'side-by-side':
                        self._show_side_by_side_diff(previous_data, current_data)
                    else:
                        diff = self._generate_unified_diff(previous_data, current_data)
                        self._show_compact_diff(diff)
                else:
                    print("✅ No changes needed or no changes detected")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "="*60)
    
    def _on_undo(self, b):
        """Handle undo button click."""
        with self.output_area:
            clear_output(wait=True)
            if self.editor.undo():
                print("↩️ Undone last change")
                print("\nCurrent state:")
                print(json.dumps(self.editor.get_current(), indent=2)[:500] + "...")
            else:
                print("⚠️ Nothing to undo")
    
    def _on_reset(self, b):
        """Handle reset button click."""
        with self.output_area:
            clear_output(wait=True)
            self.editor.reset()
            print("🔄 Reset to original JSON")
    
    def _on_save(self, b):
        """Handle save button click."""
        with self.output_area:
            clear_output(wait=True)
            self.editor.save('corrected_output.json')
            print("💾 Saved to 'corrected_output.json'")

    def _generate_unified_diff(self, original, modified):
        """Generate unified diff."""
        original_str = json.dumps(original, indent=2)
        modified_str = json.dumps(modified, indent=2)
        
        diff = difflib.unified_diff(
            original_str.splitlines(keepends=True),
            modified_str.splitlines(keepends=True),
            fromfile='before',
            tofile='after',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _show_compact_diff(self, diff_text):
        """Display unified diff with color coding."""
        html_lines = [
            '<div style="font-family: monospace; font-size: 12px; '
            'white-space: pre-wrap; word-wrap: break-word; '
            'max-width: 100%; overflow-wrap: break-word;">'
        ]
        
        for line in diff_text.split('\n'):
            if line.startswith('+++') or line.startswith('---'):
                html_lines.append(f'<span style="color: #666; font-weight: bold;">{line}</span>')
            elif line.startswith('@@'):
                html_lines.append(f'<span style="color: #0969da; font-weight: bold;">{line}</span>')
            elif line.startswith('+'):
                html_lines.append(f'<span style="background-color: #d1f0d1; color: #0a6e0a;">{line}</span>')
            elif line.startswith('-'):
                html_lines.append(f'<span style="background-color: #ffd7d5; color: #d1242f;">{line}</span>')
            else:
                html_lines.append(f'<span style="color: #333;">{line}</span>')
        
        html_lines.append('</div>')
        display(HTML('\n'.join(html_lines)))
    
    def _show_side_by_side_diff(self, original, modified):
        """Display side-by-side diff with color coding."""
        original_str = json.dumps(original, indent=2)
        modified_str = json.dumps(modified, indent=2)
        
        original_lines = original_str.splitlines()
        modified_lines = modified_str.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)
        
        html = [
            '<div style="display: flex; gap: 10px; font-family: monospace; '
            'font-size: 12px; max-width: 100%;">'
        ]
        
        # Left side (Original - Red)
        html.append(
            '<div style="flex: 1; border: 1px solid #ddd; padding: 10px; '
            'background-color: #fff; overflow-x: auto;">'
        )
        html.append('<div style="font-weight: bold; margin-bottom: 10px; color: #d1242f;">📄 Original (Before)</div>')
        html.append('<div style="white-space: pre-wrap; word-wrap: break-word;">')
        
        # Right side (Modified - Green)
        right_html = [
            '<div style="flex: 1; border: 1px solid #ddd; padding: 10px; '
            'background-color: #fff; overflow-x: auto;">'
        ]
        right_html.append('<div style="font-weight: bold; margin-bottom: 10px; color: #0a6e0a;">✅ Modified (After)</div>')
        right_html.append('<div style="white-space: pre-wrap; word-wrap: break-word;">')
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="color: #333;">{line}</div>')
                for line in modified_lines[j1:j2]:
                    right_html.append(f'<div style="color: #333;">{line}</div>')
            
            elif tag == 'delete':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="background-color: #ffd7d5; color: #d1242f;">- {line}</div>')
            
            elif tag == 'insert':
                for line in modified_lines[j1:j2]:
                    right_html.append(f'<div style="background-color: #d1f0d1; color: #0a6e0a;">+ {line}</div>')
            
            elif tag == 'replace':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="background-color: #ffd7d5; color: #d1242f;">- {line}</div>')
                for line in modified_lines[j1:j2]:
                    right_html.append(f'<div style="background-color: #d1f0d1; color: #0a6e0a;">+ {line}</div>')
        
        html.append('</div></div>')
        right_html.append('</div></div>')
        html.append(''.join(right_html))
        html.append('</div>')
        
        display(HTML(''.join(html)))
    
    def show(self):
        """Display the interactive UI."""
        print("🎯 JSON EDITOR WITH CONVERSATIONAL INTERFACE")
        print("="*60)
        print("\nType instructions naturally, like:")
        print("  • 'Add a newline after the phrase \"See table 13\"'")
        print("  • 'Remove the newline in the header'")
        print("  • 'Fix the Page footer'")
        print("  • 'Compare with image and fix all errors'")
        print("\n" + "="*60 + "\n")
        
        display(widgets.VBox([
            widgets.Label("💬 Your instruction:"),
            self.instruction_input,
            widgets.HBox([
                self.send_button, 
                self.undo_button, 
                self.reset_button, 
                self.save_button
            ]),
            widgets.HBox([
                self.include_image_checkbox, 
                self.diff_style_dropdown
            ]),
            self.output_area
        ]))


# Convenience function
def create_jupyter_editor(
    data: Union[dict, str, Path],
    format: str = "json",
    image_path: Optional[Union[str, Path]] = None,
    api_key: Optional[str] = None
):
    """
    Create and display interactive Jupyter editor.
    
    Example:
        >>> from patchai.jupyter import create_jupyter_editor
        >>> editor = create_jupyter_editor("data.json", image_path="doc.jpg")
    """
    editor = JupyterEditor(data, format, image_path, api_key)
    editor.show()
    return editor