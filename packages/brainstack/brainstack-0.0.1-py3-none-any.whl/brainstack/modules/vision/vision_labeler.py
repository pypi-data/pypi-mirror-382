import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Tuple
import cv2
from brainstack.utils.io import load_image
from brainstack.modules.embeddings.image_embedder import ImageEmbedder

class VisionLabeler:
    """Basic vision labeler using ORB feature matching for near-duplicate detection."""
    
    def __init__(self, image_embedder: ImageEmbedder):
        """Initialize with an ImageEmbedder (for potential extensions).

        Args:
            image_embedder: Instance of ImageEmbedder.
        """
        self.image_embedder = image_embedder
        # Optimized ORB settings for simple images
        self.orb = cv2.ORB_create(nfeatures=2000, scaleFactor=1.1, nlevels=10, edgeThreshold=10)
        self.labels: List[str] = []
        self.dess: List[np.ndarray] = []  # List of descriptors for each reference
        self.kpts_counts: List[int] = []  # Keypoint counts for debugging
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    def fit(self, ref_images: List[Tuple[str, Union[str, Path]]]) -> 'VisionLabeler':
        """Fit the labeler with reference images and their labels.

        Args:
            ref_images: List of (label, path) tuples.

        Returns:
            Self, fitted labeler.
        """
        self.labels = []
        self.dess = []
        self.kpts_counts = []
        
        for label, path in ref_images:
            img = load_image(path)
            kpts, des = self.orb.detectAndCompute(img, None)
            self.labels.append(label)
            self.dess.append(des)
            self.kpts_counts.append(len(kpts) if kpts else 0)
        
        return self

    def predict(self, image: Union[np.ndarray, str, Path]) -> Dict[str, Union[List[Dict], float, str]]:
        """Predict labels for the input image based on feature matching.

        Args:
            image: Image as np.ndarray (RGB uint8) or path.

        Returns:
            Dict with labels (list of dicts with label, matches, score), confidence, rationale.
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
        
        # Compute query descriptors
        kpts_query, des_query = self.orb.detectAndCompute(img, None)
        kpts_query_count = len(kpts_query) if kpts_query else 0
        
        if des_query is None or kpts_query_count == 0:
            return {
                "labels": [],
                "confidence": 0.0,
                "rationale": f"No keypoints detected in query image (keypoints={kpts_query_count})."
            }
        
        # Compute matches for each reference
        match_counts = []
        for i, des_ref in enumerate(self.dess):
            if des_ref is None or len(des_ref) == 0:
                match_counts.append(0)
                continue
            
            matches = self.matcher.knnMatch(des_query, des_ref, k=3)
            # Convert matches to list to handle tuple case
            matches = list(matches)
            # Apply Lowe's ratio test with padding for fewer matches
            good_matches = [
                m for m, n, *rest in matches + [[None, None, None]]
                if m and n and m.distance < 0.85 * n.distance
            ]
            match_counts.append(len(good_matches))
        
        # Include all references in results
        max_matches = max(match_counts) if match_counts else 0
        scores = [count / (max_matches + 1e-10) for count in match_counts]
        
        # Build labels list, sorted by score descending
        label_results = []
        for i, score in enumerate(scores):
            label_results.append({
                "label": self.labels[i],
                "matches": match_counts[i],
                "score": score
            })
        label_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Confidence and rationale
        confidence = label_results[0]["score"] if label_results else 0.0
        if confidence > 0:
            top_label = label_results[0]["label"]
            top_matches = label_results[0]["matches"]
            rationale = (f"Top label '{top_label}' with {top_matches} matches "
                        f"(query keypoints={kpts_query_count}, "
                        f"ref keypoints={[self.kpts_counts[i] for i in range(len(self.labels))]})")
        else:
            rationale = (f"No good matches found "
                        f"(query keypoints={kpts_query_count}, "
                        f"ref keypoints={[self.kpts_counts[i] for i in range(len(self.labels))]})")
        
        return {
            "labels": label_results,
            "confidence": float(confidence),
            "rationale": rationale
        }

if __name__ == "__main__":
    # Test VisionLabeler with synthetic images
    import numpy as np
    import tempfile
    import os
    
    # Create synthetic reference images with texture (noise + shapes)
    # Ref1: Square with noise
    ref1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    noise = np.random.randint(0, 50, (100, 100), dtype=np.uint8)
    ref1[:, :, 0] = 255 - noise  # Red channel with noise
    cv2.rectangle(ref1, (20, 20), (80, 80), (0, 0, 0), 2)
    
    # Ref2: Circle with noise
    ref2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    noise = np.random.randint(0, 50, (100, 100), dtype=np.uint8)
    ref2[:, :, 1] = 255 - noise  # Green channel with noise
    cv2.circle(ref2, (50, 50), 30, (0, 0, 0), 2)
    
    # Ref3: Triangle with noise
    ref3 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    noise = np.random.randint(0, 50, (100, 100), dtype=np.uint8)
    ref3[:, :, 2] = 255 - noise  # Blue channel with noise
    points = np.array([[50, 20], [20, 80], [80, 80]], np.int32)
    cv2.polylines(ref3, [points], True, (0, 0, 0), 2)
    
    # Save to temp files
    ref_images = []
    temp_files = []
    for label, img in [("square", ref1), ("circle", ref2), ("triangle", ref3)]:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            cv2.imwrite(f.name, img)
            ref_images.append((label, f.name))
            temp_files.append(f.name)
    
    # Initialize embedder (dummy)
    embedder = ImageEmbedder(max_keypoints=2000)
    
    # Fit labeler
    labeler = VisionLabeler(embedder)
    labeler.fit(ref_images)
    
    # Query with a square-like image with similar noise
    query_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    noise = np.random.randint(0, 50, (100, 100), dtype=np.uint8)
    query_img[:, :, 0] = 255 - noise  # Red channel with noise
    cv2.rectangle(query_img, (15, 15), (85, 85), (0, 0, 0), 2)
    
    result = labeler.predict(query_img)
    
    print("Labels:", result["labels"])
    print("Confidence:", result["confidence"])
    print("Rationale:", result["rationale"])
    
    # Clean up temp files
    for path in temp_files:
        os.unlink(path)