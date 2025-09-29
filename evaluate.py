#!/usr/bin/env python3
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# for completion, we only need the completion code without any <think><think/> tags or ```language\n``` wrapper
# e.g. <think>something</think>```python\ncode\n``` will become code
def process_completions(completion: str, programming_language: str) -> str:
    """Process completion to remove any markdown wrapper or think tags and think content"""
    # Remove <think>...</think> tags and their content
    while '<think>' in completion and '</think>' in completion:
        start = completion.index('<think>')
        end = completion.index('</think>') + len('</think>')
        completion = completion[:start] + completion[end:]

    # Remove ```language\n ... \n``` markdown code blocks
    if '```' in completion:
        parts = completion.split('```')
        if len(parts) >= 3:
            # Join all parts except the first and last (which are outside code blocks)
            completion = ''.join(parts[1:-1]).strip()
        else:
            # If there's only one code block, take the content inside it
            completion = parts[1].strip()

    # remove leading language declaration if exists
    lang_prefix = f"{programming_language}\n"
    if completion.startswith(lang_prefix):
        completion = completion[len(lang_prefix):]

    return completion.strip()


def convert_inference_to_samples(inference_file: Path, programming_language: str) -> List[Dict[str, Any]]:
    """Convert eval-cli inference results to HumanEval-XL sample format"""
    samples = []

    with open(inference_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                item = json.loads(line)
                completions = item.get("completion", [])
                # Handle case where completion is a string instead of list
                if isinstance(completions, str):
                    completions = [completions]
                for completion in completions:
                    sample = {
                        "task_id": item["task_id"],
                        "completion": process_completions(completion, programming_language),
                        "language": programming_language
                    }
                    samples.append(sample)

    return samples

def main():
    parser = argparse.ArgumentParser(description="Evaluate HumanEval-XL inference results")
    parser.add_argument("--experiment_id", type=str, required=True,
                       help="Experiment ID")
    parser.add_argument("--programming_language", type=str, required=True,
                       help="Programming language")
    parser.add_argument("--natural_language", type=str, required=True,
                       help="Natural language")
    parser.add_argument("--num_workers", type=int, help="Number of parallel workers")
    parser.add_argument("--n_samples", type=int, help="Number of samples to evaluate")
    parser.add_argument("--inference_file", type=str, required=True,
                       help="Inference results file")
    parser.add_argument("--evaluation_dir", type=str, required=True,
                       help="Evaluation output directory")

    args = parser.parse_args()

    inference_file = Path(args.inference_file)
    evaluation_dir = Path(args.evaluation_dir)
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    print(f"Converting inference results from: {inference_file}")

    # Convert inference results to HumanEval-XL sample format
    samples = convert_inference_to_samples(inference_file, args.programming_language)
    print(f"Converted {len(samples)} samples")

    # Write samples file
    samples_file = evaluation_dir / "samples.jsonl"
    with open(samples_file, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

    print(f"Samples file created: {samples_file}")

    # Find the problem file
    script_dir = Path(__file__).parent
    problem_file = script_dir / "data" / args.programming_language / f"{args.natural_language}.jsonl"

    if not problem_file.exists():
        print(f"Error: Problem file not found: {problem_file}")
        return 1

    print(f"Using problem file: {problem_file}")

    # Run HumanEval-XL evaluation
    print("Running HumanEval-XL evaluation...")

    cmd = [
        "python", "-m", "mxeval.evaluate_functional_correctness",
        str(samples_file),
        "--problem_file", str(problem_file),
    ]
    if args.num_workers:
        cmd += ["--n_workers", str(args.num_workers)]
    if args.n_samples and args.n_samples > 1:
        cmd += "--k", f"1,{args.n_samples}"

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True)

    if result.returncode != 0:
        print("Evaluation failed:")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return 1

    print("Evaluation completed successfully")
    print(f"STDOUT: {result.stdout}")

    # Move result files to evaluation directory
    passatk_file = Path(str(samples_file) + "_passatk.json")
    results_file = Path(str(samples_file) + "_results.jsonl")

    if passatk_file.exists():
        # Load the pass@k results and convert numpy types to Python types
        with open(passatk_file, 'r') as f:
            content = f.read().strip()
            try:
                passatk_results = json.loads(content)
            except json.JSONDecodeError:
                # Handle numpy types by evaluating and converting
                import numpy as np
                passatk_results = eval(content)

        # Convert numpy types to Python types for valid JSON
        cleaned_results = {}
        for key, value in passatk_results.items():
            if hasattr(value, 'item'):  # numpy scalar
                cleaned_results[key] = value.item()
            elif isinstance(value, (np.integer, np.floating)):
                cleaned_results[key] = float(value)
            else:
                cleaned_results[key] = value

        # Save the cleaned results
        final_passatk = evaluation_dir / "evaluation_results.json"
        with open(final_passatk, 'w') as f:
            json.dump(cleaned_results, f, indent=2)

        # Remove the original file
        passatk_file.unlink()
        print(f"Pass@k results: {final_passatk}")

    if results_file.exists():
        final_results = evaluation_dir / "evaluation_results.jsonl"
        results_file.rename(final_results)
        print(f"Detailed results: {final_results}")

    # Create summary metadata
    summary = {
        "experiment_id": args.experiment_id,
        "programming_language": args.programming_language,
        "natural_language": args.natural_language,
        "total_samples": len(samples),
        "evaluation_completed": True
    }

    # Include pass@k results if available
    if (evaluation_dir / "evaluation_results.json").exists():
        with open(evaluation_dir / "evaluation_results.json", 'r') as f:
            content = f.read().strip()
            try:
                passatk_results = json.loads(content)
            except json.JSONDecodeError:
                passatk_results = eval(content)
            summary["pass_at_k"] = passatk_results

    print(f"Evaluation summary: {summary}")
    return 0

if __name__ == "__main__":
    exit(main())

