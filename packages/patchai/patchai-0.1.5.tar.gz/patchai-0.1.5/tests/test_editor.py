"""Tests for PatchAI editor."""

import json
import pytest
from pathlib import Path
from patchai import PatchAI


@pytest.fixture
def sample_json():
    """Sample JSON data for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York"
        }
    }


@pytest.fixture
def temp_json_file(tmp_path, sample_json):
    """Create temporary JSON file."""
    file_path = tmp_path / "test.json"
    file_path.write_text(json.dumps(sample_json, indent=2))
    return file_path


def test_init_with_dict(sample_json):
    """Test initialization with dictionary."""
    editor = PatchAI(sample_json)
    assert editor.get_current() == sample_json
    assert editor.get_original() == sample_json
    assert not editor.has_changes


def test_init_with_file(temp_json_file, sample_json):
    """Test initialization with file path."""
    editor = PatchAI(temp_json_file)
    assert editor.get_current() == sample_json


def test_init_with_json_string(sample_json):
    """Test initialization with JSON string."""
    json_str = json.dumps(sample_json)
    editor = PatchAI(json_str)
    assert editor.get_current() == sample_json


def test_deep_copy(sample_json):
    """Test that data is deep copied."""
    editor = PatchAI(sample_json)
    current = editor.get_current()
    current["name"] = "Jane Doe"
    
    # Original should be unchanged
    assert editor.get_current()["name"] == "John Doe"


def test_has_changes(sample_json):
    """Test has_changes property."""
    editor = PatchAI(sample_json)
    assert not editor.has_changes
    
    # Manually modify for testing
    editor.current_data["name"] = "Jane Doe"
    assert editor.has_changes


def test_reset(sample_json):
    """Test reset functionality."""
    editor = PatchAI(sample_json)
    
    # Manually modify
    editor.current_data["name"] = "Jane Doe"
    assert editor.has_changes
    
    # Reset
    editor.reset()
    assert not editor.has_changes
    assert editor.get_current()["name"] == "John Doe"


def test_undo(sample_json):
    """Test undo functionality."""
    editor = PatchAI(sample_json)
    
    # Make change
    editor.history.append({"name": "Jane Doe"})
    editor.current_data = {"name": "Jane Doe"}
    
    # Undo
    assert editor.undo()
    assert editor.get_current() == sample_json
    
    # Can't undo beyond original
    assert not editor.undo()


def test_save(tmp_path, sample_json):
    """Test saving to file."""
    editor = PatchAI(sample_json)
    
    # Manually modify
    editor.current_data["name"] = "Jane Doe"
    
    # Save
    output_path = tmp_path / "output.json"
    editor.save(output_path)
    
    # Verify
    assert output_path.exists()
    saved_data = json.loads(output_path.read_text())
    assert saved_data["name"] == "Jane Doe"


def test_serialize_json(sample_json):
    """Test JSON serialization."""
    editor = PatchAI(sample_json, format="json")
    result = editor._serialize(sample_json)
    assert json.loads(result) == sample_json


def test_validate_structure(sample_json):
    """Test structure validation."""
    editor = PatchAI(sample_json)
    
    # Same structure should validate
    assert editor._validate_structure(sample_json)
    
    # Different structure should fail
    invalid = {"different": "structure"}
    assert not editor._validate_structure(invalid)
    
    # Same keys, different values should validate
    modified = sample_json.copy()
    modified["name"] = "Jane Doe"
    assert editor._validate_structure(modified)


def test_extract_json_from_code_block():
    """Test extracting JSON from markdown code block."""
    editor = PatchAI({"test": "data"})
    
    response = '''```json
{
  "test": "modified"
}
```'''
    
    result = editor._extract_data(response)
    assert result == {"test": "modified"}


def test_extract_json_plain():
    """Test extracting plain JSON."""
    editor = PatchAI({"test": "data"})
    
    response = '{"test": "modified"}'
    
    result = editor._extract_data(response)
    assert result == {"test": "modified"}


def test_history_tracking(sample_json):
    """Test edit history tracking."""
    editor = PatchAI(sample_json)
    
    # Initial history
    assert len(editor.history) == 1
    assert len(editor.edit_history) == 0
    
    # Add to history manually (simulating edit)
    new_data = sample_json.copy()
    new_data["name"] = "Jane Doe"
    editor.history.append(new_data)
    editor.current_data = new_data
    editor.edit_history.append({
        'instruction': 'Test edit',
        'response': 'Test response'
    })
    
    assert len(editor.history) == 2
    assert len(editor.edit_history) == 1


@pytest.mark.parametrize("format_type", ["json", "yaml"])
def test_format_support(sample_json, format_type):
    """Test different format support."""
    if format_type == "yaml":
        pytest.importorskip("yaml")
    
    editor = PatchAI(sample_json, format=format_type)
    assert editor.format == format_type


def test_invalid_format(sample_json):
    """Test invalid format raises error."""
    with pytest.raises(ValueError, match="Unsupported format"):
        editor = PatchAI(sample_json, format="invalid")
        # Try to use it
        editor._serialize(sample_json)


def test_image_loading(tmp_path, sample_json):
    """Test image loading."""
    # Create dummy image
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"fake image data")
    
    editor = PatchAI(sample_json, image_path=image_path)
    assert editor.image_bytes == b"fake image data"


def test_missing_image(sample_json):
    """Test handling of missing image."""
    editor = PatchAI(sample_json, image_path="nonexistent.jpg")
    assert editor.image_bytes is None