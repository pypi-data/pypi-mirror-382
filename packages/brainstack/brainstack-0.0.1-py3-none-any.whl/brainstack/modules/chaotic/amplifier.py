import numpy as np
from typing import List, Dict

class ChaoticAmplifier:
    """Generate chaotic variants of an input embedding for diversity."""
    
    def __init__(self, map_type: str = 'logistic', r: float = 3.9, steps: int = 1, 
                 variants: int = 2, seed: int | None = None):
        """Initialize chaotic amplifier with logistic map parameters.

        Args:
            map_type: Type of chaotic map ('logistic' supported).
            r: Logistic map parameter (e.g., 3.9 for chaotic behavior).
            steps: Number of iterations for the chaotic map.
            variants: Number of output variants (1 or 2).
            seed: Optional seed for PRNG to control jitter.
        """
        if map_type != 'logistic':
            raise ValueError("Only 'logistic' map_type is supported")
        if variants not in [1, 2]:
            raise ValueError("Variants must be 1 or 2")
        self.map_type = map_type
        self.r = r
        self.steps = max(1, steps)
        self.variants = variants
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def transform(self, vec: np.ndarray) -> List[np.ndarray]:
        """Generate chaotic variants of the input vector.

        Args:
            vec: Input vector (float32 or float64).

        Returns:
            List of variant vectors, each L2-normalized.
        """
        if not isinstance(vec, np.ndarray) or vec.size == 0:
            raise ValueError("Input must be a non-empty numpy array")
        
        # Convert to float32 for consistency
        vec = vec.astype(np.float32)
        
        # Normalize to [0,1] per feature
        min_val = np.min(vec)
        max_val = np.max(vec)
        if max_val - min_val < 1e-8:
            # Constant vector: return duplicates
            return [vec.copy() for _ in range(self.variants)]
        
        norm_vec = (vec - min_val) / (max_val - min_val + 1e-8)
        
        # Generate variants
        results = []
        for i in range(self.variants):
            # Apply small per-feature jitter using PRNG
            jitter_seed = self.rng.integers(0, 1000000) if self.seed is not None else None
            jitter_rng = np.random.default_rng(jitter_seed)
            jitter = jitter_rng.normal(0, 0.01, size=vec.shape).astype(np.float32)
            variant = norm_vec + jitter
            
            # Apply logistic map
            if self.map_type == 'logistic':
                for _ in range(self.steps):
                    variant = self.r * variant * (1 - variant)
            
            # Clamp to finite values and handle NaNs
            variant = np.clip(variant, 0, 1)
            variant = np.where(np.isfinite(variant), variant, 0.0)
            
            # Re-center to zero-mean
            variant -= np.mean(variant)
            
            # L2 normalize
            norm = np.linalg.norm(variant)
            if norm > 0:
                variant = variant / norm
            
            results.append(variant)
        
        return results

    def info(self) -> Dict:
        """Return parameters for logging.

        Returns:
            Dict with map_type, r, steps, variants, seed.
        """
        return {
            "map_type": self.map_type,
            "r": self.r,
            "steps": self.steps,
            "variants": self.variants,
            "seed": self.seed
        }

if __name__ == "__main__":
    # Test ChaoticAmplifier
    import numpy as np
    
    # Create dummy vector
    dummy_vec = np.array([0.1, 0.5, 0.3, 0.8, 0.2], dtype=np.float32)
    
    # Initialize amplifier
    amplifier = ChaoticAmplifier(map_type='logistic', r=3.9, steps=2, variants=2, seed=42)
    
    # Generate variants
    variants = amplifier.transform(dummy_vec)
    
    # Print results
    print(f"Input vector: {dummy_vec}")
    for i, var in enumerate(variants):
        print(f"Variant {i+1}: {var[:3]}... (norm: {np.linalg.norm(var):.6f})")
    print(f"Parameters: {amplifier.info()}")