import streamlit as st
import requests
import base64

st.sidebar.title("⚙️ Settings")
API_BASE = st.sidebar.text_input("Enter your FastAPI backend URL", value="http://localhost:8000")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

st.title("🍌 Nano Banana Studio")
st.markdown("Welcome to your creative image studio! Select a mode below to get started.")

mode = st.selectbox("Select Mode", [
    # Beginner
    "📝 Generate Image with Text  •  Beginner",
    "✏️ Edit Image with Prompt  •  Beginner",
    # Advanced
    "👗 Virtual Try On  •  Advanced",
    "🔧 Restore Old Image  •  Advanced",
    # Professional
    "📢 Create Ads  •  Professional",
    "🔗 Merge Images  •  Professional",
    "🎭 Generate Scenes  •  Professional",
])

def display_image(img_b64):
    img_bytes = base64.b64decode(img_b64)
    st.image(img_bytes)

if mode == "📝 Generate Image with Text  •  Beginner":
    prompt = st.text_area("Enter prompt")
    if st.button("Generate"):
        resp = requests.post(f"{API_BASE}/generate", data={'api_key': api_key, 'prompt': prompt})
        if resp.status_code == 200:
            display_image(resp.json()['image'])
        else:
            st.error(resp.text)

elif mode == "✏️ Edit Image with Prompt  •  Beginner":
    prompt = st.text_area("Enter edit prompt")
    file = st.file_uploader("Upload an image", key="edit_image_file")
    if file:
        st.image(file, caption="Preview of uploaded image", width=120)
    if st.button("Edit") and file:
        resp = requests.post(f"{API_BASE}/edit", data={'api_key': api_key, 'prompt': prompt}, files={'file': file})
        if resp.status_code == 200:
            display_image(resp.json()['image'])
        else:
            st.error(resp.text)

elif mode == "👗 Virtual Try On  •  Advanced":
    cols = st.columns(2)
    product = st.file_uploader("Upload product image", key="virtual_tryon_product")
    if product:
        with cols[0]:
            st.image(product, caption="Product", width=120)
    person = st.file_uploader("Upload person image", key="virtual_tryon_person")
    if person:
        with cols[1]:
            st.image(person, caption="Person", width=120)
    prompt = st.text_area("Optional prompt for virtual try-on", key="virtual_tryon_prompt")
    if st.button("Try On") and product and person:
        files = {'product': product, 'person': person}
        data = {'api_key': api_key, 'prompt': prompt}
        resp = requests.post(f"{API_BASE}/virtual_try_on", data=data, files=files)
        if resp.status_code == 200:
            display_image(resp.json()['image'])
        else:
            st.error(resp.text)

elif mode == "📢 Create Ads  •  Professional":
    cols = st.columns(2)
    model = st.file_uploader("Upload model image", key="create_ads_model")
    if model:
        with cols[0]:
            st.image(model, caption="Model", width=120)
    product = st.file_uploader("Upload product image", key="create_ads_product")
    if product:
        with cols[1]:
            st.image(product, caption="Product", width=120)
    prompt = st.text_area("Optional prompt for ads (e.g., 'Make it colorful and modern')", key="create_ads_prompt")
    if st.button("Create Ads") and model and product:
        files = {'model': model, 'product': product}
        data = {'api_key': api_key, 'prompt': prompt}
        resp = requests.post(f"{API_BASE}/create_ads", data=data, files=files)
        if resp.status_code == 200:
            for img in resp.json().get('results', []):
                display_image(img['image'])
        else:
            st.error(resp.text)

elif mode == "🔗 Merge Images  •  Professional":
    uploaded_files = st.file_uploader("Upload up to 5 images", accept_multiple_files=True, key="merge_images_files")
    if uploaded_files:
        cols = st.columns(len(uploaded_files[:5]))
        for idx, f in enumerate(uploaded_files[:5]):
            with cols[idx]:
                st.image(f, caption=None, width=120)
    prompt = st.text_area("Optional prompt for merging", key="merge_images_prompt")
    if st.button("Merge") and uploaded_files:
        files = [('files', f) for f in uploaded_files[:5]]
        data = {'api_key': api_key, 'prompt': prompt}
        resp = requests.post(f"{API_BASE}/merge_images", data=data, files=files)
        if resp.status_code == 200:
            display_image(resp.json()['image'])
        else:
            st.error(resp.text)

elif mode == "🎭 Generate Scenes  •  Professional":
    scene = st.file_uploader("Upload scene image", key="generate_scenes_scene")
    if scene:
        st.image(scene, caption="Preview of scene image", width=120)
    prompt = st.text_area("Optional prompt for scenes", key="generate_scenes_prompt")
    if st.button("Generate Scenes") and scene:
        data = {'api_key': api_key, 'prompt': prompt}
        resp = requests.post(f"{API_BASE}/generate_scenes", data=data, files={'scene': scene})
        if resp.status_code == 200:
            for img in resp.json().get('results', []):
                display_image(img['image'])
        else:
            st.error(resp.text)

elif mode == "🔧 Restore Old Image  •  Advanced":
    file = st.file_uploader("Upload old image to restore", key="restore_old_image_file")
    if file:
        st.image(file, caption="Preview of old image", width=120)
    prompt = st.text_area("Optional prompt for restoration", key="restore_old_image_prompt")
    if st.button("Restore Image") and file:
        data = {'api_key': api_key, 'prompt': prompt}
        resp = requests.post(f"{API_BASE}/restore_old_image", data=data, files={'file': file})
        if resp.status_code == 200:
            display_image(resp.json()['image'])
        else:
            st.error(resp.text)
