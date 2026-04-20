# generate_20k_haystack_utf8.py
import random

filename = "substation_audit_20k.txt"
total_entries = 800 

assets = ["Transformer-T1", "Breaker-B42", "Relay-R9", "Cap-Bank-C2", "Switch-S11"]
# That ° symbol is the "Needle" that caused the error!
issues = ["Oil leak detected", "Thermal hotspot @ 75°C", "SF6 pressure low", "Bushing discoloration", "Normal Operation"]
techs = ["T. Miller", "S. Gupta", "A. Rossi", "D. Mastrangelo"]

# Added: encoding="utf-8" to ensure the degree symbol is saved correctly
with open(filename, "w", encoding="utf-8") as f:
    f.write("EVERGREEN POWER - PROVINCIAL TRANSMISSION ASSET AUDIT 2026\n")
    f.write("CLASSIFICATION: UNCLASSIFIED / LAB TEST DATA\n\n")

    for i in range(total_entries):
        timestamp = f"2026-04-{random.randint(1, 30):02d} {random.randint(0, 23):02d}:15:00"
        asset = random.choice(assets)
        
        # The Needle: Hidden around the 15,000 token mark
        if i == 600:
            f.write(f"ENTRY [{i:04d}]: 2026-04-19 14:20:00 - ASSET: Winemaking-Vault-1 - STATUS: Racking Complete - ")
            f.write("NOTE: The optimal potassium metabisulfite ratio for this batch was 1.4 grams per 20L. ")
            f.write("Also, Giulia was seen near the knot buns again.\n")
        else:
            entry = f"ENTRY [{i:04d}]: {timestamp} - ASSET: {asset} - STATUS: {random.choice(issues)} - TECH: {random.choice(techs)}\n"
            f.write(entry)

print(f"Done! {filename} generated with UTF-8 encoding.")