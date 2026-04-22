# Video Walkthrough Guide

This guide helps you create the required video walkthrough for the assignment.

## 📹 What to Cover

### 1. Introduction (30 seconds)
- Introduce yourself
- Brief overview of the project
- Show the live demo URL

### 2. Overall Architecture (2-3 minutes)

**Show the architecture diagram and explain:**
- Three-node LangGraph architecture
- Why LangGraph instead of a single prompt
- How state flows between nodes
- Error handling strategy

**Code walkthrough:**
- Open `agent.py`
- Show the `_build_graph()` method
- Explain each node's responsibility:
  - Intent Identification
  - Tool Invocation
  - Answer Synthesis

### 3. Agent Flow with Examples (3-4 minutes)

**Live Demo:**
1. Open the web interface
2. Run these example questions and explain what happens at each node:

   **Example 1: "What is the population of Germany?"**
   - Show logs/terminal output
   - Explain:
     - Node 1: Identifies "Germany" and "population" field
     - Node 2: Calls REST Countries API
     - Node 3: Synthesizes natural answer

   **Example 2: "What is the capital and population of Brazil?"**
   - Show how multiple fields are identified
   - Explain how answer synthesis handles multiple fields

   **Example 3: "Tell me about France"**
   - Show how "general_info" intent works
   - Explain how answer includes multiple relevant fields

   **Example 4: "What is the capital of InvalidCountry123?"**
   - Show error handling
   - Explain graceful degradation

### 4. Production Behavior (2-3 minutes)

**Explain production-ready features:**
- Stateless design (no database) → easy horizontal scaling
- Health check endpoint for load balancers
- Comprehensive error handling
- Logging for debugging and monitoring
- CORS support for frontend integration
- API documentation (show /docs)

**Discuss what would be added for production:**
- Rate limiting
- Caching (Redis)
- Authentication
- Monitoring/alerting
- Circuit breakers

### 5. Known Limitations and Trade-offs (1-2 minutes)

**Be honest about limitations:**
- Single API dependency (REST Countries API)
- No caching = every request hits LLM
- LLM latency (2-5 seconds per query)
- No authentication (could be abused)
- No conversation memory (stateless by design)

**Explain trade-offs:**
- Chose gpt-4o-mini for cost vs. accuracy balance
- Stateless design for scalability vs. no memory
- No embeddings/RAG as per requirements

### 6. Code Quality (1 minute)

**Briefly show:**
- Type hints in code
- Pydantic models for validation
- Comprehensive error handling
- Logging throughout
- Clear separation of concerns

### 7. Closing (30 seconds)
- Show the GitHub repository
- Mention deployment options (Render, Railway, etc.)
- Thank viewers

## 🎬 Recording Setup

### Tools
- **Screen Recording**:
  - Mac: QuickTime Player or Screenshot.app
  - Windows: OBS Studio or Xbox Game Bar
  - Online: Loom (easiest, free tier available)

- **Video Editing** (optional):
  - iMovie (Mac)
  - DaVinci Resolve (Free, cross-platform)
  - Online: Kapwing, Clipchamp

### Recording Tips

1. **Clean up your screen**
   - Close unnecessary windows
   - Hide desktop icons
   - Use a clean browser profile

2. **Audio quality**
   - Use a decent microphone (even phone earbuds are better than laptop mic)
   - Record in a quiet room
   - Speak clearly and not too fast

3. **Visual clarity**
   - Increase font sizes in terminal/IDE (16-18pt minimum)
   - Use high contrast themes
   - Record at 1080p minimum

4. **Pace yourself**
   - Pause between sections
   - Don't rush through code
   - Allow time for viewers to read code/logs

## 📝 Script Template

```
Hi, I'm [Name], and this is my Country Information AI Agent built with LangGraph.

[Show browser with live demo]

Let me give you a quick demo first...
[Ask a question and show the answer]

Now let me walk you through the architecture...
[Open agent.py in IDE]

The system uses LangGraph with three distinct nodes...
[Show _build_graph() method]

Let me explain each node...
[Go through each node method]

Now let's see it in action with a few examples...
[Run examples and show terminal logs]

As you can see, the agent properly identifies...

For production deployment, this system is designed to...
[Discuss production features]

Some known limitations include...
[Discuss trade-offs honestly]

The code is structured with...
[Show code organization]

You can find the complete source code on GitHub at...
[Show README]

Thanks for watching!
```

## 🎯 Checklist Before Recording

- [ ] Application is running locally
- [ ] Logs are visible in terminal
- [ ] Browser is open to localhost:8000
- [ ] IDE is open with agent.py
- [ ] Font sizes are large enough
- [ ] No sensitive information visible (API keys, etc.)
- [ ] Audio is tested
- [ ] Examples work correctly
- [ ] GitHub repo is ready to show

## 📤 Publishing

### Recommended Platforms
1. **YouTube** (Unlisted)
   - Best compatibility
   - Easy sharing
   - Good quality

2. **Loom**
   - Quick and easy
   - Good for assignments
   - Automatic transcription

3. **Google Drive** (with public link)
   - Simple
   - No account needed to view

### Video Settings
- **Resolution**: 1080p (1920x1080)
- **Format**: MP4
- **Length**: 8-12 minutes ideal
- **Privacy**: Unlisted (not private, not fully public)

## 📎 Add to README

After recording, add to your README.md:

```markdown
## 🎥 Video Walkthrough

Watch the complete walkthrough: [Video Link](your-video-url)

Topics covered:
- Architecture and design decisions
- LangGraph node flow with examples
- Production deployment considerations
- Error handling and limitations
- Live demo
```

## 💡 Pro Tips

1. **Record in sections**: Record each part separately and edit together
2. **Have a backup**: Record twice in case something goes wrong
3. **Use captions**: Add subtitles for better accessibility
4. **Show enthusiasm**: Your passion for the project comes through!
5. **Time stamps**: Add timestamps in YouTube description for easy navigation

Example timestamps:
```
0:00 - Introduction
0:30 - Architecture Overview
3:00 - Agent Flow Demo
6:00 - Production Features
8:00 - Limitations & Trade-offs
9:30 - Closing
```

Good luck with your video! 🎥✨
