#!/bin/bash

# Nano Banana Studio - Vercel Deployment Script

echo "🍌 Preparing Nano Banana Studio for Vercel Deployment"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Nano Banana Studio for Vercel"
else
    echo "📦 Adding changes to git..."
    git add .
    git commit -m "Update: Ready for Vercel deployment"
fi

echo ""
echo "✅ Project is ready for Vercel deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to GitHub:"
echo "   git remote add origin <your-github-repo-url>"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to Vercel:"
echo "   - Visit https://vercel.com"
echo "   - Connect your GitHub repository"
echo "   - Import the project"
echo "   - Deploy automatically!"
echo ""
echo "3. Get your Gemini API Key:"
echo "   - Visit https://makersuite.google.com/app/apikey"
echo "   - Create a new API key"
echo "   - Use it in your deployed application"
echo ""
echo "🚀 Your Nano Banana Studio will be live on Vercel!"