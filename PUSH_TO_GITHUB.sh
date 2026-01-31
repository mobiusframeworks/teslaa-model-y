#!/bin/bash
echo "========================================="
echo "PUSHING TO GITHUB"
echo "========================================="
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
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
    echo "   Repository: mobiusframeworks/car-valuation-dashboard"
    echo "   Branch: main"
    echo "   Main file: dashboard.py"
    echo "5. Click 'Deploy!'"
    echo ""
    echo "Your app will be live at:"
    echo "https://car-valuation-dashboard.streamlit.app"
    echo ""
else
    echo ""
    echo "✗ Failed to push"
    echo "Make sure you created the repository at:"
    echo "https://github.com/new"
fi
