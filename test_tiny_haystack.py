import os
import random
import sys

def generate_haystack(num_tokens, needle, needle_pos):
    # Rough estimate: 1 token is 4 characters
    total_chars = num_tokens * 4
    haystack = "The quick brown fox jumps over the lazy dog. " * (total_chars // 40)
    
    # Insert needle
    needle_pos_chars = needle_pos * 4
    haystack = haystack[:needle_pos_chars] + "\n" + needle + "\n" + haystack[needle_pos_chars:]
    
    return haystack

def main():
    num_tokens = 50000
    needle = "The secret ingredient for the perfect Attention Matching is the Kenilworth Needle."
    needle_pos = 25000
    question = "What is the secret ingredient for the perfect Attention Matching?"
    
    filename = "tiny_haystack.txt"
    print(f"Generating {num_tokens} token haystack in {filename}...")
    
    content = generate_haystack(num_tokens, needle, needle_pos)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Haystack generated. Needle at {needle_pos} tokens.")
    
    model_path = "models/Qwen3.6-35B-A3B-UD-Q3_K_M.gguf"
    
    # Run in non-interactive mode with -p and --file
    # This usually works to process the file and then the prompt
    test_cmd = f".\\llama.cpp\\build\\bin\\Release\\llama-cli.exe -m {model_path} -f {filename} -p \"{question}\" -n 64 --compact --compact-ratio 10 --am-trigger 10000 --am-gpu -ngl 99 --temp 0"
    
    print("\nTo run the test, use the following command:")
    print(test_cmd)

if __name__ == "__main__":
    main()
