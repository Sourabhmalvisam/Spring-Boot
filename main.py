import os
import shutil
from bs4 import BeautifulSoup
from urllib.parse import unquote

# === CONFIG ===
html_file = "index.html"
base_dir = os.path.dirname(os.path.abspath(html_file))
output_dir = os.path.join(base_dir, "topics")
os.makedirs(output_dir, exist_ok=True)

# === LOAD HTML ===
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# === PROCESS EACH TOPIC ===
topic_counter = 1
for details in soup.find_all("details"):
    summary_tag = details.find("summary")
    if not summary_tag:
        continue

    # Clean topic title to remove extra spaces/newlines
    topic_title = summary_tag.get_text(" ", strip=True)
    safe_folder_name = "".join(c for c in topic_title if c.isalnum() or c in " _-").strip()
    topic_folder = os.path.join(base_dir, safe_folder_name)
    os.makedirs(topic_folder, exist_ok=True)

    # Copy CSS/head from main page
    head_html = soup.head.decode()

    # Create new HTML page with original styling
    topic_soup = BeautifulSoup(f"<html>{head_html}<body></body></html>", "html.parser")
    topic_body = topic_soup.body
    topic_body.append(topic_soup.new_tag("h1"))
    topic_body.h1.string = topic_title

    # Move images & update src (relative path from topics folder)
    for img in details.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        decoded_src = unquote(src)
        img_path = os.path.join(base_dir, decoded_src)
        if os.path.exists(img_path):
            dest_path = os.path.join(topic_folder, os.path.basename(decoded_src))
            shutil.move(img_path, dest_path)
            # from /topics/topic_X.html to /<safe_folder_name>/<image>
            img['src'] = os.path.join("..", safe_folder_name, os.path.basename(decoded_src))

    # Add content except summary to topic page
    for child in details.find_all(recursive=False):
        if child.name != "summary":
            topic_body.append(child)

    # Save topic page
    topic_filename = f"topic_{topic_counter}.html"
    topic_filepath = os.path.join(output_dir, topic_filename)
    with open(topic_filepath, "w", encoding="utf-8") as tf:
        tf.write(str(topic_soup))
    topic_counter += 1

    # Replace <details> in main index with link (no extra spaces)
    link_tag = soup.new_tag("a", href=os.path.join("topics", topic_filename))
    link_tag.string = topic_title
    details.replace_with(link_tag)

# === SAVE UPDATED INDEX ===
with open(html_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Done. Extra spaces removed, images linked correctly, pages styled like main index.")
