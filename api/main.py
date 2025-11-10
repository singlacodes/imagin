import base64
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from typing import List, Optional

app = FastAPI(title="Nano Banana API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

PROMPTS = {
    "generate": "Generate a high-quality image based on this prompt:",
    "edit": "Edit this image according to the instructions:",
    "virtual_try_on": "Create a realistic virtual try-on combining these images:",
    "restore": "Restore this old or damaged image:"
}

def encode_image(file: UploadFile) -> tuple[str, str]:
    data = file.file.read()
    mime = file.content_type or "image/png"
    return base64.b64encode(data).decode('utf-8'), mime

def call_gemini(api_key: str, prompt: str, images: Optional[List[dict]] = None) -> tuple[Optional[str], str]:
    parts = [{'text': prompt}]
    if images:
        for img in images:
            parts.append({'inlineData': {'data': img['data'], 'mimeType': img['mime']}})

    payload = {'contents': [{'parts': parts}]}
    
    try:
        response = requests.post(
            f"{API_URL}?key={api_key}", 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            return None, f"API Error: {response.status_code}"
        
        data = response.json()
        candidates = data.get('candidates', [])
        if not candidates:
            return None, "No response from API"
            
        parts_out = candidates[0].get('content', {}).get('parts', [])
        for part in parts_out:
            if 'inlineData' in part:
                return part['inlineData']['data'], part['inlineData'].get('mimeType', 'image/png')
                
        return None, "No image in response"
        
    except requests.RequestException as e:
        return None, f"Request failed: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.get("/")
def home():
    return HTMLResponse("""
    <html><body style="font-family:Arial;max-width:600px;margin:50px auto;padding:20px;">
    <h1>🍌 Nano Banana Studio API</h1>
    <p>AI Image Generation and Editing</p>
    <p><a href="/docs">📚 API Documentation</a></p>
    </body></html>
    """)

@app.post("/generate")
def generate_image(api_key: str = Form(...), prompt: str = Form(...)):
    if not api_key or not prompt:
        raise HTTPException(status_code=400, detail="API key and prompt required")
    
    full_prompt = f"{PROMPTS['generate']} {prompt}"
    img_data, error = call_gemini(api_key, full_prompt)
    
    if img_data:
        return {"image": img_data, "mime": "image/png"}
    return JSONResponse({"error": error}, status_code=500)

@app.post("/edit")
def edit_image(api_key: str = Form(...), prompt: str = Form(...), file: UploadFile = File(...)):
    if not api_key or not prompt:
        raise HTTPException(status_code=400, detail="API key and prompt required")
    
    img_b64, mime = encode_image(file)
    full_prompt = f"{PROMPTS['edit']} {prompt}"
    
    img_data, error = call_gemini(api_key, full_prompt, [{"data": img_b64, "mime": mime}])
    
    if img_data:
        return {"image": img_data, "mime": "image/png"}
    return JSONResponse({"error": error}, status_code=500)

@app.post("/virtual_try_on")
def virtual_try_on(
    api_key: str = Form(...), 
    product: UploadFile = File(...), 
    person: UploadFile = File(...), 
    prompt: str = Form("")
):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    images = []
    for file in [product, person]:
        img_b64, mime = encode_image(file)
        images.append({"data": img_b64, "mime": mime})
    
    full_prompt = f"{PROMPTS['virtual_try_on']} {prompt}".strip()
    img_data, error = call_gemini(api_key, full_prompt, images)
    
    if img_data:
        return {"image": img_data, "mime": "image/png"}
    return JSONResponse({"error": error}, status_code=500)

@app.post("/restore_old_image")
def restore_image(api_key: str = Form(...), file: UploadFile = File(...), prompt: str = Form("")):
    if not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    img_b64, mime = encode_image(file)
    full_prompt = f"{PROMPTS['restore']} {prompt}".strip()
    
    img_data, error = call_gemini(api_key, full_prompt, [{"data": img_b64, "mime": mime}])
    
    if img_data:
        return {"image": img_data, "mime": "image/png"}
    return JSONResponse({"error": error}, status_code=500)

# Vercel handler
handler = app

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