#!/bin/bash

# Display each step with a message
echo "🚀 Starting Git repository initialization..."

# Initialize Git repository
echo "📦 Initializing Git repository..."
git init

# Add all files
echo "📄 Adding all files to staging area..."
git add .

# Make initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Upload sales dashboard project"

# Set main branch as default
echo "🌿 Setting main branch as default..."
git branch -M main

# Add remote origin
echo "🔗 Adding remote origin..."
git remote add origin https://github.com/gamjagf/sales_dashboard.git

# Push to GitHub
echo "⬆️ Pushing code to GitHub..."
git push -u origin main

echo "✅ Done! Repository initialized and pushed to GitHub." 