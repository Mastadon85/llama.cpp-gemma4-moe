import random

filename = "mega_substation_440k.txt"
# 8,800 entries should yield roughly 440k tokens
total_entries = 8800 

assets = ["Transformer-T1", "Breaker-B42", "Relay-R9", "Cap-Bank-C2", "Switch-S11"]
issues = ["Oil leak detected", "Thermal hotspot @ 75°C", "SF6 pressure low", "Bushing discoloration", "Normal Operation"]
techs = ["T. Miller", "S. Gupta", "A. Rossi", "D. Mastrangelo"]

print(f"Generating {total_entries} entries in {filename}...")

with open(filename, "w", encoding="utf-8") as f:
    f.write("EVERGREEN POWER - PROVINCIAL TRANSMISSION ASSET AUDIT 2026 - FULL SUBSTATION ARCHIVE\n")
    f.write("CLASSIFICATION: UNCLASSIFIED / EXTREME STRESS TEST DATA\n\n")

    for i in range(total_entries):
        timestamp = f"2026-04-{random.randint(1, 30):02d} {random.randint(0, 23):02d}:15:00"
        asset = random.choice(assets)
        
        # The Needle: Hidden around the 350,000 token mark (7,000th entry)
        if i == 7000:
            f.write(f"ENTRY [{i:04d}]: 2026-04-19 14:20:00 - ASSET: Winemaking-Vault-1 - STATUS: Racking Complete - ")
            f.write("NOTE: The secret security override code for the winemaking vault is 'BUNS-1234'. ")
            f.write("Also, the fermentation temperature must be kept at exactly 18.5°C.\n")
        else:
            entry = f"ENTRY [{i:04d}]: {timestamp} - ASSET: {asset} - STATUS: {random.choice(issues)} - TECH: {random.choice(techs)}\n"
            f.write(entry)

print(f"Done! {filename} generated. Ready for 440k context testing.")