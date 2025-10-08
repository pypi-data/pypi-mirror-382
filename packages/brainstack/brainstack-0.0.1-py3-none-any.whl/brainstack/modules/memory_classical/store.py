import json
import hashlib
from typing import Dict, List, Iterator, Optional
from pathlib import Path
import os
from brainstack.utils.io import load_text

def chunk_text(text: str, max_tokens: int = 120) -> List[str]:
    """Split text into chunks with approximately max_tokens tokens.

    Args:
        text: Input text to chunk.
        max_tokens: Approximate number of tokens per chunk (whitespace-based).

    Returns:
        List of text chunks.
    """
    if not text.strip():
        return []
    
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0
    
    for word in words:
        current_chunk.append(word)
        current_count += 1
        if current_count >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

class CorpusStore:
    """Append-only JSONL corpus store with chunking and metadata."""
    
    def __init__(self, path: str) -> None:
        """Initialize store with a JSONL file path.

        Args:
            path: Path to JSONL file; created if it doesn't exist.
        """
        self.path = Path(path)
        from brainstack.utils.io import ensure_dir
        ensure_dir(self.path.parent)
        if not self.path.exists():
            self.path.touch()
        self._index: Dict[str, bool] = {}  # id -> is_deleted
        self._load_index()

    def _load_index(self) -> None:
        """Load index from JSONL file, tracking deleted records."""
        self._index.clear()
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if 'id' in record:
                            self._index[record['id']] = record.get('deleted', False)
        except json.JSONDecodeError:
            pass  # Empty or corrupt file, start fresh

    def _generate_id(self, text: str, meta: Optional[Dict] = None) -> str:
        """Generate a unique ID for a text and metadata pair.

        Args:
            text: Input text.
            meta: Optional metadata dictionary.

        Returns:
            First 12 characters of SHA1 hash of text + JSON-serialized metadata.
        """
        meta_str = json.dumps(meta or {}, sort_keys=True)
        hash_input = (text + meta_str).encode('utf-8')
        return hashlib.sha1(hash_input).hexdigest()[:12]

    def add(self, text: str, meta: Optional[Dict] = None) -> List[str]:
        """Add text to the store, chunking if needed, and return record IDs.

        Args:
            text: Input text to store.
            meta: Optional metadata dictionary.

        Returns:
            List of record IDs for the added chunks.
        """
        chunks = chunk_text(text)
        if not chunks:
            return []
        
        record_ids = []
        ts = int(os.path.getmtime(self.path) * 1000) if self.path.exists() else 0
        
        with open(self.path, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                record_id = self._generate_id(chunk, meta)
                if record_id not in self._index or self._index[record_id]:
                    record = {
                        "id": record_id,
                        "text": chunk,
                        "meta": meta or {},
                        "ts": ts
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
                    self._index[record_id] = False
                    record_ids.append(record_id)
        
        return record_ids

    def add_file(self, path: str, meta: Optional[Dict] = None) -> List[str]:
        """Add text from a file to the store, chunking if needed.

        Args:
            path: Path to text file.
            meta: Optional metadata dictionary.

        Returns:
            List of record IDs for the added chunks.
        """
        text = load_text(path)
        return self.add(text, meta)

    def iter_records(self) -> Iterator[Dict]:
        """Iterate over non-deleted records in the store.

        Yields:
            Records as dictionaries with id, text, meta, ts.
        """
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if 'id' in record and not record.get('deleted', False):
                            yield record
        except json.JSONDecodeError:
            pass  # Skip corrupt lines

    def load_all(self) -> List[Dict]:
        """Load all non-deleted records from the store.

        Returns:
            List of records as dictionaries.
        """
        return list(self.iter_records())

    def delete(self, id: str) -> bool:
        """Mark a record as deleted by appending a tombstone.

        Args:
            id: Record ID to delete.

        Returns:
            True if the record existed and was not already deleted, False otherwise.
        """
        if id not in self._index or self._index[id]:
            return False
        
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"id": id, "deleted": True}) + '\n')
        self._index[id] = True
        return True

if __name__ == "__main__":
    # Test CorpusStore
    import tempfile
    from brainstack.utils.io import ensure_dir
    
    # Create a temporary JSONL file
    temp_dir = Path(tempfile.gettempdir()) / "brainstack_test"
    ensure_dir(temp_dir)
    temp_file = temp_dir / "test_store.jsonl"
    
    # Initialize store
    store = CorpusStore(str(temp_file))
    
    # Add two texts
    ids1 = store.add("This is a test sentence about cats.", {"source": "test1"})
    ids2 = store.add("Another sentence about dogs and cats.", {"source": "test2"})
    
    # Iterate and count records
    records = list(store.iter_records())
    print(f"Added {len(ids1)} chunk(s) for text 1: {ids1}")
    print(f"Added {len(ids2)} chunk(s) for text 2: {ids2}")
    print(f"Total records: {len(records)}")
    
    # Print first record
    if records:
        print(f"First record: {records[0]}")
    
    # Clean up
    if temp_file.exists():
        temp_file.unlink()