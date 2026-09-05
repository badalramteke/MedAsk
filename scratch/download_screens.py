import json, urllib.request, os

with open(r'c:\Users\ASUS\OneDrive\Pictures\college 5th sem\SIH\scratch\all_screens_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

html_dir = r'c:\Users\ASUS\OneDrive\Pictures\college 5th sem\SIH\scratch\stitch_screens_html'
os.makedirs(html_dir, exist_ok=True)

success_count = 0
for sid, data in catalog.items():
    url = data.get('downloadUrl')
    title = data.get('title', 'screen').replace('/', '_').replace('\\', '_')
    if url:
        fname = f"{sid[:8]}_{title[:30]}.html"
        out_path = os.path.join(html_dir, fname)
        if not os.path.exists(out_path):
            try:
                urllib.request.urlretrieve(url, out_path)
                success_count += 1
            except Exception as e:
                print(f"Error downloading {sid}: {e}")

print(f"Downloaded {success_count} screen HTML files into {html_dir}")
