# 🍌 Nano Banana Studio

FastAPI + Streamlit playground for experimenting with Google's Gemini image generation & editing ("nano banana") capabilities. Provides a simple creative studio UI plus a clean backend with multiple image workflows: generation, editing, virtual try-on, ad variants, image merging, scene extension, and restoration.

## Features
- Text-to-image generation
- Prompt-based image editing
- Virtual try-on (product + person composite)
- Multi-variation ad creative generator
- Merge up to 5 images with prompt guidance
- Scene extension / reinterpretation variants (capped at 3)
- Old photo restoration
- Simple randomized system prompts for diversity

## Tech Stack
- Python 3.11+
- FastAPI backend (`backend.py`)
- Streamlit frontend (`frontend.py`)
- `uv` for dependency + runtime management
- Uvicorn ASGI server

## Prerequisites
- Python 3.11 installed
- `uv` installed (https://github.com/astral-sh/uv)
- A valid Gemini API key (set in the UI each session)

Install `uv` if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
(On macOS with Homebrew you can also: `brew install uv`)

## Quick Start
Clone and sync dependencies:
```bash
git clone https://github.com/AIwithhassan/nano-banana-studio.git
cd nano-banana-studio
uv sync
```

Run the FastAPI backend:
```bash
uv run backend.py
```
This starts the API at: http://localhost:8000

Run the Streamlit frontend (in a second terminal):
```bash
uv run streamlit run frontend.py
```
Open the printed local URL (usually http://localhost:8501) and paste your Gemini API key in the sidebar.

## Environment Variables (Optional)
| Variable | Purpose | Default |
|----------|---------|---------|
| `MAX_AD_VARIATIONS` | Upper bound for ad images (hard capped at 3 in code) | 3 |
| `MAX_SCENE_VARIATIONS` | Currently not user-controlled (scenes forced to 3) | 3 |

Export before running if you want to adjust:
```bash
export MAX_AD_VARIATIONS=3
export MAX_SCENE_VARIATIONS=3
```

## API Overview
All endpoints expect `api_key` form field carrying your Gemini key.

### 1. Generate Image
POST `/generate`
Form fields: `api_key`, `prompt`
Returns base64 image.

Example:
```bash
curl -X POST http://localhost:8000/generate \
  -F api_key="$GEMINI_KEY" \
  -F prompt="A cinematic banana spaceship over neon city"
```

### 2. Edit Image
POST `/edit`
Form: `api_key`, `prompt` + file upload `file`
```bash
curl -X POST http://localhost:8000/edit \
  -F api_key="$GEMINI_KEY" \
  -F prompt="Make it watercolor" \
  -F file=@input.png
```

### 3. Virtual Try-On
POST `/virtual_try_on`
Files: `product`, `person`
Optional `prompt`.

### 4. Create Ads (multi-variation)
POST `/create_ads`
Files: `model`, `product`
Optional: `prompt`
Returns JSON `{ results: [ { image, mime }, ... ] }` up to 3.

### 5. Merge Images
POST `/merge_images`
Multiple files field name `files` (up to 5). Optional `prompt`.

### 6. Generate Scenes
POST `/generate_scenes`
File: `scene` + optional `prompt`. Returns up to 3 variations.

### 7. Restore Old Image
POST `/restore_old_image`
File: `file` + optional `prompt`.

## Frontend Usage
1. Start backend
2. Start Streamlit app
3. Enter backend URL (default http://localhost:8000)
4. Paste API key
5. Pick a mode and interact

## Project Structure
```
backend.py      # FastAPI app & endpoints
frontend.py     # Streamlit UI
prompts.py      # System / mode prompt templates
pyproject.toml  # Dependencies & metadata
movie/          # Sample media asset (nano-banana.mp4)
```

## Development Notes
- `prompts.py` contains prompt banks keyed by mode.
- Some routes purposely randomize a system prompt for variety.
- Scene + ad variants are clamped to prevent runaway usage.
- Responses return base64 images directly (no temp files).

## Troubleshooting
| Issue | Fix |
|-------|-----|
| 401/403 or quota errors | Verify API key & usage limits |
| Empty `results` array | Model returned no image; retry with different prompt |
| Streamlit can't reach backend | Confirm backend running at 8000 & URL matches |
| Slow responses | Model rate limiting -> automatic backoff applied |

## Future Ideas
- Local caching layer for identical prompts
- Download button for each generated image
- Async endpoint calls for parallel variants
- Optional persistent key via env var

## License
MIT (add a LICENSE file if desired)

---
Happy creating! 🍌
