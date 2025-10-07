"""Core editor for PatchAI - AI-powered structured file editing."""

import json
import re
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class PatchAI:
    """AI-powered editor for structured files (JSON, YAML, configs)."""
    
    SYSTEM_PROMPT = """You are PatchAI, a structured document editor that makes precise edits to JSON/YAML/config files.

Your task:
1. Analyze the current data structure
2. Apply ONLY the requested changes - do not modify other fields
3. Preserve all structure, formatting, and data types
4. Return the complete edited structure

Rules:
- Return valid JSON/YAML with identical keys to the input
- Preserve data types (strings stay strings, numbers stay numbers)
- Only modify values explicitly requested by the user
- If comparing with an image, fix only discrepancies you can verify

Common edit types:
- Text corrections (typos, OCR errors)
- Formatting (add/remove newlines, fix spacing)
- Field moves (move text between header/footer/body)
- Value updates (change specific values)

Return format: Complete JSON object with the same structure, wrapped in ```json``` code block."""

    def __init__(
        self,
        data: Union[Dict, str, Path],
        format: str = "json",
        image_path: Optional[Union[str, Path]] = None,
        llm_function: Optional[Callable] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = "gemini",
    ):
        """
        Initialize PatchAI editor.
        
        Args:
            data: Input data as dict, JSON string, or file path
            format: File format ('json' or 'yaml')
            image_path: Optional reference image for visual comparison
            llm_function: Custom function that takes (prompt, image_bytes) and returns edited text.
                         If provided, overrides provider/api_key/model settings.
            api_key: API key for LLM provider (or set via environment variable)
            model: Model name (provider-specific)
            provider: LLM provider ('gemini', 'openai', 'anthropic', 'custom')
        
        Example with custom function:
            >>> def my_llm(prompt, image_bytes=None):
            ...     # Your custom LLM call here
            ...     return edited_json_string
            >>> editor = PatchAI("data.json", llm_function=my_llm)
        
        Example with providers:
            >>> # Gemini
            >>> editor = PatchAI("data.json", provider="gemini", api_key="...", model="gemini-2.0-flash-exp")
            
            >>> # OpenAI
            >>> editor = PatchAI("data.json", provider="openai", api_key="...", model="gpt-4o")
            
            >>> # Anthropic
            >>> editor = PatchAI("data.json", provider="anthropic", api_key="...", model="claude-sonnet-4-20250514")
        """
        self.format = format.lower()
        self.provider = provider.lower()
        
        # Set up LLM function
        if llm_function:
            self.llm_function = llm_function
        else:
            self.llm_function = self._create_llm_function(provider, api_key, model)
        
        # Load data
        self.original_data = self._load_data(data)
        self.current_data = self._deep_copy(self.original_data)
        
        # History tracking
        self.history: List[Dict] = [self._deep_copy(self.original_data)]
        self.edit_history: List[Dict] = []
        
        # Load image if provided
        self.image_bytes: Optional[bytes] = None
        if image_path:
            image_path = Path(image_path)
            if image_path.exists():
                self.image_bytes = image_path.read_bytes()

    def _create_llm_function(self, provider: str, api_key: Optional[str], model: Optional[str]) -> Callable:
        """Create LLM function based on provider."""
        if provider == "gemini":
            return self._create_gemini_function(api_key, model or "gemini-2.0-flash-exp")
        elif provider == "openai":
            return self._create_openai_function(api_key, model or "gpt-4o")
        elif provider == "anthropic":
            return self._create_anthropic_function(api_key, model or "claude-sonnet-4-20250514")
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                "Use 'gemini', 'openai', 'anthropic', or provide custom llm_function"
            )

    def _create_gemini_function(self, api_key: Optional[str], model: str) -> Callable:
        """Create Gemini LLM function."""
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError(
                "Gemini support requires google-genai. Install with:\n"
                "  pip install google-genai"
            )
        
        client = genai.Client(api_key=api_key)
        
        def gemini_call(prompt: str, image_bytes: Optional[bytes] = None) -> str:
            parts = [types.Part(text=prompt)]
            
            if image_bytes:
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=base64.b64encode(image_bytes).decode('utf-8')
                        )
                    )
                )
            
            response = client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=parts)],
            )
            return response.text
        
        return gemini_call

    def _create_openai_function(self, api_key: Optional[str], model: str) -> Callable:
        """Create OpenAI LLM function."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI support requires openai package. Install with:\n"
                "  pip install openai"
            )
        
        client = OpenAI(api_key=api_key)
        
        def openai_call(prompt: str, image_bytes: Optional[bytes] = None) -> str:
            messages = []
            
            if image_bytes:
                # Vision model with image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                            }
                        }
                    ]
                })
            else:
                messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        
        return openai_call

    def _create_anthropic_function(self, api_key: Optional[str], model: str) -> Callable:
        """Create Anthropic Claude LLM function."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic support requires anthropic package. Install with:\n"
                "  pip install anthropic"
            )
        
        client = anthropic.Anthropic(api_key=api_key)
        
        def anthropic_call(prompt: str, image_bytes: Optional[bytes] = None) -> str:
            content = []
            
            if image_bytes:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64.b64encode(image_bytes).decode('utf-8')
                    }
                })
            
            content.append({"type": "text", "text": prompt})
            
            message = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": content}]
            )
            return message.content[0].text
        
        return anthropic_call
    
    def _load_data(self, data: Union[Dict, str, Path]) -> Dict:
        """Load data from various sources."""
        if isinstance(data, dict):
            return data
        
        if isinstance(data, (str, Path)):
            path = Path(data)
            if path.exists():
                content = path.read_text(encoding="utf-8-sig")
            else:
                content = data
            
            # Parse based on format
            if self.format == "json":
                return json.loads(content)
            elif self.format == "yaml":
                if not HAS_YAML:
                    raise ImportError("PyYAML not installed. Install with: pip install pyyaml")
                return yaml.safe_load(content)
            else:
                raise ValueError(f"Unsupported format: {self.format}")
        
        raise TypeError(f"Unsupported data type: {type(data)}")

    def _deep_copy(self, data: Dict) -> Dict:
        """Deep copy data."""
        if self.format == "json":
            return json.loads(json.dumps(data))
        elif self.format == "yaml":
            return yaml.safe_load(yaml.dump(data))
        return data.copy()

    def _serialize(self, data: Dict) -> str:
        """Serialize data to string."""
        if self.format == "json":
            return json.dumps(data, indent=2)
        elif self.format == "yaml":
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        return str(data)
    
    def edit(self, instruction: str, include_image: bool = True) -> Dict:
        """
        Apply an edit instruction using AI.
        
        Args:
            instruction: Natural language edit instruction
            include_image: Whether to include reference image
            
        Returns:
            Edited data as dictionary
        """
        # Build prompt with current data
        prompt = f"""{self.SYSTEM_PROMPT}

Current {self.format.upper()}:
{self._serialize(self.current_data)}

User request: {instruction}

Return the corrected {self.format.upper()} object wrapped in ```{self.format}``` code block."""

        try:
            # Call LLM (with or without image)
            image_to_send = self.image_bytes if (include_image and self.image_bytes) else None
            response_text = self.llm_function(prompt, image_to_send)
            
            # Extract and parse response
            edited_data = self._extract_data(response_text)
            
            if edited_data is None:
                raise ValueError("Could not parse AI response")
            
            # Validate structure
            if not self._validate_structure(edited_data):
                raise ValueError("Response structure doesn't match original")
            
            # Update state
            self.history.append(self._deep_copy(edited_data))
            self.current_data = edited_data
            self.edit_history.append({
                'instruction': instruction,
                'response': response_text
            })
            
            return edited_data
            
        except Exception as e:
            raise RuntimeError(f"Edit failed: {e}")

    def _extract_data(self, response_text: str) -> Optional[Dict]:
        """Extract data from AI response."""
        try:
            # Try to extract from code block
            pattern = r'```(?:json|yaml|yml)?\s*\n?(.*?)\n?```'
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            if match:
                content = match.group(1).strip()
            else:
                content = response_text.strip()
            
            # Parse based on format
            if self.format == "json":
                return json.loads(content)
            elif self.format == "yaml":
                return yaml.safe_load(content)
                
        except Exception as e:
            print(f"Parse error: {e}")
            return None

    def _validate_structure(self, new_data: Dict) -> bool:
        """Validate that new data has same structure as original."""
        def get_keys(d, prefix=""):
            keys = set()
            if isinstance(d, dict):
                for k, v in d.items():
                    keys.add(f"{prefix}{k}")
                    if isinstance(v, dict):
                        keys.update(get_keys(v, f"{prefix}{k}."))
            return keys
        
        original_keys = get_keys(self.original_data)
        new_keys = get_keys(new_data)
        
        return original_keys == new_keys
    
    def undo(self) -> bool:
        """Undo last edit. Returns True if successful."""
        if len(self.history) > 1:
            self.history.pop()
            self.current_data = self._deep_copy(self.history[-1])
            if self.edit_history:
                self.edit_history.pop()
            return True
        return False

    def reset(self):
        """Reset to original data."""
        self.current_data = self._deep_copy(self.original_data)
        self.history = [self._deep_copy(self.original_data)]
        self.edit_history = []

    def save(self, path: Union[str, Path]) -> None:
        """Save current data to file."""
        path = Path(path)
        path.write_text(self._serialize(self.current_data))

    def get_current(self) -> Dict:
        """Get current data as dictionary."""
        return self._deep_copy(self.current_data)

    def get_original(self) -> Dict:
        """Get original data as dictionary."""
        return self._deep_copy(self.original_data)

    @property
    def has_changes(self) -> bool:
        """Check if data has been modified."""
        return self.current_data != self.original_data