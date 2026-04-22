# Quick Start Guide

Get the Country Information AI Agent up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- An OpenAI API key (get one at https://platform.openai.com/api-keys)

## Option 1: Automated Setup (Recommended)

```bash
# 1. Clone or navigate to the repository
cd Country-Information-AI-Agent

# 2. Run the setup script
python setup.py
```

The script will:
- Check Python version
- Install dependencies
- Set up your API key
- Run tests

## Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file:

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

Add this to `.env`:
```
OPENAI_API_KEY=your-openai-api-key-here
MODEL_NAME=gpt-4o-mini
```

### Step 3: Test the Setup

```bash
python test_agent.py
```

You should see test results with ✅ marks.

### Step 4: Start the Server

```bash
python app.py
```

You'll see:
```
INFO:     Started server on http://0.0.0.0:8000
```

### Step 5: Try It Out!

Open your browser to: **http://localhost:8000**

Or test via API:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the population of Germany?"}'
```

## Example Questions to Try

- "What is the population of Germany?"
- "What currency does Japan use?"
- "Tell me about France"
- "What is the capital and population of Brazil?"
- "What languages are spoken in Switzerland?"

## Troubleshooting

### "No API key found"
- Make sure your `.env` file exists
- Check that `OPENAI_API_KEY` is set correctly
- No quotes around the key

### "Module not found"
- Run: `pip install -r requirements.txt`
- Make sure you're in the project directory

### "Failed to initialize agent"
- Check your API key is valid
- Verify you have internet connection
- Check OpenAI API status: https://status.openai.com/

### "Country not found"
- Check spelling of country name
- Try full country name (e.g., "United States of America" not "USA")

## Next Steps

- **Deploy it**: See [DEPLOYMENT.md](DEPLOYMENT.md) for hosting options
- **Record video**: See [VIDEO_GUIDE.md](VIDEO_GUIDE.md) for walkthrough tips
- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for details
- **API docs**: Visit http://localhost:8000/docs for interactive API documentation

## Using Docker (Optional)

If you have Docker installed:

```bash
# Build and run with docker-compose
docker-compose up

# Or build and run manually
docker build -t country-agent .
docker run -p 8000:8000 --env-file .env country-agent
```

Access at: http://localhost:8000

## Project Structure

```
Country-Information-AI-Agent/
├── agent.py              # Main LangGraph agent (3 nodes)
├── tools.py              # REST Countries API tool
├── app.py                # FastAPI web application
├── requirements.txt      # Python dependencies
├── .env                  # Your API keys (create this)
├── test_agent.py         # Test suite
└── README.md             # Full documentation
```

## Support

- Check the [README.md](README.md) for detailed documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
- See [DEPLOYMENT.md](DEPLOYMENT.md) for hosting options

## Quick Tips

💡 **Cost Saving**: Use `gpt-4o-mini` (default) instead of `gpt-4` for 10x lower costs

💡 **Performance**: Response time is typically 2-5 seconds (LLM + API call)

💡 **Customization**: Edit prompts in `agent.py` to change behavior

💡 **Hosting**: Deploy to Render or Railway for free (see DEPLOYMENT.md)

---

Happy coding! 🚀
