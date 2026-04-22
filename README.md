# Country Information AI Agent

An AI-powered agent that answers questions about countries using LangGraph and the REST Countries API.

## 🎯 Overview

This project implements a production-ready AI agent using **LangGraph** to answer questions about countries. The agent follows a structured three-node architecture:

1. **Intent Identification**: Analyzes the user's question to extract the country name and requested information fields
2. **Tool Invocation**: Fetches data from the REST Countries API based on identified intent
3. **Answer Synthesis**: Generates natural language responses using the fetched data

## 🏗️ Architecture

```
User Question
     |
     v
┌────────────────────────────────┐
│  Intent Identification Node    │
│  - Extract country name         │
│  - Identify requested fields    │
└────────────┬───────────────────┘
             |
             v
┌────────────────────────────────┐
│  Tool Invocation Node          │
│  - Call REST Countries API      │
│  - Handle errors gracefully     │
└────────────┬───────────────────┘
             |
             v
┌────────────────────────────────┐
│  Answer Synthesis Node         │
│  - Generate natural response    │
│  - Format data appropriately    │
└────────────┬───────────────────┘
             |
             v
        Final Answer
```

### Key Design Decisions

- **LangGraph State Machine**: Ensures clear separation of concerns and makes the agent flow explicit and maintainable
- **Error Handling**: Comprehensive error handling at each node (API failures, invalid inputs, network issues)
- **Production-Ready**: Structured logging, health checks, proper HTTP status codes, and graceful degradation
- **LLM-Agnostic**: Supports both OpenAI (GPT) and Anthropic (Claude) models via configuration
- **No Database**: Stateless design for horizontal scalability
- **RESTful API**: Standard HTTP endpoints with proper request/response models

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- An API key from either:
  - OpenAI (recommended: `gpt-4o-mini` for cost-effectiveness)
  - Anthropic (Claude)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Country-Information-AI-Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```env
   # For OpenAI (recommended)
   OPENAI_API_KEY=your-openai-api-key-here
   MODEL_NAME=gpt-4o-mini

   # OR for Anthropic
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   MODEL_NAME=claude-3-5-sonnet-20241022
   ```

### Running the Application

**Start the web server:**
```bash
python app.py
```

The server will start on `http://localhost:8000`

**Access the web interface:**
- Open your browser to `http://localhost:8000`
- Try example questions or ask your own!

**API Endpoints:**
- `GET /` - Web interface
- `POST /ask` - Ask questions (JSON API)
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## 📝 Example Usage

### Via Web Interface

1. Open `http://localhost:8000` in your browser
2. Type a question like "What is the population of Germany?"
3. Click "Ask" or press Enter
4. View the natural language answer with metadata

### Via API (cURL)

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the population of Germany?"}'
```

### Via API (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "What currency does Japan use?"}
)

result = response.json()
print(result["answer"])
```

### Example Questions

- "What is the population of Germany?"
- "What currency does Japan use?"
- "What is the capital and population of Brazil?"
- "Tell me about France"
- "What languages are spoken in Switzerland?"
- "What is the area of Canada?"

## 🧪 Testing

**Run the agent directly (no web server):**
```bash
python agent.py
```

This will run a set of test questions and display the agent's reasoning process.

**Test API health:**
```bash
curl http://localhost:8000/health
```

## 📊 Agent Flow Example

**Question**: "What is the population of Germany?"

**Node 1 - Intent Identification:**
- Country: Germany
- Fields: population

**Node 2 - Tool Invocation:**
- API Call: `GET https://restcountries.com/v3.1/name/Germany`
- Response: Country data with population, capital, currencies, etc.

**Node 3 - Answer Synthesis:**
- Extract relevant fields (population in this case)
- Generate natural language: "Germany has a population of approximately 83,240,525 people."

## 🏭 Production Considerations

### What's Production-Ready

✅ **Structured Architecture**: Clear separation via LangGraph nodes
✅ **Error Handling**: Graceful handling of API failures, timeouts, and invalid inputs
✅ **Logging**: Comprehensive logging at each step for debugging and monitoring
✅ **Health Checks**: `/health` endpoint for load balancers and monitoring systems
✅ **Stateless Design**: No database = easy horizontal scaling
✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs
✅ **Input Validation**: Pydantic models for request/response validation
✅ **CORS Support**: Ready for frontend integration

### Limitations and Trade-offs

⚠️ **Single API Dependency**: Relies on REST Countries API availability
- *Mitigation*: Could add retry logic, circuit breakers, or fallback data sources

⚠️ **No Caching**: Every query hits the LLM and API
- *Mitigation*: Could add Redis caching for frequent queries

⚠️ **LLM Latency**: Response time includes LLM inference (2-5 seconds)
- *Mitigation*: Could use streaming responses or faster models (gpt-4o-mini)

⚠️ **No Authentication**: Open endpoint, could be abused
- *Mitigation*: Add API key auth, rate limiting (e.g., using SlowAPI)

⚠️ **No Conversation Memory**: Each query is independent
- *Design Choice*: Aligns with stateless architecture, but could add session management

⚠️ **Limited to REST Countries API Data**: Only answers what the API provides
- *Design Choice*: Meets requirements (no embeddings/RAG), but could be extended

### Scaling Recommendations

**For Production Deployment:**

1. **Add Rate Limiting**: Prevent abuse using middleware (SlowAPI, Redis)
2. **Implement Caching**: Cache API responses (Redis) and common questions
3. **Add Monitoring**: Integrate with Prometheus, Datadog, or similar
4. **API Key Authentication**: Protect endpoints with API keys
5. **Load Balancing**: Deploy multiple instances behind a load balancer
6. **Error Tracking**: Integrate Sentry or similar for error monitoring
7. **Async Processing**: Use async/await for concurrent requests
8. **Circuit Breakers**: Prevent cascade failures when API is down

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes (or ANTHROPIC_API_KEY) |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes (or OPENAI_API_KEY) |
| `MODEL_NAME` | LLM model to use | `gpt-4o-mini` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |

### Supported Models

**OpenAI:**
- `gpt-4o-mini` (recommended for production - fast & cost-effective)
- `gpt-4o` (more capable, higher cost)
- `gpt-4-turbo`

**Anthropic:**
- `claude-3-5-sonnet-20241022` (recommended)
- `claude-3-opus-20240229` (most capable)

## 📦 Project Structure

```
Country-Information-AI-Agent/
├── agent.py              # LangGraph agent implementation (3 nodes)
├── tools.py              # REST Countries API integration
├── app.py                # FastAPI web application
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🛠️ Technology Stack

- **LangGraph**: State machine orchestration for agent flow
- **LangChain**: LLM abstraction and integration
- **FastAPI**: High-performance web framework
- **Pydantic**: Data validation and serialization
- **OpenAI/Anthropic**: Language models for understanding and generation
- **REST Countries API**: Country data source
- **Uvicorn**: ASGI server

## 🤝 Contributing

This is an assignment project, but feedback and suggestions are welcome!

## 📄 License

This project is created for educational and assignment purposes.

## 🎥 Video Walkthrough

A video walkthrough is available that covers:
- Overall architecture and design decisions
- Agent flow with live examples
- Production deployment considerations
- Known limitations and trade-offs
- Live demo of the web interface and API

[Video Link: To be added]

## 🌐 Live Demo

[Live Demo Link: To be added after deployment]

You can deploy this to:
- **Render**: Easy deployment with free tier
- **Railway**: Simple deployment with automatic HTTPS
- **Heroku**: Classic PaaS with good Python support
- **AWS/GCP/Azure**: For full production deployment

## 📞 Contact

For questions or feedback about this assignment:
- GitHub Issues: [Create an issue]
- Email: [Your email]

---

Built with ❤️ using LangGraph and FastAPI
