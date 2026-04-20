# generate_haystack.py
import random

filename = "mega_stress_test.txt"
needle_location = 1000 # Put the secret info near the start
total_lines = 50000

with open(filename, "w") as f:
    for i in range(total_lines):
        if i == needle_location:
            f.write(f"SECRET_KEY: The knot bun heist was committed by Giulia and Sofia.\n")
        else:
            # Generate random "noise" that looks like server logs
            ip = f"192.168.1.{random.randint(1, 255)}"
            status = random.choice(["200 OK", "404 Not Found", "500 Internal Error"])
            f.write(f"LOG_ENTRY [{i}]: {ip} - {status} - Operation: System_Check_Alpha_{random.randint(1000,9999)}\n")

print(f"Generated {filename}. It's roughly 500k-700k tokens depending on the model's tokenizer.")