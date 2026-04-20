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
    num_tokens = 1200000
    needle = "The secret ingredient for the perfect Attention Matching is the Kenilworth Needle."
    needle_pos = 950000
    
    filename = "mega_haystack.txt"
    print(f"Generating {num_tokens} token haystack in {filename}...")
    
    content = generate_haystack(num_tokens, needle, needle_pos)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Haystack generated. Needle at {needle_pos} tokens.")
    
    # Output the test command
    # We assume llama-cli is built and available in build/bin/Release
    model_path = "models/Qwen3.6-35B-A3B-UD-Q3_K_M.gguf"
    
    # Corrected flags based on Step 3
    test_cmd = f".\\llama.cpp\\build\\bin\\Release\\llama-cli.exe -m {model_path} -f {filename} -n 64 --compact --compact-ratio 10 --am-trigger 131072 --am-gpu -p \"What is the secret ingredient for the perfect Attention Matching?\""
    
    print("\nTo run the test, use the following command:")
    print(test_cmd)

if __name__ == "__main__":
    main()
