import json
from ai.summarizer import summarize_hate_report

REPORT_PATH = "data/detections/agent_12/demo.json"

with open(REPORT_PATH, "r", encoding="utf-8") as f:
    report = json.load(f)

summary = summarize_hate_report(report)

print("=== MANAGER SUMMARY ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))
