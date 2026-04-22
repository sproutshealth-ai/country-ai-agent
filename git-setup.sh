#!/bin/bash

# Git Setup Script for Country Information AI Agent
# This script helps you initialize Git and push to GitHub

echo "=================================="
echo "Git Setup for Country Info Agent"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    echo "Please install Git first: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Check if already a git repo
if [ -d ".git" ]; then
    echo "⚠️  Git repository already exists"
    echo ""
    read -p "Do you want to reinitialize? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping git init"
    else
        rm -rf .git
        git init
        echo "✅ Git reinitialized"
    fi
else
    git init
    echo "✅ Git initialized"
fi

echo ""
echo "Creating initial commit..."

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Country Information AI Agent

- Implemented LangGraph-based agent with 3 nodes
- Intent identification, tool invocation, and answer synthesis
- FastAPI web application with UI
- REST Countries API integration
- Production-ready with error handling
- Comprehensive documentation
- Multiple deployment options
- Docker support
- CI/CD ready

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo "✅ Initial commit created"
echo ""

# Get GitHub repo URL
echo "Now let's connect to GitHub..."
echo ""
echo "Steps:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: Country-Information-AI-Agent"
echo "3. Do NOT initialize with README, .gitignore, or license"
echo "4. Copy the repository URL"
echo ""

read -p "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "⚠️  No URL provided. You can add it later with:"
    echo "git remote add origin <your-repo-url>"
    echo "git push -u origin main"
else
    git remote add origin "$REPO_URL"
    echo "✅ Remote origin added"
    echo ""

    # Check if main or master
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" != "main" ]; then
        git branch -M main
        echo "✅ Renamed branch to 'main'"
    fi

    echo "Pushing to GitHub..."
    git push -u origin main

    if [ $? -eq 0 ]; then
        echo ""
        echo "=================================="
        echo "🎉 Success!"
        echo "=================================="
        echo ""
        echo "Your repository is now on GitHub!"
        echo "URL: $REPO_URL"
        echo ""
        echo "Next steps:"
        echo "1. Set up deployment (see DEPLOYMENT.md)"
        echo "2. Record video walkthrough (see VIDEO_GUIDE.md)"
        echo "3. Submit your assignment"
    else
        echo ""
        echo "❌ Push failed"
        echo "Common issues:"
        echo "- Make sure the repository exists on GitHub"
        echo "- Check your GitHub credentials"
        echo "- Ensure you have push access"
        echo ""
        echo "Try manually:"
        echo "git push -u origin main"
    fi
fi

echo ""
echo "Git setup complete!"
