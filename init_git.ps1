# Display each step with a message
Write-Host "🚀 Starting Git repository initialization..." -ForegroundColor Green

# Initialize Git repository
Write-Host "📦 Initializing Git repository..." -ForegroundColor Cyan
git init

# Add all files
Write-Host "📄 Adding all files to staging area..." -ForegroundColor Cyan
git add .

# Make initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Upload sales dashboard project"

# Set main branch as default
Write-Host "🌿 Setting main branch as default..." -ForegroundColor Cyan
git branch -M main

# Add remote origin
Write-Host "🔗 Adding remote origin..." -ForegroundColor Cyan
git remote add origin https://github.com/gamjagf/sales_dashboard.git

# Push to GitHub
Write-Host "⬆️ Pushing code to GitHub..." -ForegroundColor Cyan
git push -u origin main

Write-Host "✅ Done! Repository initialized and pushed to GitHub." -ForegroundColor Green 