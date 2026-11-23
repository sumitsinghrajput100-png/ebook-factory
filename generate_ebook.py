import os
import re
import time
import json
import markdown
import pymupdf as fitz
from dotenv import load_dotenv
from google import genai

print("Starting script")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file.")

client = genai.Client(api_key=api_key)

MODELS = ["gemini-3.5-flash", "gemini-2.0-flash", "gemini-3.8-flash"]

def generate_with_retry(prompt_text):
    for model_name in MODELS:
        for attempt in range(3):
            try:
                return client.models.generate_content(
                    model=model_name,
                    contents=prompt_text
                )
            except Exception as e:
                err = str(e)
                if "404" in err or "429" in err:
                    print(f"{model_name} unavailable/quota hit, switching model...")
                    break
                if "503" in err and attempt < 2:
                    print(f"{model_name} busy (503), waiting 5 seconds...")
                    time.sleep(5)
                elif "503" in err:
                    print(f"{model_name} overloaded, switching model...")
                    break
                else:
                    raise
    raise RuntimeError("All models hit quota or overload. Try again later.")

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

os.makedirs("output", exist_ok=True)
safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", config["title"]).strip("_").lower()

print(f"Generating Ebook: '{config['title']}'...")

# Step 1: Generate Outline
outline_prompt = f"""
Create a structured {config['num_chapters']}-chapter outline for a book titled '{config['title']}'.
Target Audience: {config['target_audience']}
Description: {config['description']}
Objective: {config['objective']}
Return ONLY a list of chapter titles, one per line, without numbering or 'Chapter X:' prefixes.
"""

response = generate_with_retry(outline_prompt)
chapters = [
    re.sub(r"^(Chapter\s*\d+[:.\-\s]*|\d+[:.\-\s]*)", "", line.strip(), flags=re.IGNORECASE)
    for line in response.text.strip().split("\n")
    if line.strip()
][:config["num_chapters"]]

full_markdown = f"# {config['title']}\n\n**Author:** {config['author']}\n\n---\n\n"

# Step 2: Draft Chapters Sequentially
for index, chapter_title in enumerate(chapters, 1):
    print(f"Drafting Chapter {index}/{len(chapters)}: {chapter_title}...")
    chapter_prompt = f"""
    Write Chapter {index}: '{chapter_title}' for the book '{config['title']}'.
    Target Audience: {config['target_audience']}
    Style: Clear, highly educational, easy to read, with practical examples.
    Use Markdown headings and formatting.
    """
    chap_response = generate_with_retry(chapter_prompt)
    full_markdown += f"\n\n# Chapter {index}: {chapter_title}\n\n" + chap_response.text
    time.sleep(2)

# Save Backup Markdown
md_filepath = os.path.join("output", f"{safe_name}.md")
with open(md_filepath, "w", encoding="utf-8") as f:
    f.write(full_markdown)

# Step 3: Render to HTML and Export PDF
print("Compiling print-ready PDF...")
with open("style.css", "r", encoding="utf-8") as css_file:
    css_content = css_file.read()

css_content = re.sub(r"@page\s*\{.*?\}\s*\}", "", css_content, flags=re.DOTALL)
css_content = re.sub(r"@page\s*\{.*?\}", "", css_content, flags=re.DOTALL)

html_content = markdown.markdown(full_markdown, extensions=["tables", "fenced_code"])
full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css_content}</style></head><body>{html_content}</body></html>"

pdf_filepath = os.path.join("output", f"{safe_name}.pdf")
story = fitz.Story(html=full_html)
writer = fitz.DocumentWriter(pdf_filepath)
mediabox = fitz.paper_rect("a4")
where = mediabox + (54, 54, -54, -54)

more = 1
page_count = 0
while more:
    page_count += 1
    device = writer.begin_page(mediabox)
    more, _ = story.place(where)
    story.draw(device, None)
    writer.end_page()
    if page_count > 300:
        break

writer.close()
print(f"Success! Saved {pdf_filepath} ({page_count} pages)")