import json
import os
import matplotlib

# Use non-GUI backend (fixes Tkinter error on Windows)
matplotlib.use("Agg")

import matplotlib.pyplot as plt

# --------------------------------------------------
# Ensure output folder exists
# --------------------------------------------------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# Load submission results
# --------------------------------------------------
with open(os.path.join(OUTPUT_DIR, "submission.json"), "r", encoding="utf-8") as f:
    results = json.load(f)

total = len(results)

valid_answers = 0
fallback_count = 0

# --------------------------------------------------
# Calculate Metrics
# --------------------------------------------------
for item in results:
    answer = item["answer"].strip()
    sections = item["references"]["sections"]
    pages = item["references"]["pages"]

    if answer == "Not found in the provided textbook.":
        fallback_count += 1
    elif sections and pages:
        valid_answers += 1

invalid_answers = total - valid_answers - fallback_count

grounded_accuracy = (valid_answers / total) * 100 if total > 0 else 0
fallback_rate = (fallback_count / total) * 100 if total > 0 else 0

# --------------------------------------------------
# Print Results
# --------------------------------------------------
print("\n===== RAG Evaluation Summary =====")
print("Total Questions:", total)
print("Valid Grounded Answers:", valid_answers)
print("Fallback Count:", fallback_count)
print("Invalid Cases:", invalid_answers)
print("Grounded Accuracy:", round(grounded_accuracy, 2), "%")
print("Fallback Rate:", round(fallback_rate, 2), "%")

# --------------------------------------------------
# Bar Chart
# --------------------------------------------------
labels = ["Valid Grounded", "Fallback", "Invalid"]
values = [valid_answers, fallback_count, invalid_answers]

plt.figure(figsize=(8, 5))
plt.bar(labels, values)
plt.title("RAG Evaluation Summary")
plt.ylabel("Number of Questions")
plt.savefig(os.path.join(OUTPUT_DIR, "bar_chart.png"))
plt.close()

# --------------------------------------------------
# Pie Chart
# --------------------------------------------------
plt.figure(figsize=(6, 6))
plt.pie(
    [valid_answers, fallback_count],
    labels=["Grounded Answers", "Fallback"],
    autopct="%1.1f%%"
)
plt.title("Grounded Answer Distribution")
plt.savefig(os.path.join(OUTPUT_DIR, "pie_chart.png"))
plt.close()

print("\nCharts saved in output/ folder:")
print(" - bar_chart.png")
print(" - pie_chart.png")
print("===================================")