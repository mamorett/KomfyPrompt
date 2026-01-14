#!/usr/bin/env python3
"""
ComfyUI Prompt Extractor - CLI Tool
A simple CLI to extract positive prompts from ComfyUI workflows (JSON) and images (PNG).
"""
import argparse
import sys
import os
import glob
from extractor import PromptExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract prompts from ComfyUI JSON workflows or PNG images.")
    parser.add_argument('files', nargs='+', help='File path(s) or pattern (e.g., *.json, workflow.json)')
    args = parser.parse_args()

    extractor = PromptExtractor()
    
    # Process inputs (handle shell expansion and manual globs)
    all_files = []
    for pattern in args.files:
        # Check if the pattern contains wildcards that weren't expanded by shell
        if any(char in pattern for char in ['*', '?', '[']):
             # Manual globbing for quoted wildcards
             matches = glob.glob(pattern)
             all_files.extend(matches)
        else:
             # Regular file path (already expanded or precise)
             all_files.append(pattern)
    
    # Remove duplicates and resolve paths
    unique_files = sorted(list(set(os.path.abspath(f) for f in all_files if os.path.exists(f))))
    
    if not unique_files:
        print("No valid files found.")
        sys.exit(1)

    for i, file_path in enumerate(unique_files):
        try:
            filename = os.path.basename(file_path)
            result = None
            
            if file_path.lower().endswith('.json'):
                result = extractor.extract_positive_prompts_json(file_path)
            elif file_path.lower().endswith('.png'):
                # Try ComfyUI method first as it's cleaner for workflows
                result = extractor.extract_positive_prompts_comfyui(file_path)
                # Fallback handled within method logic? 
                # Nope, main.py checks both. 
                # Let's match main.py logic: try comfyui, then parameters?
                # Actually main.py UI asks user for mode. 
                # Here we want to "simply print the prompt".
                # If ComfyUI method finds nothing, we could try Parameters?
                # Let's stick to ComfyUI first (workflow/prompt metadata) as it is most similar to JSON.
                if not result or not result.get('positive_prompts'):
                    result_params = extractor.extract_positive_prompts_parameters(file_path)
                    if result_params and result_params.get('positive_prompts'):
                        result = result_params

            if result and result.get('positive_prompts'):
                print(f"=== {filename} ===")
                for prompt in result['positive_prompts']:
                    title = prompt.get('title', 'Untitled')
                    text = prompt.get('text', '').strip()
                    if title and title != 'Untitled':
                        print(f"[{title}]")
                    print(text)
                    print("-" * 40)
                print()
            else:
                # Optional: print that nothing was found
                # print(f"=== {filename} ===\n(No prompts found)\n")
                pass

        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
