import base64
import os
import time
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List
import random

# Prompts directly in the file for Vercel deployment
PROMPTS = {
    "generate_image": [
        "SYSTEM: Generate a high-quality image based on the appended user prompt. Maintain clarity, coherent lighting, clean composition, and omit all textual overlays or watermarks."
    ],
    "edit_image": [
        "SYSTEM: Apply non-destructive visual transformations guided by the appended user prompt while preserving subject identity, proportions, and core composition. Avoid artifacts, over-saturation, or unintended style drift."
    ],
    "virtual_try_on": [
        "SYSTEM: Perform realistic virtual try-on by blending the product image onto the person image. Maintain anatomical correctness, natural fabric behavior, consistent lighting, and seamless color integration. No distortions or added accessories."
    ],
    "create_ads": [
        "SYSTEM: Produce professional advertisement imagery combining the model and product. Each generation should feel like a distinct ad concept while keeping the product clearly legible, composition balanced, and free of textual elements or logos."
    ],
    "merge_images": [
        "SYSTEM: Merge all provided images into a single coherent output guided by the user prompt. Unify perspective, color temperature, exposure, and shadow logic; remove redundancies; avoid frames, borders, or extraneous artifacts."
    ],
    "generate_scenes": [
        "SYSTEM: Generate extended or reinterpreted scene outputs derived from the uploaded image and optional user prompt. Preserve spatial coherence, plausible lighting, and material consistency while allowing creative environmental variation."
    ],
    "restore_old_image": [
        "SYSTEM: Restore the uploaded aged or damaged image. Remove scratches, noise, stains, and fading while preserving authentic detail, texture, and historical integrity. No stylistic modernization beyond faithful clarity recovery."
    ]
}

def sample_prompts(mode: str, count: int | None = None):
    """Return up to `count` prompts for a mode (all if count is None).
    Safeguards against IndexError if prompt lists are shortened.
    """
    plist = PROMPTS.get(mode, []) or []
    if count is None or count >= len(plist):
        return plist
    return plist[:count]

# === FastAPI Backend for Nano Banana ===
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

app = FastAPI(title="Nano Banana API", description="AI Image Generation and Editing API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def b64encode_file(file: UploadFile):
    data = file.file.read()
    mime = file.content_type or "image/png"
    return base64.b64encode(data).decode('utf-8'), mime

def call_nano_banana(api_key: str, prompt: str, images: List[dict] = None, retries: int = 3, backoff: float = 1.5):
    parts = [{'text': prompt}]
    if images:
        for img in images:
            parts.append({'inlineData': {'data': img['data'], 'mimeType': img['mime']}})

    payload = {'contents': [{'parts': parts}]}
    attempt = 0
    while attempt <= retries:
        res = requests.post(f"{API_URL}?key={api_key}", json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 429:
            # Quota / rate limit – exponential backoff
            if attempt == retries:
                return None, res.text
            sleep_for = backoff ** attempt
            time.sleep(sleep_for)
            attempt += 1
            continue
        if res.status_code != 200:
            return None, res.text
        data = res.json()
        parts_out = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
        for p in parts_out:
            if 'inlineData' in p:
                return p['inlineData']['data'], p['inlineData'].get('mimeType', 'image/png')
        return None, "No image returned"
    return None, "Exhausted retries"

@app.get("/")
def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🍌 Nano Banana Studio API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .method { color: #2196F3; font-weight: bold; }
            .path { color: #4CAF50; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🍌 Nano Banana Studio API</h1>
            <p>AI-powered image generation and editing service</p>
            <a href="/docs">📚 View API Documentation</a>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/generate</span> - Generate images from text
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/edit</span> - Edit existing images
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/virtual_try_on</span> - Virtual try-on
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/create_ads</span> - Create advertisements
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/merge_images</span> - Merge multiple images
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/generate_scenes</span> - Generate scene variations
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <span class="path">/restore_old_image</span> - Restore old images
        </div>
    </body>
    </html>
    """)

@app.post("/generate")
def generate_image(api_key: str = Form(...), prompt: str = Form(...)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    system_prompt = random.choice(PROMPTS["generate_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, mime = call_nano_banana(api_key, full_prompt)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": mime})
    return JSONResponse({"error": mime}, status_code=500)

@app.post("/edit")
def edit_image(api_key: str = Form(...), prompt: str = Form(...), file: UploadFile = File(...)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["edit_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=[{'data': img_data, 'mime': mime}])
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

@app.post("/virtual_try_on")
def virtual_try_on(api_key: str = Form(...), product: UploadFile = File(...), person: UploadFile = File(...), prompt: str = Form("")):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    images = []
    for f in [product, person]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    system_prompt = random.choice(PROMPTS["virtual_try_on"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=images)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

MAX_AD_VARIATIONS = 3
MAX_SCENE_VARIATIONS = 3

@app.post("/create_ads")
def create_ads(api_key: str = Form(...), model: UploadFile = File(...), product: UploadFile = File(...), prompt: str = Form(""), variations: int = Form(None)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    images = []
    for f in [model, product]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    target = variations or MAX_AD_VARIATIONS
    target = max(1, min(target, 3))
    system_prompt = PROMPTS["create_ads"][0]
    base_hints = [
        "lifestyle angle",
        "dramatic lighting",
        "portrait social feed style"
    ]
    results = []
    for i in range(target):
        hint = base_hints[i % len(base_hints)]
        full_prompt = f"{system_prompt} Variation {i+1}: {hint}.".strip()
        if prompt:
            full_prompt += f" User: {prompt.strip()}"
        img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=images)
        if img_b64:
            results.append({'image': img_b64, 'mime': out_mime})
    return JSONResponse({"results": results})

@app.post("/merge_images")
def merge_images(api_key: str = Form(...), files: List[UploadFile] = File(...), prompt: str = Form("")):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    images = []
    for f in files[:5]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    system_prompt = random.choice(PROMPTS["merge_images"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=images)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

@app.post("/generate_scenes")
def generate_scenes(api_key: str = Form(...), scene: UploadFile = File(...), prompt: str = Form(""), variations: int = Form(None)):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    data, mime = b64encode_file(scene)
    target = 3
    system_prompt = PROMPTS["generate_scenes"][0]
    base_hints = [
        "wide cinematic extension",
        "dawn atmosphere",
        "midday clarity"
    ]
    results = []
    for i in range(min(target, 3)):
        hint = base_hints[i % len(base_hints)]
        full_prompt = f"{system_prompt} Variation {i+1}: {hint}.".strip()
        if prompt:
            full_prompt += f" User: {prompt.strip()}"
        img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=[{'data': data, 'mime': mime}])
        if img_b64:
            results.append({'image': img_b64, 'mime': out_mime})
    if len(results) > 3:
        results = results[:3]
    return JSONResponse({"results": results})

@app.post("/restore_old_image")
def restore_old_image(api_key: str = Form(...), file: UploadFile = File(...), prompt: str = Form("")):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["restore_old_image"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=[{'data': img_data, 'mime': mime}])
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

# For Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)