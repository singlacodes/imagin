import base64
import os
import time
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import random
from prompts import PROMPTS


def sample_prompts(mode: str, count: int | None = None):
    """Return up to `count` prompts for a mode (all if count is None).
    Safeguards against IndexError if prompt lists are shortened.
    """
    plist = PROMPTS.get(mode, []) or []
    if count is None or count >= len(plist):
        return plist
    return plist[:count]

# === FastAPI Backend for Nano Banana ===
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])  # For Streamlit frontend

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

@app.post("/generate")
def generate_image(api_key: str = Form(...), prompt: str = Form(...)):
    system_prompt = random.choice(PROMPTS["generate_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, mime = call_nano_banana(api_key, full_prompt)
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": mime})
    return JSONResponse({"error": mime}, status_code=500)

@app.post("/edit")
def edit_image(api_key: str = Form(...), prompt: str = Form(...), file: UploadFile = File(...)):
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["edit_image"])
    full_prompt = f"{system_prompt} {prompt}"
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=[{'data': img_data, 'mime': mime}])
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

@app.post("/virtual_try_on")
def virtual_try_on(api_key: str = Form(...), product: UploadFile = File(...), person: UploadFile = File(...), prompt: str = Form("")):
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

MAX_AD_VARIATIONS = int(os.getenv("MAX_AD_VARIATIONS", "3"))
MAX_SCENE_VARIATIONS = int(os.getenv("MAX_SCENE_VARIATIONS", "3"))

@app.post("/create_ads")
def create_ads(api_key: str = Form(...), model: UploadFile = File(...), product: UploadFile = File(...), prompt: str = Form(""), variations: int = Form(None)):
    images = []
    for f in [model, product]:
        data, mime = b64encode_file(f)
        images.append({'data': data, 'mime': mime})
    # Determine how many variations to attempt
    target = variations or MAX_AD_VARIATIONS
    # Clamp to maximum of 3 variations
    target = max(1, min(target, 3))
    system_prompt = PROMPTS["create_ads"][0]
    base_hints = [
        "lifestyle angle",
        "dramatic lighting",
        "portrait social feed style",
        "product-forward macro",
        "cinematic depth",
        "high contrast poster feel",
        "minimal negative space layout",
        "moody editorial",
        "bright commercial",
        "subtle neutral studio"
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
    data, mime = b64encode_file(scene)
    # Force exactly up to 3 images regardless of requested variations
    target = 3
    system_prompt = PROMPTS["generate_scenes"][0]
    base_hints = [
        "wide cinematic extension",
        "dawn atmosphere",
        "midday clarity",
        "night / blue hour mood",
        "stylized painterly reinterpretation",
        "foggy ambient variant",
        "high contrast sunset",
        "rainy ambience",
        "snowy transformation",
        "minimal desaturated look"
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
    # Hard truncate just in case
    if len(results) > 3:
        results = results[:3]
    return JSONResponse({"results": results})

@app.post("/restore_old_image")
def restore_old_image(api_key: str = Form(...), file: UploadFile = File(...), prompt: str = Form("")):
    img_data, mime = b64encode_file(file)
    system_prompt = random.choice(PROMPTS["restore_old_image"])
    full_prompt = system_prompt
    if prompt:
        full_prompt += " " + prompt
    img_b64, out_mime = call_nano_banana(api_key, full_prompt, images=[{'data': img_data, 'mime': mime}])
    if img_b64:
        return JSONResponse({"image": img_b64, "mime": out_mime})
    return JSONResponse({"error": out_mime}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
