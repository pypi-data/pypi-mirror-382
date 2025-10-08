import re
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from brainstack.modules.memory_classical.retriever import Retriever
from brainstack.modules.embeddings.text_embedder import TextEmbedder
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt and punkt_tab are available
for resource in ['punkt', 'punkt_tab']:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        nltk.download(resource, quiet=True)

class QASmall:
    """Small QA module using rules and retrieval for extractive answers."""
    
    def __init__(self, retriever: Retriever, faq: Optional[Dict[str, str]] = None, 
                 regex_rules: Optional[List[Tuple[str, str]]] = None):
        """Initialize QA with retriever, optional FAQ dict, and regex rules.

        Args:
            retriever: Fitted Retriever for document search.
            faq: Dict of exact question-answer pairs.
            regex_rules: List of (regex_pattern, response) tuples.
        """
        self.retriever = retriever
        self.faq = faq or {}
        self.regex_rules = regex_rules or []
        self.embedder: TextEmbedder = retriever.embedder

    def answer(self, question: str, max_chars: int = 400) -> Dict[str, Any]:
        """Generate an answer to the question with confidence and rationale.

        Args:
            question: Input question string.
            max_chars: Maximum characters in the answer.

        Returns:
            Dict with answer, confidence (0-1), citations, rationale.
        """
        if not question.strip():
            return {
                "answer": "",
                "confidence": 0.0,
                "citations": [],
                "rationale": "Empty question provided."
            }
        
        # Check FAQ for exact match (case-insensitive)
        q_lower = question.lower().strip()
        for key, ans in self.faq.items():
            if q_lower == key.lower().strip():
                return {
                    "answer": ans[:max_chars],
                    "confidence": 0.9,
                    "citations": [],
                    "rationale": f"Matched FAQ entry for '{key}'."
                }
        
        # Check regex rules
        for pattern, response in self.regex_rules:
            if re.match(pattern, question, re.IGNORECASE):
                return {
                    "answer": response[:max_chars],
                    "confidence": 0.9,
                    "citations": [],
                    "rationale": f"Matched regex pattern '{pattern}'."
                }
        
        # Fall back to retrieval
        result = self.retriever.query(question, topk=1)  # Only need top hit
        hits = result["hits"]
        if not hits:
            return {
                "answer": "",
                "confidence": 0.0,
                "citations": [],
                "rationale": "No relevant documents found in corpus."
            }
        
        top_hit = hits[0]
        text = top_hit["text"]
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        if not sentences:
            # No sentences; use truncated text
            answer = text[:max_chars]
            rationale = f"Retrieved document {top_hit['id']}; no sentences detected, using snippet."
        else:
            # Embed query and sentences
            query_embed = self.embedder.embed(question)["vector"]
            sent_embeds = self.embedder.transform(sentences)
            
            # Compute cosine similarities
            cosines = np.dot(sent_embeds, query_embed.T).flatten()
            
            # Select best sentence
            max_idx = np.argmax(cosines)
            answer = sentences[max_idx][:max_chars]
            rationale = f"Retrieved document {top_hit['id']}; extracted best sentence with cosine {cosines[max_idx]:.3f}."
        
        # Confidence: use the document's blended score (0.5*bm25_norm + 0.5*cosine_norm)
        confidence = top_hit["score"]
        
        citations = [{"id": top_hit["id"], "score": top_hit["score"]}]
        
        return {
            "answer": answer,
            "confidence": float(confidence),
            "citations": citations,
            "rationale": rationale
        }

if __name__ == "__main__":
    # Test QASmall
    from brainstack.modules.embeddings.text_embedder import TextEmbedder
    from brainstack.modules.memory_classical.retriever import Retriever
    
    # Small corpus
    corpus_texts = [
        "The cat is a small carnivorous mammal. It is the only domesticated species in the family Felidae.",
        "Dogs are domesticated mammals, not natural wild animals."
    ]
    records = [
        {"id": "1", "text": corpus_texts[0], "meta": {}},
        {"id": "2", "text": corpus_texts[1], "meta": {}}
    ]
    
    # Fit embedder and retriever
    embedder = TextEmbedder(max_features=100)
    embedder.fit(corpus_texts)
    retriever = Retriever(embedder, k=1)
    retriever.fit(records)
    
    # Initialize QA with simple FAQ
    faq = {"What is a cat?": "A small carnivorous mammal."}
    qa = QASmall(retriever, faq=faq)
    
    # Test with FAQ match
    result = qa.answer("What is a cat?")
    print("FAQ Test Result:", result)
    
    # Test with retrieval
    result = qa.answer("Information about cats")
    print("Retrieval Test Result:", result)