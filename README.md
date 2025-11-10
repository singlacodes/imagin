# 🍌 Nano Banana Studio

An AI-powered creative studio that turns your ideas into stunning images using Google's Gemini AI.

## ✨ Features

- **Generate Images** - Create images from text descriptions
- **Edit Images** - Modify existing images with AI
- **Virtual Try-On** - See how products look on people
- **Restore Old Images** - Fix damaged or aged photos

## 🚀 Live Demo

Visit the live application: [Your Vercel URL here]

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup
1. Clone the repository
```bash
git clone <your-repo-url>
cd imagin
```

2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the API server
```bash
python api/main.py
```

5. Open `public/index.html` in your browser or serve it locally

## 🌐 Deployment on Vercel

1. Push your code to GitHub
2. Connect your GitHub repo to Vercel
3. Deploy automatically with the included `vercel.json` configuration

## 📋 API Endpoints

- `POST /api/generate` - Generate images from text
- `POST /api/edit` - Edit existing images  
- `POST /api/virtual_try_on` - Virtual try-on functionality
- `POST /api/restore_old_image` - Restore old/damaged images

## 🔑 Configuration

Add your Gemini API key in the web interface to start using the AI features.

## 📄 License

MIT License - see LICENSE file for details
