import numpy as np
from pathlib import Path
from typing import Dict, List, Union

class RouterRules:
    """Deterministic router for input based on type and configuration."""
    
    def __init__(self, config: Dict):
        """Initialize router with configuration.

        Args:
            config: Dict with optional 'chaos' and 'budget' keys.
        """
        self.config = config
        self.default_latency_ms = 500
        # Validate config
        self.chaos_enabled = config.get('chaos', {}).get('enabled', False)
        self.latency_ms = config.get('budget', {}).get('latency_ms', self.default_latency_ms)

    def route(self, text: Union[str, None], image: Union[np.ndarray, str, Path, None]) -> Dict:
        """Route input to appropriate modules based on type and config.

        Args:
            text: Input text string or None.
            image: Input image as np.ndarray (RGB uint8), path, or None.

        Returns:
            Dict with modules (list of module names), reasons, and budget.
        """
        modules = []
        reasons = []
        
        # Check text input
        if text and isinstance(text, str) and text.strip():
            modules.extend(["retriever", "qa_small"])
            reasons.append("Text input provided; routing to retriever and qa_small.")
        
        # Check image input
        if image is not None:
            if isinstance(image, np.ndarray):
                if image.shape[2] != 3 or image.dtype != np.uint8:
                    reasons.append("Invalid image array; skipping vision_labeler.")
                else:
                    modules.append("vision_labeler")
                    reasons.append("Valid image array provided; routing to vision_labeler.")
            elif isinstance(image, (str, Path)):
                try:
                    from brainstack.utils.io import load_image
                    img = load_image(image)
                    modules.append("vision_labeler")
                    reasons.append(f"Valid image path {image} provided; routing to vision_labeler.")
                except FileNotFoundError:
                    reasons.append(f"Image path {image} not found; skipping vision_labeler.")
            else:
                reasons.append("Invalid image input; skipping vision_labeler.")
        
        # Add chaotic amplifier if enabled
        if self.chaos_enabled and modules:
            modules.insert(0, "amplifier")
            reasons.append("Chaos enabled in config; adding amplifier as pre-step.")
        
        # Handle empty input case
        if not modules:
            reasons.append("No valid text or image input; no modules selected.")
        
        return {
            "modules": modules,
            "reasons": reasons,
            "budget": {"latency_ms": self.latency_ms}
        }

if __name__ == "__main__":
    # Test RouterRules
    import numpy as np
    
    # Minimal config
    config = {
        "chaos": {"enabled": True},
        "budget": {"latency_ms": 1000}
    }
    
    # Initialize router
    router = RouterRules(config)
    
    # Test 1: Text only
    text_input = "What is a cat?"
    result_text = router.route(text=text_input, image=None)
    print("Text-only routing:", result_text)
    
    # Test 2: Image only
    dummy_img = np.ones((64, 64, 3), dtype=np.uint8)  # Dummy RGB image
    result_image = router.route(text=None, image=dummy_img)
    print("Image-only routing:", result_image)
    
    # Test 3: Both text and image
    result_both = router.route(text=text_input, image=dummy_img)
    print("Text+Image routing:", result_both)
    
    # Test 4: Empty input
    result_empty = router.route(text=None, image=None)
    print("Empty routing:", result_empty)