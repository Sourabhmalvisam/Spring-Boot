import os
import shutil
from bs4 import BeautifulSoup
from urllib.parse import unquote

# === CONFIG ===
html_file = "index.html"  # Your HTML file name
base_dir = os.path.dirname(os.path.abspath(html_file))  # Folder where HTML & images are

# === PARSE HTML ===
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# === LOOP OVER TOPICS ===
for details in soup.find_all("details"):
    summary_tag = details.find("summary")
    if not summary_tag:
        continue

    # Folder name from summary text (clean it)
    folder_name = summary_tag.get_text(strip=True)
    safe_folder_name = "".join(c for c in folder_name if c.isalnum() or c in " _-").strip()
    topic_folder = os.path.join(base_dir, safe_folder_name)

    os.makedirs(topic_folder, exist_ok=True)

    img_tags = details.find_all("img")
    counter = 1  # numbering start from 1 for each topic

    for img in img_tags:
        src = img.get("src")
        if not src:
            continue

        decoded_src = unquote(src)  # decode %20 to spaces
        img_path = os.path.join(base_dir, decoded_src)

        if os.path.exists(img_path):
            ext = os.path.splitext(decoded_src)[1]  # keep original extension (.png, .jpg)
            new_name = f"{counter}{ext}"
            dest_path = os.path.join(topic_folder, new_name)
            shutil.move(img_path, dest_path)
            print(f"Moved {decoded_src} → {dest_path}")
            counter += 1
        else:
            print(f"⚠ Image not found: {img_path}")

print("✅ Done. Images moved and renamed with numbering per folder.")
