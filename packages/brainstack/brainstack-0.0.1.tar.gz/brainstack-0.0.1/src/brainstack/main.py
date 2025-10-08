import argparse
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Optional
from brainstack.modules.embeddings.text_embedder import TextEmbedder
from brainstack.modules.memory_classical.store import CorpusStore
from brainstack.modules.memory_classical.retriever import Retriever
from brainstack.modules.text.qa_small import QASmall
from brainstack.modules.embeddings.image_embedder import ImageEmbedder
from brainstack.modules.vision.vision_labeler import VisionLabeler
from brainstack.modules.chaotic.amplifier import ChaoticAmplifier
from brainstack.controller.router_rules import RouterRules
from brainstack.controller.integrator_simple import IntegratorSimple
from brainstack.utils.io import load_text

def load_default_config() -> Dict:
    """Load default configuration."""
    return {
        "chaos": {"enabled": False},
        "budget": {"latency_ms": 500},
        "data": {
            "corpus_dir": "data/corpus",
            "image_dir": "data/images"
        },
        "priors": {
            "qa_small": 1.0,
            "vision_labeler": 0.9
        }
    }

def initialize_modules(config: Dict, seed: Optional[int] = None) -> Dict:
    """Initialize all modules with config and optional seed."""
    modules = {}
    
    # Text pipeline
    text_embedder = TextEmbedder(max_features=1000)
    corpus_dir = Path(config.get("data", {}).get("corpus_dir", "data/corpus"))
    corpus_store = CorpusStore(str(corpus_dir / "store.jsonl"))
    
    # Load sample corpus if exists
    records = []
    if corpus_dir.exists():
        for text_file in corpus_dir.glob("*.txt"):
            try:
                corpus_store.add_file(str(text_file))
            except Exception as e:
                print(f"Warning: Failed to load {text_file}: {e}")
        records = corpus_store.load_all()
    
    # Fit text embedder (use FAQ as fallback if no corpus)
    faq = {"What is a cat?": "A small carnivorous mammal."}
    if records:
        text_embedder.fit([r["text"] for r in records])
    else:
        text_embedder.fit(list(faq.keys()) + list(faq.values()))
    
    retriever = Retriever(text_embedder, k=5)
    retriever.fit(records)
    
    qa_small = QASmall(retriever, faq=faq)
    
    # Image pipeline
    image_embedder = ImageEmbedder(max_keypoints=2000)
    vision_labeler = VisionLabeler(image_embedder)
    
    # Chaotic amplifier (optional)
    if config.get("chaos", {}).get("enabled", False):
        chaotic_amplifier = ChaoticAmplifier(map_type="logistic", r=3.9, steps=2, variants=2, seed=seed)
        modules["amplifier"] = chaotic_amplifier
    
    # Router and integrator
    router = RouterRules(config)
    integrator = IntegratorSimple(config.get("priors", {}))
    
    modules.update({
        "text_embedder": text_embedder,
        "corpus_store": corpus_store,
        "retriever": retriever,
        "qa_small": qa_small,
        "image_embedder": image_embedder,
        "vision_labeler": vision_labeler,
        "router": router,
        "integrator": integrator
    })
    
    return modules

def run_pipeline(text: Optional[str] = None, image: Optional[Union[np.ndarray, str, Path]] = None, 
                config: Optional[Dict] = None) -> Dict:
    """Run the full pipeline with text and/or image input.

    Args:
        text: Input text string or None.
        image: Input image as np.ndarray, path, or None.
        config: Configuration dict or None (loads defaults).

    Returns:
        Dict with answer and debug info (modules, latency, router output, seeds).
    """
    # Load config
    config = config or load_default_config()
    
    # Initialize modules with seed
    seed = 42  # Fixed seed for reproducibility
    modules = initialize_modules(config, seed)
    
    # Route input
    start_time = time.time()
    router_output = modules["router"].route(text, image)
    latency_breakdown = [{"module": "router", "ms": int((time.time() - start_time) * 1000)}]
    
    # Collect reports
    reports = []
    activated_modules = router_output["modules"]
    
    if "amplifier" in activated_modules:
        # Apply chaotic amplifier to text or image embeddings
        amplifier = modules["amplifier"]
        if "qa_small" in activated_modules and text:
            # Embed text and amplify
            text_embed = modules["text_embedder"].embed(text)["vector"]
            variants = amplifier.transform(text_embed)
            # Use first variant for qa_small (simplified)
            start_module = time.time()
            text_report = modules["qa_small"].answer(text)
            text_report["confidence"] = text_report["confidence"] * 0.9  # Discount for chaos
            text_report["module"] = "qa_small"
            reports.append(text_report)
            latency_breakdown.append({"module": "qa_small", "ms": int((time.time() - start_module) * 1000)})
        if "vision_labeler" in activated_modules and image:
            # Load reference images excluding query if path provided
            image_dir = Path(config.get("data", {}).get("image_dir", "data/images"))
            ref_images = []
            if image_dir.exists():
                all_images = [(f.stem, str(f)) for f in image_dir.glob("*.png")]
                # Exclude query image if it's a path in the directory
                if isinstance(image, (str, Path)):
                    query_path = Path(image)
                    if query_path.exists():
                        ref_images = [(label, path) for label, path in all_images if Path(path) != query_path]
                else:
                    ref_images = all_images
            # Fit vision_labeler with refs
            modules["vision_labeler"].fit(ref_images)
            # Embed image and amplify
            image_embed = modules["image_embedder"].embed(image)["vector"]
            variants = amplifier.transform(image_embed)
            # Use first variant for vision_labeler (simplified)
            start_module = time.time()
            vision_report = modules["vision_labeler"].predict(image)
            vision_report["confidence"] = vision_report["confidence"] * 0.9  # Discount for chaos
            vision_report["module"] = "vision_labeler"
            reports.append(vision_report)
            latency_breakdown.append({"module": "vision_labeler", "ms": int((time.time() - start_module) * 1000)})
    else:
        # Run modules directly
        if "qa_small" in activated_modules and text:
            start_module = time.time()
            report = modules["qa_small"].answer(text)
            report["module"] = "qa_small"
            reports.append(report)
            latency_breakdown.append({"module": "qa_small", "ms": int((time.time() - start_module) * 1000)})
        if "vision_labeler" in activated_modules and image:
            # Load reference images excluding query if path provided
            image_dir = Path(config.get("data", {}).get("image_dir", "data/images"))
            ref_images = []
            if image_dir.exists():
                all_images = [(f.stem, str(f)) for f in image_dir.glob("*.png")]
                # Exclude query image if it's a path in the directory
                if isinstance(image, (str, Path)):
                    query_path = Path(image)
                    if query_path.exists():
                        ref_images = [(label, path) for label, path in all_images if Path(path) != query_path]
                else:
                    ref_images = all_images
            # Fit vision_labeler with refs
            modules["vision_labeler"].fit(ref_images)
            start_module = time.time()
            report = modules["vision_labeler"].predict(image)
            report["module"] = "vision_labeler"
            reports.append(report)
            latency_breakdown.append({"module": "vision_labeler", "ms": int((time.time() - start_module) * 1000)})
    
    # Integrate reports
    start_integrate = time.time()
    result = modules["integrator"].integrate(reports)
    latency_breakdown.append({"module": "integrator", "ms": int((time.time() - start_integrate) * 1000)})
    
    # Build final output
    return {
        "answer": result["answer"],
        "debug": {
            "activated_modules": result["activated_modules"],
            "latency_breakdown": latency_breakdown,
            "router": router_output,
            "seeds": {"global": seed}
        }
    }

if __name__ == "__main__":
    # CLI for testing
    parser = argparse.ArgumentParser(description="Brainstack Pipeline")
    parser.add_argument("--text", type=str, help="Input text query")
    parser.add_argument("--image", type=str, help="Path to input image")
    args = parser.parse_args()
    
    # Run pipeline
    result = run_pipeline(text=args.text, image=args.image)
    
    # Print result
    print("Answer:", result["answer"])
    print("Debug:")
    print(f"  Activated Modules: {result['debug']['activated_modules']}")
    print("  Latency Breakdown:")
    for entry in result['debug']['latency_breakdown']:
        print(f"    {entry['module']}: {entry['ms']}ms")
    print(f"  Router Output: {result['debug']['router']}")
    print(f"  Seeds: {result['debug']['seeds']}")