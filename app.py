"""
FastAPI web application for the Country Information AI Agent
Provides REST API endpoints and a web interface for testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
import os
from typing import Optional

from agent import CountryInfoAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Country Information AI Agent",
    description="AI agent that answers questions about countries using LangGraph and REST Countries API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent (singleton)
agent = None


def get_agent():
    """Get or create the agent instance"""
    global agent
    if agent is None:
        try:
            agent = CountryInfoAgent()
            logger.info("Country Information Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize agent. Please check your API key configuration: {str(e)}"
            )
    return agent


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=1, max_length=500, description="Question about a country")


class AnswerResponse(BaseModel):
    """Response model for answers"""
    question: str
    answer: str
    intent: dict
    api_success: bool
    error: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Country Information AI Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .content {
            padding: 30px;
        }

        .input-section {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .input-wrapper {
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .examples {
            margin: 20px 0;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
        }

        .examples h3 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #666;
        }

        .example-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .example-chip {
            padding: 6px 12px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .example-chip:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .result-section {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            display: none;
        }

        .result-section.show {
            display: block;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .result-header h3 {
            color: #333;
        }

        .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-success {
            background: #d4edda;
            color: #155724;
        }

        .status-error {
            background: #f8d7da;
            color: #721c24;
        }

        .answer-box {
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            line-height: 1.6;
            color: #333;
        }

        .metadata {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            font-size: 13px;
        }

        .metadata-item {
            margin: 8px 0;
            color: #666;
        }

        .metadata-item strong {
            color: #333;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            color: #721c24;
            background: #f8d7da;
            padding: 10px 15px;
            border-radius: 8px;
            margin-top: 10px;
        }

        .footer {
            padding: 20px;
            text-align: center;
            background: #f5f5f5;
            color: #666;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Country Information AI Agent</h1>
            <p>Ask me anything about countries around the world!</p>
        </div>

        <div class="content">
            <div class="input-section">
                <label for="question">Your Question</label>
                <div class="input-wrapper">
                    <input
                        type="text"
                        id="question"
                        placeholder="e.g., What is the population of Germany?"
                        autocomplete="off"
                    />
                    <button onclick="askQuestion()" id="askBtn">Ask</button>
                </div>
            </div>

            <div class="examples">
                <h3>💡 Try these examples:</h3>
                <div class="example-chips">
                    <span class="example-chip" onclick="fillExample('What is the population of Germany?')">Population of Germany</span>
                    <span class="example-chip" onclick="fillExample('What currency does Japan use?')">Currency of Japan</span>
                    <span class="example-chip" onclick="fillExample('What is the capital and population of Brazil?')">Capital & Population of Brazil</span>
                    <span class="example-chip" onclick="fillExample('Tell me about France')">About France</span>
                    <span class="example-chip" onclick="fillExample('What languages are spoken in Switzerland?')">Languages in Switzerland</span>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your question...</p>
            </div>

            <div class="result-section" id="result">
                <div class="result-header">
                    <h3>Answer</h3>
                    <span class="status-badge" id="status"></span>
                </div>
                <div class="answer-box" id="answer"></div>
                <div class="metadata">
                    <div class="metadata-item"><strong>Identified Country:</strong> <span id="country"></span></div>
                    <div class="metadata-item"><strong>Requested Fields:</strong> <span id="fields"></span></div>
                </div>
            </div>
        </div>

        <div class="footer">
            Powered by LangGraph • REST Countries API • Built for Production
        </div>
    </div>

    <script>
        const questionInput = document.getElementById('question');
        const askBtn = document.getElementById('askBtn');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');

        // Allow Enter key to submit
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });

        function fillExample(example) {
            questionInput.value = example;
            questionInput.focus();
        }

        async function askQuestion() {
            const question = questionInput.value.trim();

            if (!question) {
                alert('Please enter a question!');
                return;
            }

            // Show loading
            loading.classList.add('show');
            result.classList.remove('show');
            askBtn.disabled = true;

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'An error occurred');
                }

                // Display result
                document.getElementById('answer').textContent = data.answer;
                document.getElementById('country').textContent = data.intent.country || 'Not identified';
                document.getElementById('fields').textContent = data.intent.fields?.join(', ') || 'None';

                const statusBadge = document.getElementById('status');
                if (data.api_success) {
                    statusBadge.textContent = 'Success';
                    statusBadge.className = 'status-badge status-success';
                } else {
                    statusBadge.textContent = 'Error';
                    statusBadge.className = 'status-badge status-error';
                }

                loading.classList.remove('show');
                result.classList.add('show');

            } catch (error) {
                loading.classList.remove('show');
                alert('Error: ' + error.message);
            } finally {
                askBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a country

    Args:
        request: QuestionRequest containing the user's question

    Returns:
        AnswerResponse with the answer and metadata
    """
    try:
        agent_instance = get_agent()
        result = agent_instance.run(request.question)

        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            intent=result["intent"],
            api_success=result["api_success"],
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if agent can be initialized
        get_agent()
        return {
            "status": "healthy",
            "service": "Country Information AI Agent",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/api/docs")
async def api_documentation():
    """API documentation endpoint"""
    return {
        "service": "Country Information AI Agent",
        "description": "LangGraph-based AI agent for answering questions about countries",
        "endpoints": {
            "/": "Web interface for testing the agent",
            "/ask": "POST endpoint to ask questions (JSON: {question: string})",
            "/health": "Health check endpoint",
            "/api/docs": "API documentation",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)"
        },
        "architecture": {
            "framework": "LangGraph",
            "nodes": [
                "Intent Identification: Extracts country name and requested fields",
                "Tool Invocation: Calls REST Countries API",
                "Answer Synthesis: Generates natural language response"
            ],
            "data_source": "REST Countries API (https://restcountries.com)",
            "llm": "Configurable (OpenAI GPT or Anthropic Claude)"
        },
        "example_questions": [
            "What is the population of Germany?",
            "What currency does Japan use?",
            "What is the capital and population of Brazil?",
            "Tell me about France"
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting Country Information AI Agent on {host}:{port}")
    logger.info(f"Web interface: http://localhost:{port}")
    logger.info(f"API docs: http://localhost:{port}/docs")

    uvicorn.run(app, host=host, port=port)
