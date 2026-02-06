from ai.hate_detector import detect_hate_from_textfile

file_path = "data/transcripts/agent_12/conv_test123.txt"

report = detect_hate_from_textfile(file_path)

print(report)
