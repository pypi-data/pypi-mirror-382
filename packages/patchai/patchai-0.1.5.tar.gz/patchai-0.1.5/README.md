# PatchAI ✨

**AI-powered structured file editor with beautiful diff visualization**

PatchAI lets you edit JSON, YAML, and config files using natural language instructions. Perfect for fixing OCR errors, cleaning up data, or making bulk changes across structured documents.

## ✨ Features

- **Natural Language Editing** - Just describe what you want to change
- **Visual Diff** - See exactly what changed with beautiful unified or side-by-side diffs
- **Image-Aware** - Compare JSON/YAML with original document images to fix OCR errors
- **Undo/Reset** - Full history tracking with easy undo
- **Rich CLI** - Beautiful terminal interface with colors and panels
- **Simple API** - 3 lines of code to get started

## 🚀 Quick Start

### Installation

```bash
# Basic installation (no LLM provider)
pip install patchai

# With specific provider
pip install patchai[gemini]     # Google Gemini
pip install patchai[openai]     # OpenAI GPT
pip install patchai[anthropic]  # Anthropic Claude

# With all providers
pip install patchai[all-providers]

# With Jupyter support
pip install patchai[jupyter,gemini]
```

### Basic Usage

**Python API:**
```python
from patchai import PatchAI

# Using Gemini (default)
editor = PatchAI("data.json", provider="gemini", api_key="your-key")
editor.edit("Fix all typos and remove extra newlines")
editor.save("fixed.json")

# Using OpenAI
editor = PatchAI("data.json", provider="openai", api_key="your-key", model="gpt-4o")
editor.edit("Fix all typos")
editor.save("fixed.json")

# Using Anthropic Claude
editor = PatchAI("data.json", provider="anthropic", api_key="your-key", model="claude-sonnet-4-20250514")
editor.edit("Fix all typos")
editor.save("fixed.json")
```

**Command Line:**
```bash
# Gemini (default)
export GEMINI_API_KEY="your-key"
patchai data.json -e "Fix all typos"

# OpenAI
export OPENAI_API_KEY="your-key"
patchai data.json --provider openai --model gpt-4o -e "Fix all typos"

# Anthropic
export ANTHROPIC_API_KEY="your-key"
patchai data.json --provider anthropic --model claude-sonnet-4-20250514 -e "Fix all typos"
```

## 📖 Examples

### Fix OCR Errors with Image Reference

```python
from patchai import PatchAI

# Load JSON with reference image
editor = PatchAI(
    data="extracted.json",
    image_path="original_document.jpg"
)

# AI compares JSON with image and fixes errors
editor.edit("Compare the JSON with the document image and correct any OCR errors")

# Show what changed
from patchai import print_diff
print_diff(editor.get_original(), editor.get_current())

# Save
editor.save("corrected.json")
```

### Edit YAML Config

```python
from patchai import PatchAI

editor = PatchAI("config.yaml", format="yaml")
editor.edit("Update database host to localhost and change port to 5432")
editor.save("config.yaml")
```

### Interactive Editing Session

```python
from patchai import PatchAI

editor = PatchAI("data.json")

# Make multiple edits
editor.edit("Remove all empty strings")
editor.edit("Add newlines after periods in the text field")
editor.edit("Fix capitalization in headers")

# Undo last change if needed
editor.undo()

# Check if anything changed
if editor.has_changes:
    editor.save("cleaned.json")
```

### Batch Processing

```python
from patchai import PatchAI
from pathlib import Path

# Process multiple files
files = Path("data/").glob("*.json")

for file in files:
    editor = PatchAI(file)
    editor.edit("Standardize date format to YYYY-MM-DD")
    editor.save(file)
    print(f"✓ Processed {file}")
```

## 🎨 CLI Examples

### Interactive Mode

```bash
patchai data.json
```

You'll see:
```
┌─ PatchAI Interactive Mode ────────────────────────┐
│                                                    │
│ Commands:                                          │
│   • Type instruction to edit                       │
│   • 'undo' - undo last edit                       │
│   • 'reset' - reset to original                   │
│   • 'save' - save and exit                        │
│   • 'quit' - exit without saving                  │
│   • 'diff' - show current changes                 │
│                                                    │
└────────────────────────────────────────────────────┘

Instruction: Fix all typos in the header
```

### Single Edit Mode

```bash
# Basic edit
patchai data.json -e "Clean up formatting"

# With image reference
patchai extracted.json \
  --image document.jpg \
  -e "Compare with image and fix OCR errors"

# YAML file
patchai config.yaml \
  --format yaml \
  -e "Update production database credentials"

# Save to new file
patchai data.json \
  -e "Remove all null values" \
  -o cleaned.json

# Side-by-side diff
patchai data.json \
  -e "Fix all dates" \
  --diff side-by-side
```

## 🔧 Advanced Usage

### Custom Model

```python
from patchai import PatchAI

editor = PatchAI(
    "data.json",
    model="gemini-2.0-flash",  # or gemini-2.0-flash-thinking-exp
    api_key="your-api-key"     # or set GEMINI_API_KEY env var
)
```

### Programmatic Diff Analysis

```python
from patchai import PatchAI, print_diff, print_summary, generate_unified_diff

editor = PatchAI("data.json")
original = editor.get_original()

editor.edit("Your instruction here")
modified = editor.get_current()

# Print colored diff
print_diff(original, modified, style="unified")

# Print summary of changes
print_summary(original, modified)

# Get diff as string
diff_text = generate_unified_diff(original, modified)
```

### History Tracking

```python
editor = PatchAI("data.json")

# Make multiple edits
editor.edit("Fix typos")
editor.edit("Remove newlines")
editor.edit("Update dates")

# Access edit history
for i, edit in enumerate(editor.edit_history):
    print(f"{i+1}. {edit['instruction']}")

# Undo multiple times
editor.undo()  # undo "Update dates"
editor.undo()  # undo "Remove newlines"

# Reset to original
editor.reset()
```

## 🎯 Use Cases

### 📄 Document Processing
- Fix OCR extraction errors by comparing JSON output with original document images
- Clean up formatting in extracted data
- Standardize field values across documents

### ⚙️ Configuration Management  
- Update config files across multiple environments
- Fix formatting issues in YAML/JSON configs
- Bulk update values (URLs, API keys, ports)

### 🔧 Data Cleaning
- Remove null/empty values
- Standardize date formats
- Fix typos across structured data
- Normalize field values

### 📊 Data Transformation
- Restructure nested JSON
- Move values between fields
- Split/merge fields based on natural language instructions

## 🧪 Jupyter Notebook Support

```python
from patchai import PatchAI

editor = PatchAI("data.json", image_path="doc.jpg")

# Edit
editor.edit("Fix all OCR errors")

# Beautiful diff in notebook
from patchai import print_diff
print_diff(editor.get_original(), editor.get_current(), style="side-by-side")
```

## 💬 Interactive Jupyter Editor (Widget UI)
PatchAI also includes a fully interactive **Jupyter/Colab editor** — a beautiful, two-panel interface that lets you edit JSON or YAML files using natural language instructions, with live diffs and undo support.

```python
from patchai.jupyter import create_jupyter_editor

# Launch interactive editor
create_jupyter_editor("data.json", image_path="document.jpg")
```

## 🛡️ API Reference

### PatchAI

```python
PatchAI(
    data: Union[Dict, str, Path],
    format: str = "json",
    image_path: Optional[Union[str, Path]] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash-exp"
)
```

**Parameters:**
- `data`: Input data as dict, JSON/YAML string, or file path
- `format`: File format (`"json"` or `"yaml"`)
- `image_path`: Optional reference image for visual comparison
- `api_key`: Gemini API key (or set `GEMINI_API_KEY` env var)
- `model`: Gemini model to use

**Methods:**
- `edit(instruction: str, include_image: bool = True) -> Dict` - Apply edit instruction
- `undo() -> bool` - Undo last edit
- `reset()` - Reset to original data
- `save(path: Union[str, Path])` - Save to file
- `get_current() -> Dict` - Get current data
- `get_original() -> Dict` - Get original data

**Properties:**
- `has_changes: bool` - Check if data has been modified
- `history: List[Dict]` - Edit history
- `edit_history: List[Dict]` - Instruction history

## 🔐 Environment Variables

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"
```

Get your free API key at: [https://ai.google.dev](https://ai.google.dev)

## 📦 Project Structure

```
patchai/
├── src/patchai/
│   ├── __init__.py      # Main exports
│   ├── editor.py        # Core PatchAI class
│   ├── diff.py          # Diff utilities
│   └── cli.py           # Command-line interface
│   └── jupyter.py        
├── tests/               # Unit tests
├── examples/            # Example scripts
├── pyproject.toml       # Package configuration
└── README.md
```

## 🤝 Contributing

Contributions welcome! Ideas for improvement:

- [ ] Support for more formats (TOML, XML, CSV)
- [ ] Web UI for non-technical users
- [ ] Batch operation commands
- [ ] Custom validation rules
- [ ] PDF form field editing
- [ ] Excel/DOCX simple edits

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with:
- [Google Gemini](https://ai.google.dev) - AI editing engine
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [PyYAML](https://pyyaml.org) - YAML parsing

## 💡 Tips

1. **Be specific**: "Fix typos in the 'description' field" works better than "fix everything"
2. **Use image reference**: When fixing OCR errors, always include the original image
3. **Check diffs**: Always review changes before saving
4. **Start small**: Test on a copy before editing important files

## 📚 More Examples

Check out the [examples/](examples/) directory for:
- OCR error correction workflow
- Batch config file updates
- Data cleaning pipelines
- YAML configuration management

## 🔗 Links

- **Documentation**: [https://github.com/davidkjeremiah/patchai](https://github.com/davidkjeremiah/patchai)
- **Issues**: [https://github.com/davidkjeremiah/patchai/issues](https://github.com/davidkjeremiah/patchai/issues)
- **PyPI**: [https://pypi.org/project/patchai](https://pypi.org/project/patchai)

---

**Made with ❤️ by developers who hate manual data cleaning**