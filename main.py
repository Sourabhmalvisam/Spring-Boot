import os
import re
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

# === UPDATE BODY STYLE IN MAIN INDEX ===
for style_tag in soup.find_all("style"):
    if "white-space: pre-wrap;" in style_tag.text:
        style_tag.string = style_tag.text.replace("white-space: pre-wrap;", "white-space: nowrap;")

# === PROCESS EACH TOPIC ===
topic_counter = 1
for details in soup.find_all("details"):
    summary_tag = details.find("summary")
    if not summary_tag:
        continue

    # Clean topic title
    raw_title = summary_tag.get_text(" ", strip=True)
    topic_title = re.sub(r"\s+", " ", raw_title)
    safe_folder_name = "".join(c for c in topic_title if c.isalnum() or c in " _-").strip()
    topic_folder = os.path.join(base_dir, safe_folder_name)
    os.makedirs(topic_folder, exist_ok=True)

    # Copy CSS/head from main page
    head_html = soup.head.decode()

    # Create topic HTML with same CSS
    topic_soup = BeautifulSoup(f"<html>{head_html}<body></body></html>", "html.parser")
    topic_body = topic_soup.body
    topic_body.append(topic_soup.new_tag("h1"))
    topic_body.h1.string = topic_title

    # Process images
    for img in details.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        decoded_src = unquote(src)
        img_path = os.path.join(base_dir, decoded_src)
        if os.path.exists(img_path):
            dest_path = os.path.join(topic_folder, os.path.basename(decoded_src))
            shutil.move(img_path, dest_path)
            new_src = os.path.join("..", safe_folder_name, os.path.basename(decoded_src))

            # Replace figure with plain img tag (no href, no style)
            new_img_tag = topic_soup.new_tag("img", src=new_src)
            img.parent.replace_with(new_img_tag)

    # Add remaining content without summary
    for child in details.find_all(recursive=False):
        if child.name != "summary":
            topic_body.append(child)

    # Save topic HTML
    topic_filename = f"topic_{topic_counter}.html"
    topic_filepath = os.path.join(output_dir, topic_filename)
    with open(topic_filepath, "w", encoding="utf-8") as tf:
        tf.write(str(topic_soup))
    topic_counter += 1

    # Replace <details> with link in index
    link_tag = soup.new_tag("a", href=os.path.join("topics", topic_filename))
    link_tag.string = topic_title
    details.replace_with(link_tag)

# === SAVE UPDATED INDEX ===
with open(html_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Done. Figure cleaned, index body style updated, pages created.")
