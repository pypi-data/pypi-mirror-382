# PatchAI Provider Guide

PatchAI is **model-agnostic** and works with any LLM provider. Here's how to use different providers:

## 🎯 Quick Start by Provider

### Google Gemini (Default)

```bash
# Install
pip install patchai[gemini]

# Set API key
export GEMINI_API_KEY="your-key-here"  # Linux/Mac
$env:GEMINI_API_KEY = "your-key"       # Windows PowerShell

# Use it
patchai data.json -e "Fix all typos"
```

**Python:**
```python
from patchai import PatchAI

editor = PatchAI(
    "data.json",
    provider="gemini",
    api_key="your-key",
    model="gemini-2.0-flash-exp"  # default
)
```

**Get API Key:** https://ai.google.dev

**Models:**
- `gemini-2.0-flash-exp` (default, fastest)
- `gemini-2.0-flash`
- `gemini-pro-vision` (for images)

---

### OpenAI GPT

```bash
# Install
pip install patchai[openai]

# Set API key
export OPENAI_API_KEY="your-key-here"

# Use it
patchai data.json --provider openai --model gpt-4o -e "Fix typos"
```

**Python:**
```python
from patchai import PatchAI

editor = PatchAI(
    "data.json",
    provider="openai",
    api_key="your-key",
    model="gpt-4o"
)
```

**Get API Key:** https://platform.openai.com/api-keys

**Models:**
- `gpt-4o` (vision support)
- `gpt-4o-mini` (faster, cheaper)
- `gpt-4-turbo`
- `o1-preview` (reasoning)

---

### Anthropic Claude

```bash
# Install
pip install patchai[anthropic]

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Use it
patchai data.json --provider anthropic --model claude-sonnet-4-20250514 -e "Fix typos"
```

**Python:**
```python
from patchai import PatchAI

editor = PatchAI(
    "data.json",
    provider="anthropic",
    api_key="your-key",
    model="claude-sonnet-4-20250514"
)
```

**Get API Key:** https://console.anthropic.com/

**Models:**
- `claude-sonnet-4-20250514` (balanced)
- `claude-opus-4-20250514` (most capable)
- `claude-haiku-3-5-20241022` (fastest)

---

### Custom LLM Function

Use **any** LLM by providing your own function:

```python
from patchai import PatchAI

def my_llm_function(prompt: str, image_bytes: bytes = None) -> str:
    """
    Call your custom LLM.
    
    Args:
        prompt: Complete prompt with instructions and data
        image_bytes: Optional image (JPEG format)
        
    Returns:
        Edited JSON/YAML as string
    """
    # Your LLM call here
    # Could be: local model, custom API, HuggingFace, etc.
    
    response = your_llm_api.generate(prompt)
    return response

editor = PatchAI("data.json", llm_function=my_llm_function)
```

**Examples:**
- Local models (Ollama, LM Studio)
- HuggingFace models
- Azure OpenAI
- Custom fine-tuned models
- Any API endpoint

---

### Local Models (Ollama)

```python
from patchai import PatchAI
import requests

def ollama_llm(prompt: str, image_bytes: bytes = None) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

editor = PatchAI("data.json", llm_function=ollama_llm)
```

**Setup:**
1. Install Ollama: https://ollama.ai/
2. Run model: `ollama run llama3.2`
3. Use PatchAI with custom function

---

## 📊 Provider Comparison

| Provider | Best For | Vision Support | Cost | Speed |
|----------|----------|----------------|------|-------|
| **Gemini** | General use, free tier | ✅ Yes | 💰 Free tier available | ⚡ Very fast |
| **OpenAI** | High quality, reliability | ✅ Yes (gpt-4o) | 💰💰 Pay per token | ⚡⚡ Fast |
| **Anthropic** | Long context, accuracy | ✅ Yes | 💰💰 Pay per token | ⚡⚡ Fast |
| **Custom/Local** | Privacy, no cost | Depends | 💰 Free (hardware cost) | ⚡ Varies |

---

## 🔑 Setting API Keys

### Option 1: Environment Variables (Recommended)

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-key"
$env:OPENAI_API_KEY = "your-key"
$env:ANTHROPIC_API_KEY = "your-key"
```

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=your-key
set OPENAI_API_KEY=your-key
set ANTHROPIC_API_KEY=your-key
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

**Permanent (add to profile):**
```bash
# Linux/Mac: Add to ~/.bashrc or ~/.zshrc
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc

# Windows: Use System Environment Variables
# Search "Environment Variables" → Edit → New
```

### Option 2: Pass Directly in Code

```python
editor = PatchAI(
    "data.json",
    provider="openai",
    api_key="sk-..."  # Not recommended for production
)
```

### Option 3: CLI Argument

```bash
patchai data.json --provider openai --api-key "sk-..." -e "Edit"
```

---

## 🖼️ Image Support

All major providers support image-aware editing:

```python
editor = PatchAI(
    "extracted.json",
    provider="gemini",  # or "openai", "anthropic"
    image_path="original_document.jpg"
)

editor.edit("Compare JSON with image and fix OCR errors")
```

**Provider Image Capabilities:**
- ✅ Gemini: All vision models
- ✅ OpenAI: `gpt-4o`, `gpt-4-turbo`, `gpt-4-vision-preview`
- ✅ Anthropic: All Claude 3+ models
- ⚠️ Custom: Depends on your implementation

---

## 💡 Tips & Best Practices

### 1. Use Environment Variables
```bash
# Good - secure, reusable
export GEMINI_API_KEY="..."
patchai data.json -e "Edit"

# Bad - key in command history
patchai data.json --api-key "..." -e "Edit"
```

### 2. Choose the Right Model

**For speed:** Use default models
```python
# Gemini: gemini-2.0-flash-exp
# OpenAI: gpt-4o-mini
# Anthropic: claude-haiku-3-5-20241022
```

**For quality:** Use premium models
```python
# Gemini: gemini-pro-vision
# OpenAI: gpt-4o
# Anthropic: claude-opus-4-20250514
```

### 3. Install Only What You Need

```bash
# Just Gemini
pip install patchai[gemini]

# All providers
pip install patchai[all-providers]

# With Jupyter
pip install patchai[gemini,jupyter]
```

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Install missing provider
pip install patchai[gemini]    # or [openai] or [anthropic]
```

### "API key not found"

```bash
# Check environment variable is set
echo $GEMINI_API_KEY           # Linux/Mac
echo %GEMINI_API_KEY%          # Windows cmd
echo $env:GEMINI_API_KEY       # Windows PowerShell
```

### Rate limits or errors

```python
# Add retry logic in custom function
def resilient_llm(prompt, image=None):
    import time
    for attempt in range(3):
        try:
            return your_llm_call(prompt)
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise

editor = PatchAI("data.json", llm_function=resilient_llm)
```

---

## 📚 More Examples

See `examples/multi_provider_usage.py` for complete working examples with all providers.

---

## 🆘 Need Help?

- **Issues:** https://github.com/davidkjeremiah/patchai/issues