import glob, json, os

output_files = glob.glob(r"C:\Users\ASUS\.gemini\antigravity-ide\brain\7d128360-cd4b-4ad9-b80b-f0736236d91b\.system_generated\steps\*\output.txt")
found = {}

for p in output_files:
    try:
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
            if "screens" in content and "projectId" in content:
                data = json.loads(content)
                comps = data.get("outputComponents", [])
                for c in comps:
                    design = c.get("design", {})
                    screens = design.get("screens", [])
                    for s in screens:
                        s_id = s.get("id") or s.get("name", "").split("/")[-1]
                        title = s.get("title", "")
                        if s_id and title:
                            found[s_id] = title
    except Exception:
        pass

print("Generated screens discovered in outputs:")
for s_id, title in found.items():
    print(f"[{s_id}] {title}")
