import csv, os, hashlib
from rapidfuzz import fuzz

BASE = os.path.dirname(__file__)

def norm(s):
    return s.strip().lower()

def make_hash(r):
    return hashlib.sha256(f"{norm(r['name'])}|{norm(r['email'])}".encode()).hexdigest()

def classify(row, unique):
    flagged = False
    for u in unique:
        if fuzz.ratio(norm(row["name"]), norm(u["name"])) >= 85:
            if norm(row["email"]) == norm(u["email"]) or row["phone"].strip() == u["phone"].strip():
                return "near_duplicate"
            flagged = True  # similar name, different identity
    return "false_positive" if flagged else "unique"

def save(filename, rows, fields):
    with open(os.path.join(BASE, filename), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

seen, unique, duplicates = set(), [], []

with open(os.path.join(BASE, "data.csv")) as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    for row in reader:
        h = make_hash(row)
        if h in seen:
            row["status"] = "exact_duplicate"
            duplicates.append(row)
            continue
        status = classify(row, unique)
        row["status"] = status
        if status == "near_duplicate":
            duplicates.append(row)
        else:  # unique or false_positive -> keep
            seen.add(h)
            unique.append(row)

save("unique.csv", unique, fields + ["status"])
save("duplicates.csv", duplicates, fields + ["status"])

print("Unique:", len(unique), "| Duplicates:", len(duplicates))
print("False positives kept:", sum(1 for r in unique if r["status"] == "false_positive"))