import numpy as np
from pathlib import Path
from typing import Dict, Union
import cv2
from brainstack.utils.io import load_image

class ImageEmbedder:
    """Lightweight image embedder using ORB descriptors and RGB color histogram."""
    
    def __init__(self, max_keypoints: int = 500):
        """Initialize the embedder with ORB parameters.

        Args:
            max_keypoints: Maximum number of ORB keypoints to detect.
        """
        self.max_keypoints = max_keypoints
        self.orb = cv2.ORB_create(nfeatures=max_keypoints)
        self.hist_bins = 32  # Bins per RGB channel
        self.hist_size = self.hist_bins * 3  # Total histogram dimensions (R+G+B)
        self.orb_dim = 32  # ORB descriptor dimension (fixed by OpenCV ORB)

    def embed(self, image: Union[np.ndarray, str, Path]) -> Dict[str, Union[np.ndarray, Dict]]:
        """Embed an image into a compact descriptor.

        Args:
            image: RGB image as np.ndarray (H,W,3, uint8) or path to image.

        Returns:
            Dict with:
                - vector: L2-normalized feature vector (float32).
                - meta: Dict with number of keypoints and histogram bins.
        """
        # Set deterministic RNG for ORB
        cv2.setRNGSeed(0)
        
        # Load image if path provided
        if isinstance(image, (str, Path)):
            img = load_image(image)
        else:
            img = image
        
        # Validate image
        if not isinstance(img, np.ndarray) or img.shape[2] != 3 or img.dtype != np.uint8:
            raise ValueError("Image must be RGB uint8 array with shape (H,W,3)")
        
        # Compute ORB descriptors
        keypoints, descriptors = self.orb.detectAndCompute(img, None)
        kpts_count = len(keypoints) if keypoints else 0
        
        # Mean pool ORB descriptors (or zeros if none)
        if descriptors is not None and len(descriptors) > 0:
            orb_vector = np.mean(descriptors, axis=0, dtype=np.float32)
        else:
            orb_vector = np.zeros(self.orb_dim, dtype=np.float32)
        
        # Compute color histogram (32 bins per RGB channel)
        hist = []
        for channel in range(3):  # R, G, B
            channel_hist = cv2.calcHist([img], [channel], None, [self.hist_bins], [0, 256])
            hist.append(channel_hist.flatten())
        hist_vector = np.concatenate(hist).astype(np.float32)
        
        # L1 normalize histogram
        hist_vector = hist_vector / (np.sum(hist_vector) + 1e-10)
        
        # Concatenate ORB and histogram features
        final_vector = np.concatenate([orb_vector, hist_vector], axis=0)
        
        # L2 normalize final vector
        norm = np.linalg.norm(final_vector)
        if norm > 0:
            final_vector = final_vector / norm
        
        return {
            "vector": final_vector,
            "meta": {"kpts": kpts_count, "hist_bins": self.hist_size}
        }

if __name__ == "__main__":
    # Test ImageEmbedder
    import numpy as np
    
    # Create a synthetic 64x64 RGB image (red square)
    synthetic_img = np.zeros((64, 64, 3), dtype=np.uint8)
    synthetic_img[:, :, 0] = 255  # Red channel full
    
    # Initialize embedder
    embedder = ImageEmbedder(max_keypoints=100)
    
    # Embed image
    result = embedder.embed(synthetic_img)
    
    # Print results
    print(f"Vector shape: {result['vector'].shape}")
    print(f"Keypoints detected: {result['meta']['kpts']}")
    print(f"Histogram bins: {result['meta']['hist_bins']}")