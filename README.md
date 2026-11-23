

# Ebook Factory

An automated local Python pipeline that generates structured, multi-chapter ebooks using the Google Gemini API and compiles them into styled, print-ready A4 PDFs via PyMuPDF.

## Features
- **Automated Outline & Chapter Drafting:** Generates a full chapter outline and drafts each chapter sequentially from a single JSON configuration.
- **Built-in Model Fallback & Retry Logic:** Automatically handles temporary API spikes (`503`) and switches across Gemini models if quota limits (`429`) are reached.
- **Markdown Backup:** Saves the complete raw manuscript as a `.md` file inside `output/` before rendering.
- **Zero-Dependency PDF Rendering:** Converts Markdown to styled HTML and exports clean A4 PDFs using `pymupdf` (`fitz`) and custom CSS (`style.css`), automatically stripping unsupported `@page` rules.

## Project Structure
```text
ebook-factory/
├── generate_ebook.py   # Main pipeline: outline -> chapters -> Markdown -> PDF
├── compile_pdf.py      # Standalone compiler to re-render existing .md files to PDF
├── config.json         # Book metadata (title, author, chapters, audience, objective)
├── style.css           # Custom typography and layout styling for PDF export
├── requirements.txt    # Python dependencies
├── .env                # Local API key storage (excluded from Git)
└── output/             # Generated .md and .pdf ebooks (excluded from Git)
Setup & Installation
Clone the repository:

git clone https://github.com/sumitsinghrajput100-png/ebook-factory.git
cd ebook-factory

Install dependencies:

pip install -r requirements.txt

Configure your API key:
Create a .env file in the root folder and add your Google Gemini API key:

GEMINI_API_KEY=your_gemini_api_key_here
Usage
1. Configure Your Book
Edit config.json with your desired topic and structure:n
{
"title": "The AI Agent Blueprint: Building Autonomous Workflows Without Code",
"author": "Sumit Singh",
"num_chapters": 7,
"target_audience": "Solopreneurs, freelancers, and digital creators",
"description": "A step-by-step tactical guide covering autonomous AI agent architecture and no-code workflow automation.",
"objective": "Equip readers to design, deploy, and scale reliable no-code AI agent workflows."
}


### 2. Generate the Ebook
Run the main pipeline:
```bash
python generate_ebook.py

Both the .md manuscript and final .pdf will be saved inside the output/ folder.
3. Re-compile PDF Only (Optional)
If you tweak style.css and want to regenerate the PDF from an existing Markdown draft without making new API calls:

python compile_pdf.py

