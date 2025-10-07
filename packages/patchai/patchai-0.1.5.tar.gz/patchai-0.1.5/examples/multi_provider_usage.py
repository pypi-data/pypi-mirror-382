"""
PatchAI with Multiple LLM Providers

This example shows how to use PatchAI with different LLM providers:
- Google Gemini
- OpenAI GPT
- Anthropic Claude
- Custom LLM function
"""

import os
from patchai import PatchAI

# Sample data for testing
sample_data = {
    "name": "john doe",
    "email": "JOHN@EXAMPLE.COM",
    "status": "active"
}


# ============================================
# Example 1: Google Gemini (Default)
# ============================================
def example_gemini():
    """Use Google Gemini."""
    print("\n" + "="*60)
    print("Example 1: Google Gemini")
    print("="*60)
    
    # Set API key
    api_key = os.getenv("GEMINI_API_KEY", "your-gemini-key-here")
    
    # Create editor
    editor = PatchAI(
        sample_data,
        provider="gemini",
        api_key=api_key,
        model="gemini-2.0-flash-exp"  # or "gemini-2.0-flash", "gemini-pro-vision"
    )
    
    # Edit
    print("\nInstruction: Capitalize name and lowercase email")
    editor.edit("Capitalize the name and lowercase the email")
    
    print("\nResult:")
    print(editor.get_current())


# ============================================
# Example 2: OpenAI GPT
# ============================================
def example_openai():
    """Use OpenAI GPT models."""
    print("\n" + "="*60)
    print("Example 2: OpenAI GPT")
    print("="*60)
    
    # Set API key
    api_key = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
    
    # Create editor
    editor = PatchAI(
        sample_data,
        provider="openai",
        api_key=api_key,
        model="gpt-4o"  # or "gpt-4o-mini", "gpt-4-turbo"
    )
    
    # Edit
    print("\nInstruction: Capitalize name and lowercase email")
    editor.edit("Capitalize the name and lowercase the email")
    
    print("\nResult:")
    print(editor.get_current())


# ============================================
# Example 3: Anthropic Claude
# ============================================
def example_anthropic():
    """Use Anthropic Claude models."""
    print("\n" + "="*60)
    print("Example 3: Anthropic Claude")
    print("="*60)
    
    # Set API key
    api_key = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key-here")
    
    # Create editor
    editor = PatchAI(
        sample_data,
        provider="anthropic",
        api_key=api_key,
        model="claude-sonnet-4-20250514"  # or "claude-opus-4-20250514"
    )
    
    # Edit
    print("\nInstruction: Capitalize name and lowercase email")
    editor.edit("Capitalize the name and lowercase the email")
    
    print("\nResult:")
    print(editor.get_current())


# ============================================
# Example 4: Custom LLM Function
# ============================================
def example_custom_llm():
    """Use a custom LLM function."""
    print("\n" + "="*60)
    print("Example 4: Custom LLM Function")
    print("="*60)
    
    # Define custom LLM function
    def my_custom_llm(prompt: str, image_bytes: bytes = None) -> str:
        """
        Custom LLM function - could be local model, custom API, etc.
        
        Args:
            prompt: Full prompt with system instructions and user request
            image_bytes: Optional image data (JPEG bytes)
            
        Returns:
            Edited JSON as string (with or without code fences)
        """
        # For demonstration, we'll use a simple rule-based approach
        # In real usage, you'd call your LLM here
        
        print("  [Custom LLM called with prompt length:", len(prompt), "bytes]")
        
        # Simple demo: return modified JSON
        # In reality, you'd call your LLM here
        return '''```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "status": "active"
}
```'''
    
    # Create editor with custom function
    editor = PatchAI(
        sample_data,
        llm_function=my_custom_llm
    )
    
    # Edit
    print("\nInstruction: Capitalize name and lowercase email")
    editor.edit("Capitalize the name and lowercase email")
    
    print("\nResult:")
    print(editor.get_current())


# ============================================
# Example 5: Local Model (Ollama)
# ============================================
def example_ollama():
    """Use local Ollama model."""
    print("\n" + "="*60)
    print("Example 5: Local Ollama Model")
    print("="*60)
    
    def ollama_llm(prompt: str, image_bytes: bytes = None) -> str:
        """Call local Ollama model."""
        try:
            import requests
        except ImportError:
            print("  Install requests: pip install requests")
            return ""
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",  # or "mistral", "codellama", etc.
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return ""
    
    # Create editor
    editor = PatchAI(
        sample_data,
        llm_function=ollama_llm
    )
    
    print("\nNote: This requires Ollama running locally")
    print("Install: https://ollama.ai/")
    print("Run: ollama run llama3.2")


# ============================================
# Example 6: With Image Reference
# ============================================
def example_with_image():
    """Use any provider with image reference."""
    print("\n" + "="*60)
    print("Example 6: Image-Aware Editing")
    print("="*60)
    
    ocr_data = {
        "Page header": "17",
        "Page text": "Table5.-Sourcesand FrequencyofScience Information",
        "Page footer": ""
    }
    
    # Works with any provider that supports vision
    editor = PatchAI(
        ocr_data,
        provider="gemini",  # or "openai" with gpt-4o, "anthropic" with claude
        api_key=os.getenv("GEMINI_API_KEY"),
        image_path="document.jpg"  # Reference image
    )
    
    print("\nInstruction: Compare with image and fix OCR spacing errors")
    editor.edit("Compare the JSON with the document image and fix spacing errors")
    
    print("\nResult:")
    print(editor.get_current())


# ============================================
# Example 7: Environment Variables
# ============================================
def example_env_vars():
    """Use environment variables for API keys."""
    print("\n" + "="*60)
    print("Example 7: Using Environment Variables")
    print("="*60)
    
    print("""
Set environment variables:

Windows (PowerShell):
  $env:GEMINI_API_KEY = "your-key"
  $env:OPENAI_API_KEY = "your-key"
  $env:ANTHROPIC_API_KEY = "your-key"

Windows (cmd):
  set GEMINI_API_KEY=your-key
  set OPENAI_API_KEY=your-key
  set ANTHROPIC_API_KEY=your-key

Linux/Mac:
  export GEMINI_API_KEY="your-key"
  export OPENAI_API_KEY="your-key"
  export ANTHROPIC_API_KEY="your-key"

Then use PatchAI without api_key parameter:
    """)
    
    # API key automatically picked from environment
    editor = PatchAI(
        sample_data,
        provider="gemini"  # Will use GEMINI_API_KEY env var
    )
    
    print("✓ API key automatically loaded from environment variable")


# ============================================
# Example 8: Provider Comparison
# ============================================
def example_compare_providers():
    """Compare results from different providers."""
    print("\n" + "="*60)
    print("Example 8: Comparing Different Providers")
    print("="*60)
    
    providers = [
        ("gemini", "gemini-2.0-flash-exp", os.getenv("GEMINI_API_KEY")),
        ("openai", "gpt-4o", os.getenv("OPENAI_API_KEY")),
        ("anthropic", "claude-sonnet-4-20250514", os.getenv("ANTHROPIC_API_KEY")),
    ]
    
    instruction = "Capitalize the name and lowercase the email"
    
    for provider, model, api_key in providers:
        if not api_key:
            print(f"\n{provider}: Skipped (no API key)")
            continue
        
        try:
            print(f"\n{provider.upper()} ({model}):")
            editor = PatchAI(
                sample_data.copy(),
                provider=provider,
                api_key=api_key,
                model=model
            )
            
            editor.edit(instruction)
            print("  Result:", editor.get_current())
            
        except Exception as e:
            print(f"  Error: {e}")


# ============================================
# Run Examples
# ============================================
if __name__ == "__main__":
    print("\n🚀 PatchAI Multi-Provider Examples")
    print("="*60)
    
    # Check which API keys are available
    print("\nAvailable API keys:")
    print(f"  GEMINI_API_KEY: {'✓' if os.getenv('GEMINI_API_KEY') else '✗'}")
    print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"  ANTHROPIC_API_KEY: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")
    
    print("\nChoose which examples to run:")
    print("1. Google Gemini")
    print("2. OpenAI GPT")
    print("3. Anthropic Claude")
    print("4. Custom LLM Function")
    print("5. Local Ollama Model")
    print("6. Image-Aware Editing")
    print("7. Environment Variables Info")
    print("8. Compare All Providers")
    print("9. Run all examples")
    
    choice = input("\nEnter choice (1-9): ").strip()
    
    examples = {
        "1": example_gemini,
        "2": example_openai,
        "3": example_anthropic,
        "4": example_custom_llm,
        "5": example_ollama,
        "6": example_with_image,
        "7": example_env_vars,
        "8": example_compare_providers,
    }
    
    if choice == "9":
        for example_func in examples.values():
            try:
                example_func()
            except Exception as e:
                print(f"Error: {e}")
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice")
    
    print("\n" + "="*60)
    print("✅ Done!")
    print("="*60)