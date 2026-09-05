import json

file_path = r"C:\Users\ASUS\.gemini\antigravity-ide\brain\7d128360-cd4b-4ad9-b80b-f0736236d91b\.system_generated\steps\3212\output.txt"
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

screens = data.get("screens", [])
print(f"Total screens in Stitch: {len(screens)}")
for i, s in enumerate(screens):
    title = s.get("title", "Untitled")
    screen_id = s.get("name", "").split("/")[-1]
    print(f"{i+1:02d}. [{screen_id}] {title}")
