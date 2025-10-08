import pytest
from brainstack.main import run_pipeline

def test_text_only_query():
    """Test that a text-only query returns a dict with a string answer."""
    result = run_pipeline(text="What is a cat?")
    assert isinstance(result, dict), "Result must be a dictionary"
    assert "answer" in result, "Result must have an 'answer' key"
    assert isinstance(result["answer"], str), "Answer must be a string"
    assert result["answer"] == "A small carnivorous mammal.", "Expected answer from FAQ"

def test_empty_inputs():
    """Test that empty inputs return a low-confidence message."""
    result = run_pipeline(text=None, image=None)
    assert isinstance(result, dict), "Result must be a dictionary"
    assert "answer" in result, "Result must have an 'answer' key"
    assert isinstance(result["answer"], str), "Answer must be a string"
    assert any(phrase in result["answer"].lower() for phrase in ["couldn't find", "no confident"]), \
        "Answer must contain 'couldn't find' or 'no confident' for empty inputs"
    assert result["answer"] == "I couldn't find a confident answer.", "Expected default low-confidence message"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])