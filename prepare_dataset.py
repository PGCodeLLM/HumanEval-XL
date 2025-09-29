#!/usr/bin/env python3
"""
Prepare HumanEval-XL dataset for inference by adding completion instructions and converting format
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def load_problems(data_file: Path) -> List[Dict[str, Any]]:
    """Load problems from a JSONL file"""
    problems = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                problems.append(json.loads(line))
    return problems

def prepare_for_inference(problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prompt to generate uncompleted part only"""
    inference_data = []

    # Instruction to add to each prompt
    completion_instruction = "Complete the body of the method below. Do not add imports, classes, or extra braces.\n"

    for problem in problems:
        # Add completion instruction to the beginning of the prompt
        enhanced_prompt = completion_instruction + problem["prompt"]

        # Convert to eval-cli format with 'prompt' key (matching the run script)
        inference_item = {
            "task_id": problem["task_id"],
            "prompt": enhanced_prompt,  # Use 'prompt' key to match run script
            "language": problem["language"],
            "natural_language": problem["natural_language"],
            "entry_point": problem["entry_point"],
            "test": problem["test"],
            "canonical_solution": problem.get("canonical_solution", "")
        }
        inference_data.append(inference_item)

    return inference_data

def main():
    parser = argparse.ArgumentParser(description="Prepare HumanEval-XL dataset for inference")
    parser.add_argument("--programming_language", type=str, required=True,
                       choices=["python", "java", "javascript", "typescript", "go", "csharp",
                               "php", "ruby", "kotlin", "scala", "swift", "perl"],
                       help="Programming language")
    parser.add_argument("--natural_language", type=str, required=True,
                       choices=["English", "Russian", "Chinese", "German", "Spanish", "French",
                               "Italian", "Portuguese", "Greek", "Hungarian", "Dutch", "Finnish",
                               "Indonesian", "Turkish", "Arabic", "Vietnamese", "Bulgarian",
                               "Persian", "Malay", "Hebrew", "Estonian", "Tagalog", "Afrikaans"],
                       help="Natural language")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="Output directory for processed dataset")

    args = parser.parse_args()

    # Find the data file
    script_dir = Path(__file__).parent
    data_file = script_dir / "data" / args.programming_language / f"{args.natural_language}.jsonl"

    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        return 1

    print(f"Loading problems from: {data_file}")
    problems = load_problems(data_file)
    print(f"Loaded {len(problems)} problems")

    # Prepare for inference
    inference_data = prepare_for_inference(problems)

    # Write output to centralized location with directory structure
    output_dir = Path(args.output_dir)
    prog_lang_dir = output_dir / args.programming_language
    prog_lang_dir.mkdir(parents=True, exist_ok=True)

    output_path = prog_lang_dir / f"{args.natural_language}.jsonl"

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in inference_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Dataset prepared for inference: {output_path}")
    print(f"Total items: {len(inference_data)}")
    print(f"Enhanced prompts with completion instruction added")

    return 0

if __name__ == "__main__":
    exit(main())
