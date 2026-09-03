import os, glob, json

output_files = glob.glob(r'C:\Users\ASUS\.gemini\antigravity-ide\brain\7d128360-cd4b-4ad9-b80b-f0736236d91b\.system_generated\steps\*\output.txt')
all_screens = {}

for p in output_files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'htmlCode' in content and 'projects/16353399717353515011' in content:
                d = json.loads(content)
                screens = []
                if 'screens' in d:
                    screens.extend(d['screens'])
                if 'outputComponents' in d:
                    for comp in d['outputComponents']:
                        if 'design' in comp and 'screens' in comp['design']:
                            screens.extend(comp['design']['screens'])
                for s in screens:
                    s_id = s.get('id') or s.get('name', '').split('/')[-1]
                    title = s.get('title', 'Untitled')
                    html_info = s.get('htmlCode', {})
                    dl_url = html_info.get('downloadUrl', '') if isinstance(html_info, dict) else ''
                    if s_id and s_id not in all_screens:
                        all_screens[s_id] = {
                            'title': title,
                            'downloadUrl': dl_url,
                            'width': s.get('width'),
                            'height': s.get('height')
                        }
    except Exception:
        pass

print(f"Total unique screens captured: {len(all_screens)}")
with open(r'c:\Users\ASUS\OneDrive\Pictures\college 5th sem\SIH\scratch\all_screens_catalog.json', 'w', encoding='utf-8') as out:
    json.dump(all_screens, out, indent=2)

for sid, info in sorted(all_screens.items(), key=lambda x: x[1]['title']):
    has_url = "YES" if info['downloadUrl'] else "NO"
    print(f"- [{sid[:8]}] {info['title']} (HTML: {has_url})")
