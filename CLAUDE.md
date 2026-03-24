# automatePublicity

## Project Overview

A local-first pipeline for automatic social media content generation. Given a text description and a content type, it produces ready-to-publish assets: scripts for short-form videos, carousels, and image covers — in English or French.

All processing runs locally (Ollama for LLM, Photoshop for image generation). No external API calls are made for content generation.

---

## Pipeline Architecture

```
INPUT
  description   : str  (subject / brief for the content)
  content_type  : str  ("video" | "carousel")
  platform      : str  (--tiktok | --reels | --shorts)   [video only]
  --french      : flag (output in French instead of English)

        ↓
[OPTIONAL RAG STEP]
  If subpackages/Social-media-researcher/data/videos.xlsx exists:
    → Read transcripts from Excel via openpyxl
    → Write to a temporary text file
    → socialmediaExpert.ingest_file(temp_path)
    (enriches LLM with real trending content: hooks, vocabulary, formats)

        ↓
[CONTENT GENERATION]
  socialmediaExpert.generate_posts(description, platform=...)
    → Returns raw script text (English)

        ↓
[TRANSLATION — only if --french]
  English2french-translator.translate(raw_content)
    → Returns French version of the content

        ↓
[ASSET GENERATION]
  if content_type == "video" and platform == "--reels":
    photoshopConnector.create_reel_cover(name, text, image_path, output_dir) × 3
    → 3 JPEG cover options + PSD source files

  if content_type == "carousel":
    photoshopConnector.create_carousel_repeated(...)  OR
    photoshopConnector.create_carousel_panorama(...)  OR
    photoshopConnector.create_carousel_before_after(...)
    → JPEG slides + PSD source files

        ↓
OUTPUT
  Script saved to:  <weekday_folder>/video/<name>.txt
  Covers saved to:  <weekday_folder>/cover_photo/
  Assets saved to:  <weekday_folder>/assets/
```

---

## Entry Point (to be built)

File: `main.py` at project root.

Expected CLI interface:

```bash
# Video for TikTok (English)
python main.py "5 tips for better sleep" video --tiktok

# Instagram Reels (English) — also generates 3 reel covers
python main.py "Morning routine ideas" video --reels

# YouTube Shorts (English)
python main.py "Quick Python tricks" video --shorts

# Instagram Carousel (English)
python main.py "Before/after skincare" carousel

# Any content type in French
python main.py "Routine matinale" video --reels --french

# Optional: specify output directory
python main.py "Fitness tips" video --tiktok --output-dir 2026-03-24
```

---

## Content Types

### `video`
- Output: a text script formatted for short-form video (hook, body, CTA)
- Platform context passed to socialmediaExpert for appropriate tone/length
- If `--reels`: additionally generate 3 reel cover image options via photoshopConnector

### `carousel`
- Output: slide content + Photoshop-generated image slides
- Three carousel types available:
  - **repeated** — same image repeated across slides with different text
  - **panorama** — one wide image split across slides
  - **before/after** — two images (before and after) with treatment text

---

## Submodule Reference

### photoshopConnector
**Location:** `subpackages/photoshopConnector/`
**Requires:** Licensed Adobe Photoshop installed and running (Windows/macOS)

```python
from photoshopconnector import (
    create_reel_cover,
    create_carousel_repeated,
    create_carousel_panorama,
    create_carousel_before_after,
    create_youtube_thumbnail,
)

# Instagram Reel Cover (1080×1920)
jpeg_path, psd_path = create_reel_cover(
    name="cover_1",
    text="Your hook text",
    image_path="assets/photo.jpg",
    output_dir="cover_photo/",
    auto_crop=True,
)

# Carousel — repeated image
slides = create_carousel_repeated(
    name="carousel",
    texts=["Slide 1 text", "Slide 2 text", "Slide 3 text"],
    image_path="assets/photo.jpg",
    output_dir="assets/",
    auto_crop=True,
)  # → list of (jpeg_path, psd_path)

# Carousel — panorama split
slides = create_carousel_panorama(
    name="panorama",
    image_path="assets/wide_photo.jpg",
    n_slides=3,
    output_dir="assets/",
)  # → list of jpeg_paths

# Carousel — before/after
slides = create_carousel_before_after(
    name="transformation",
    treatment_text="After 30 days",
    before_image="assets/before.jpg",
    after_image="assets/after.jpg",
    output_dir="assets/",
    auto_crop=True,
)
```

### English2french-translator
**Location:** `subpackages/English2french-translator/`
**Requires:** Ollama running locally with `mistral` model

```python
from English2french_translator import translate

french_text = translate("Your English content here")
```

### socialmediaExpert
**Location:** `subpackages/socialmediaExpert/`
**Requires:** Ollama running locally with `llama3.2` and `nomic-embed-text` models

```python
from social_media_expert import SocialMediaExpert

expert = SocialMediaExpert(ollama_model="llama3.2")

# Optional: ingest transcripts for RAG enrichment
expert.ingest_file("transcripts_temp.txt")
expert.ingest_directory("docs/", recursive=True)

# Generate content
posts = expert.generate_posts(
    "Morning routine ideas",
    platforms=["instagram"],  # or "twitter", "linkedin", "facebook"
)
for post in posts:
    print(post.content)
```

Note: socialmediaExpert's platform targets are `instagram`, `twitter`, `linkedin`, `facebook`. For short-video scripts, use `instagram` for Reels, and adapt the prompt with a `--tiktok`/`--shorts` tone modifier.

### Social-media-researcher
**Location:** `subpackages/Social-media-researcher/`
**Used as CLI only** — run before pipeline to populate the Excel knowledge base

```bash
# Research a single video
python -m social_media_researcher "https://www.tiktok.com/@user/video/123"

# Batch research from a file of URLs
python -m social_media_researcher --batch urls.txt

# Output goes to: subpackages/Social-media-researcher/data/videos.xlsx
```

The Excel file at `data/videos.xlsx` stores: url, platform, author, title, description, likes, comments, shares, views, upload_date, duration, **transcript**, processed_at.

**The transcripts column is the key output** — feed it to socialmediaExpert for RAG.

---

## Language Support

Default output language is **English**.

Pass `--french` to generate content in French:
1. Content is first generated in English by socialmediaExpert
2. Then passed through `English2french-translator.translate()` to produce French output
3. All text outputs (scripts, carousel text) are translated; image text layers in Photoshop templates must be updated manually or extended to accept translated strings

---

## Directory Structure

`generateDirectories.py` creates a folder per weekday of the current month:

```
<root>/
  2026-03-03/
    assets/          ← source images, temp files
    video/           ← generated scripts (.txt)
    cover_photo/     ← reel covers and carousel slides
  2026-03-04/
    assets/
    video/
    cover_photo/
  ...
  subpackages/
    photoshopConnector/
    English2french-translator/
    socialmediaExpert/
    Social-media-researcher/
  generateDirectories.py   ← run this at the start of each month
  main.py                  ← pipeline entry point (to be built)
```

---

## Development Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) running locally: `ollama serve`
- Adobe Photoshop (licensed, running) — required only for cover/carousel generation

### Install Ollama models
```bash
ollama pull mistral          # English2french-translator
ollama pull llama3.2         # socialmediaExpert LLM
ollama pull nomic-embed-text # socialmediaExpert embeddings
```

### Initialize submodules
```bash
git submodule update --init --recursive
```

### Install submodule dependencies
```bash
pip install -r subpackages/photoshopConnector/requirements.txt
pip install -r subpackages/English2french-translator/requirements.txt
pip install -r subpackages/Social-media-researcher/requirements.txt
pip install -e subpackages/socialmediaExpert/
```

### Generate monthly folder structure
```bash
python generateDirectories.py
```

### Verify Ollama + socialmediaExpert
```bash
cd subpackages/socialmediaExpert
sme check
```
