#!/bin/bash

echo "========================================="
echo "DEPLOYING CAR VALUATION DASHBOARD"
echo "========================================="

# Set your GitHub repository name
REPO_NAME="car-valuation-dashboard"
GITHUB_USERNAME="mobiusframeworks"

echo ""
echo "Step 1: Create GitHub repository"
echo "Visit: https://github.com/new"
echo "Repository name: ${REPO_NAME}"
echo "Make it PUBLIC (required for free Streamlit Cloud)"
echo "DO NOT add README or .gitignore"
echo ""
echo "Press Enter when repository is created..."
read

echo ""
echo "Step 2: Pushing to GitHub..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git" 2>/dev/null || git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✓ Successfully pushed to GitHub!"
    echo ""
    echo "========================================="
    echo "NEXT: Deploy to Streamlit Cloud"
    echo "========================================="
    echo ""
    echo "1. Go to: https://share.streamlit.io/"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Fill in:"
    echo "   Repository: ${GITHUB_USERNAME}/${REPO_NAME}"
    echo "   Branch: main"
    echo "   Main file: dashboard.py"
    echo "5. Click 'Deploy!'"
    echo ""
    echo "Your app will be live at:"
    echo "https://car-valuation-dashboard.streamlit.app"
    echo ""
    echo "========================================="
    echo "FEATURES IN YOUR DEPLOYED APP:"
    echo "========================================="
    echo "✓ 339 vehicle listings with 100% clickable URLs"
    echo "✓ Tesla Model Y: 11 listings (2020-2024)"
    echo "✓ Lexus GX: 38 listings (all variants merged)"
    echo "✓ Click dots to open Facebook listings instantly"
    echo "✓ Mobile-friendly design"
    echo "✓ Regression analysis with confidence bands"
    echo ""
else
    echo "✗ Failed to push to GitHub"
    echo "Make sure you've created the repository and have permissions"
fi
