import os
import json
import pandas as pd
from tqdm import tqdm
from src.rag_pipeline import answer_question

print("Starting submission generation...")

# ---------------------------
# Create output folder
# ---------------------------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Load queries
# ---------------------------
with open("data/queries.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

print("Total queries:", len(queries))

results = []

for q in tqdm(queries):
    query_id = q["query_id"]
    question = q["question"]

    try:
        answer, context, sections, pages = answer_question(question)
    except Exception as e:
        print(f"Error on ID {query_id}:", e)
        answer = "Not found in the provided textbook."
        context = ""
        sections = []
        pages = []

    results.append({
        "ID": query_id,
        "context": context,
        "answer": answer,
        "references": {
            "sections": sections,
            "pages": pages
        }
    })

# ---------------------------
# Save CSV
# ---------------------------
df = pd.DataFrame(results)
df["references"] = df["references"].apply(json.dumps)
df = df[["ID", "context", "answer", "references"]]

csv_path = os.path.join(OUTPUT_DIR, "submission.csv")
df.to_csv(csv_path, index=False)

print(f"CSV saved at {csv_path}")

# ---------------------------
# Save JSON
# ---------------------------
json_path = os.path.join(OUTPUT_DIR, "submission.json")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"JSON saved at {json_path}")

print("Submission generation completed.")