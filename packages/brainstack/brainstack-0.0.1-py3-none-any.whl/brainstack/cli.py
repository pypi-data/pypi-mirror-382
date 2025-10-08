import argparse
from pathlib import Path
import yaml
import json
from brainstack.main import run_pipeline
from brainstack.modules.memory_classical.store import CorpusStore

def main():
    """CLI entrypoint for Brainstack."""
    parser = argparse.ArgumentParser(description="Brainstack CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # 'run' command
    run_parser = subparsers.add_parser("run", help="Run the Brainstack pipeline")
    run_parser.add_argument("--text", type=str, help="Input text query")
    run_parser.add_argument("--image", type=str, help="Path to input image")
    run_parser.add_argument("--config", type=str, default=None, 
                           help="Path to YAML config file (e.g., configs/mvp_fast.yml)")

    # 'index' command
    index_parser = subparsers.add_parser("index", help="Add a file to the corpus")
    index_parser.add_argument("--file", type=str, required=True, help="Path to text file to index")
    index_parser.add_argument("--label", type=str, default="", help="Optional label for the file")

    args = parser.parse_args()

    if args.command == "run":
        # Load config if provided
        config = None
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                print(f"Error: Config file {args.config} not found.")
                return
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        
        # Run pipeline
        result = run_pipeline(text=args.text, image=args.image, config=config)
        
        # Print result
        print("Answer:", result["answer"])
        print("Debug:")
        print(f"  Activated Modules: {result['debug']['activated_modules']}")
        print("  Latency Breakdown:")
        for entry in result['debug']['latency_breakdown']:
            print(f"    {entry['module']}: {entry['ms']}ms")
        print(f"  Router Output: {result['debug']['router']}")
        print(f"  Seeds: {result['debug']['seeds']}")
        
        # Print full integrator output for debugging
        print("\nFull Integrator Output:")
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "index":
        # Initialize CorpusStore
        corpus_dir = Path("data/corpus")
        corpus_dir.mkdir(parents=True, exist_ok=True)
        corpus_store = CorpusStore(str(corpus_dir / "store.jsonl"))
        
        # Add file to corpus
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File {args.file} not found.")
            return
        try:
            corpus_store.add_file(str(file_path), meta={"label": args.label})
            print(f"Indexed {args.file} with label '{args.label}' to {corpus_store.path}")
        except Exception as e:
            print(f"Error indexing {args.file}: {e}")

if __name__ == "__main__":
    main()