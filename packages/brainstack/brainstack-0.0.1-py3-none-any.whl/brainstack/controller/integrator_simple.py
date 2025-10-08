from typing import List, Dict, Optional
import json

class IntegratorSimple:
    """Integrate multiple module reports into a final answer."""
    
    def __init__(self, priors: Optional[Dict[str, float]] = None):
        """Initialize with module priors.

        Args:
            priors: Dict mapping module names to priority weights (default 1.0 if None).
        """
        self.priors = priors or {}
        self.default_prior = 1.0

    def integrate(self, reports: List[Dict]) -> Dict:
        """Integrate reports into a single answer with sections and confidence.

        Args:
            reports: List of report dicts, each with 'module', 'confidence', and module-specific fields.

        Returns:
            Dict with answer, overall_confidence, sections, and activated_modules.
        """
        if not reports:
            return {
                "answer": "I couldn't find a confident answer.",
                "overall_confidence": 0.0,
                "sections": [],
                "activated_modules": []
            }
        
        # Extract activated modules
        activated_modules = [r["module"] for r in reports if "module" in r]
        
        # Calculate scores: prior * confidence
        scored_reports = []
        for report in reports:
            module = report.get("module", "")
            confidence = report.get("confidence", 0.0)
            prior = self.priors.get(module, self.default_prior)
            score = prior * confidence
            scored_reports.append({
                "report": report,
                "score": score,
                "module": module,
                "confidence": confidence
            })
        
        # Sort by score, descending
        scored_reports.sort(key=lambda x: x["score"], reverse=True)
        
        # Handle no valid reports
        if not scored_reports or all(r["score"] == 0 for r in scored_reports):
            return {
                "answer": "I couldn't find a confident answer.",
                "overall_confidence": 0.0,
                "sections": [],
                "activated_modules": activated_modules
            }
        
        # Pick top report as primary answer
        top_report = scored_reports[0]["report"]
        top_module = scored_reports[0]["module"]
        overall_confidence = scored_reports[0]["score"]
        
        # Determine primary answer
        if top_module == "qa_small":
            answer = top_report.get("answer", "")
        elif top_module == "vision_labeler":
            labels = top_report.get("labels", [])
            answer = labels[0]["label"] if labels else "No label identified."
        else:
            answer = "Unknown module output."
        
        # Blend with vision label if vision is present but not top
        if top_module != "vision_labeler":
            vision_report = next((r for r in reports if r.get("module") == "vision_labeler"), None)
            if vision_report:
                labels = vision_report.get("labels", [])
                if labels:
                    top_vision_label = labels[0].get("label", "")
                    if top_vision_label:
                        answer += f" (image labeled as '{top_vision_label}')"
        
        # Build sections
        sections = []
        
        # Add Evidence section for citations/matches
        evidence = []
        for report in reports:
            module = report.get("module", "")
            if module == "qa_small" and "citations" in report and report["citations"]:
                for citation in report["citations"]:
                    evidence.append(f"Text source (ID: {citation['id']}, score: {citation['score']:.3f})")
            elif module == "vision_labeler" and "labels" in report and report["labels"]:
                for label in report["labels"]:
                    evidence.append(f"Image label '{label['label']}' (matches: {label['matches']}, score: {label['score']:.3f})")
        
        if evidence:
            sections.append({
                "title": "Evidence",
                "body": "\n".join(evidence)
            })
        
        # Add "What I skipped" section for low-confidence reports
        skipped = []
        for r in scored_reports:
            if r["score"] < 0.5 * overall_confidence or r["confidence"] < 0.1:
                skipped.append(f"Module {r['module']} (confidence: {r['confidence']:.3f}, score: {r['score']:.3f})")
        
        if skipped:
            sections.append({
                "title": "What I skipped",
                "body": "\n".join(skipped)
            })
        
        result = {
            "answer": answer,
            "overall_confidence": float(overall_confidence),
            "sections": sections,
            "activated_modules": activated_modules
        }
        
        # Print full integrator output for debugging
        print("\nFull Integrator Output:")
        print(json.dumps(result, indent=2, default=str))
        
        return result

if __name__ == "__main__":
    # Test IntegratorSimple
    # Fake reports
    reports = [
        {
            "module": "qa_small",
            "answer": "A cat is a small carnivorous mammal.",
            "confidence": 0.9,
            "citations": [{"id": "1", "score": 0.85}]
        },
        {
            "module": "vision_labeler",
            "labels": [{"label": "cat", "matches": 10, "score": 0.95}],
            "confidence": 0.2
        }
    ]
    
    # Initialize integrator with priors
    priors = {"qa_small": 1.0, "vision_labeler": 0.9}
    integrator = IntegratorSimple(priors)
    
    # Integrate reports
    result = integrator.integrate(reports)
    
    # Print result
    print("Integrated Result:")
    print(f"Answer: {result['answer']}")
    print(f"Overall Confidence: {result['overall_confidence']:.3f}")
    print("Sections:")
    for section in result['sections']:
        print(f"- {section['title']}:\n  {section['body']}")
    print(f"Activated Modules: {result['activated_modules']}")