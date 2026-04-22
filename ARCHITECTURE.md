# Architecture Documentation

## Overview

The Country Information AI Agent is built using **LangGraph**, a framework for creating stateful, multi-step agent workflows. This document explains the architectural decisions and implementation details.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  (Web Browser / API Client / cURL)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP POST /ask
                     │ {"question": "..."}
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  - Request validation (Pydantic)                            │
│  - CORS handling                                             │
│  - Error handling                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Initialize agent
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Agent (State Machine)            │
│                                                              │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Node 1: Intent Identification                  │       │
│  │  ┌──────────────────────────────────────────┐   │       │
│  │  │ Input: user_question                     │   │       │
│  │  │ Process:                                 │   │       │
│  │  │  - Send question to LLM                 │   │       │
│  │  │  - Extract country name                 │   │       │
│  │  │  - Identify requested fields            │   │       │
│  │  │ Output: identified_intent               │   │       │
│  │  │  {country: "...", fields: [...]}        │   │       │
│  │  └──────────────────────────────────────────┘   │       │
│  └────────────────────┬────────────────────────────┘       │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Node 2: Tool Invocation                        │       │
│  │  ┌──────────────────────────────────────────┐   │       │
│  │  │ Input: identified_intent                │   │       │
│  │  │ Process:                                │   │       │
│  │  │  - Call REST Countries API              │   │       │
│  │  │  - Handle errors (404, timeout, etc.)   │   │       │
│  │  │  - Structure response data              │   │       │
│  │  │ Output: api_response                    │   │       │
│  │  │  {success: bool, data: {...}}           │   │       │
│  │  └──────────────────────────────────────────┘   │       │
│  └────────────────────┬────────────────────────────┘       │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Node 3: Answer Synthesis                       │       │
│  │  ┌──────────────────────────────────────────┐   │       │
│  │  │ Input: api_response + identified_intent │   │       │
│  │  │ Process:                                │   │       │
│  │  │  - Format relevant data                 │   │       │
│  │  │  - Send to LLM for natural language     │   │       │
│  │  │  - Generate user-friendly response      │   │       │
│  │  │ Output: final_answer                    │   │       │
│  │  │  "Germany has a population of..."       │   │       │
│  │  └──────────────────────────────────────────┘   │       │
│  └─────────────────────────────────────────────────┘       │
│                                                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Return result
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response to User                          │
│  {                                                           │
│    "question": "...",                                        │
│    "answer": "...",                                          │
│    "intent": {...},                                          │
│    "api_success": true                                       │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Application (`app.py`)

**Responsibilities:**
- HTTP request handling
- Input validation using Pydantic models
- CORS configuration for frontend integration
- Health check endpoint
- API documentation (Swagger/OpenAPI)
- Error handling and proper HTTP status codes

**Key Features:**
- Singleton pattern for agent initialization (reuse across requests)
- Async-ready (can be extended for concurrent processing)
- Clean separation from business logic

### 2. LangGraph Agent (`agent.py`)

**Why LangGraph?**
- Explicit state management
- Clear node boundaries
- Easy to debug and test
- Production-ready framework
- Better than single prompt because:
  - Separation of concerns
  - Reusable nodes
  - Clear error boundaries
  - Easier to extend

**State Object:**
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_question: str
    identified_intent: dict
    api_response: dict
    final_answer: str
    error: str
```

**Graph Flow:**
```python
workflow.add_node("intent_identification", ...)
workflow.add_node("tool_invocation", ...)
workflow.add_node("answer_synthesis", ...)

workflow.set_entry_point("intent_identification")
workflow.add_edge("intent_identification", "tool_invocation")
workflow.add_edge("tool_invocation", "answer_synthesis")
workflow.add_edge("answer_synthesis", END)
```

### 3. Node Implementations

#### Node 1: Intent Identification

**Purpose:** Extract structured information from natural language question

**Input:** User's question (string)

**Process:**
1. Construct prompt with examples
2. Call LLM (GPT or Claude)
3. Parse response to extract:
   - Country name
   - Requested fields (population, capital, currency, etc.)

**Output:** `{country: str, fields: List[str]}`

**Error Handling:**
- If country is unclear → Set country to None
- If no specific fields → Default to "general_info"

#### Node 2: Tool Invocation

**Purpose:** Fetch data from REST Countries API

**Input:** Identified intent (country name)

**Process:**
1. Validate country name exists
2. Call `https://restcountries.com/v3.1/name/{country}`
3. Handle HTTP errors:
   - 404 → Country not found
   - Timeout → Network issue
   - 500 → API down
4. Structure and clean API response

**Output:** `{success: bool, data: dict, error: str}`

**Error Handling:**
- Comprehensive error categories
- User-friendly error messages
- No crashes on API failure

#### Node 3: Answer Synthesis

**Purpose:** Generate natural language answer

**Input:** API response + identified intent

**Process:**
1. Check if API call succeeded
2. If error → Generate friendly error message
3. If success:
   - Extract relevant fields from API data
   - Format numbers (add commas)
   - Send to LLM with structured prompt
   - Get natural language response

**Output:** Natural language answer (string)

**Error Handling:**
- Graceful handling of missing data
- Never make up information
- Clear when data is unavailable

### 4. REST Countries API Tool (`tools.py`)

**Responsibilities:**
- HTTP communication with REST Countries API
- Response parsing and structuring
- Error handling and retry logic
- Data extraction and formatting

**Key Methods:**
- `fetch_country_data(country_name)` → Main API call
- `_extract_currencies()` → Parse currency data
- `_extract_languages()` → Parse language data

## Data Flow

### Example: "What is the population of Germany?"

```
1. User Input
   └─> "What is the population of Germany?"

2. FastAPI Layer
   └─> Validates request
   └─> Creates QuestionRequest object
   └─> Calls agent.run()

3. Node 1: Intent Identification
   └─> LLM processes question
   └─> Identifies: {country: "Germany", fields: ["population"]}
   └─> State updated with intent

4. Node 2: Tool Invocation
   └─> Calls GET https://restcountries.com/v3.1/name/Germany
   └─> Receives country data (83M population, etc.)
   └─> State updated with API response

5. Node 3: Answer Synthesis
   └─> Extracts population: 83,240,525
   └─> LLM generates: "Germany has a population of approximately 83,240,525 people."
   └─> State updated with final answer

6. Response
   └─> Returns JSON with answer and metadata
   └─> User sees natural language response
```

## Design Decisions

### 1. Why Three Nodes?

**Separation of Concerns:**
- Each node has a single responsibility
- Easy to test independently
- Clear error boundaries
- Can be enhanced independently

**Alternatives Considered:**
- ❌ Single LLM call with tool use: Less transparent, harder to debug
- ❌ Two nodes (intent + execution): Harder to separate data fetch from synthesis
- ✅ Three nodes: Clear, testable, maintainable

### 2. Why LangGraph vs. Single Prompt?

| Aspect | Single Prompt | LangGraph |
|--------|--------------|-----------|
| Transparency | ❌ Black box | ✅ Clear steps |
| Debugging | ❌ Difficult | ✅ Easy |
| Error Handling | ❌ All-or-nothing | ✅ Per-node |
| Testing | ❌ Hard to unit test | ✅ Test each node |
| Extensibility | ❌ Rewrite prompt | ✅ Add/modify nodes |
| Production | ❌ Risky | ✅ Battle-tested |

### 3. Why Stateless (No Database)?

**Benefits:**
- Easy horizontal scaling
- No state synchronization
- Simpler deployment
- Lower operational complexity
- Fast startup time

**Trade-offs:**
- No conversation history
- No user preferences
- No analytics storage

**When to add database:**
- Need conversation memory
- User authentication required
- Analytics/metrics needed
- Caching at database level

### 4. Why No Caching?

**Current Design:**
- Every request is fresh
- Always up-to-date data
- No stale data issues

**When to add caching:**
- High traffic (>100 req/min)
- Cost optimization needed
- API rate limits hit

**Implementation Options:**
- Redis for API responses (TTL: 1 hour)
- LRU cache for common questions
- CDN for static content

### 5. Error Handling Strategy

**Layered Approach:**
1. **HTTP Layer** (FastAPI): Request validation, status codes
2. **Agent Layer** (LangGraph): Node-level error handling
3. **Tool Layer** (API): Network errors, timeouts, API errors

**Error Categories:**
- User errors (invalid input) → 400 status
- Not found (invalid country) → 200 with error message
- Server errors (API down) → 500 status
- Network errors (timeout) → Retry then error

## Production Considerations

### Scaling Strategy

**Phase 1: Single Instance (0-100 req/min)**
- Current architecture sufficient
- Monitor response times
- Log all errors

**Phase 2: Multiple Instances (100-1000 req/min)**
- Add load balancer
- Deploy 3-5 instances
- Add Redis caching
- Implement rate limiting

**Phase 3: High Scale (1000+ req/min)**
- Kubernetes deployment
- Auto-scaling based on CPU
- Redis cluster
- CDN for static assets
- API Gateway with auth

### Monitoring Recommendations

**Metrics to Track:**
- Response time per node
- API success rate
- Error rates by type
- LLM token usage
- Concurrent requests

**Tools:**
- Datadog / New Relic: APM
- Prometheus + Grafana: Metrics
- Sentry: Error tracking
- CloudWatch / Stackdriver: Logs

### Security Considerations

**Current State:**
- No authentication
- No rate limiting
- Open CORS

**Production Requirements:**
- API key authentication
- Rate limiting (10-50 req/min per IP)
- Restricted CORS origins
- Input sanitization (already done via Pydantic)
- HTTPS only

## Testing Strategy

### Unit Tests
- Test each node independently
- Mock LLM responses
- Mock API calls

### Integration Tests
- Test full agent flow
- Use test API keys
- Test error scenarios

### Load Tests
- Use hey or locust
- Test concurrent requests
- Identify bottlenecks

## Future Enhancements

### Short Term
1. Add caching (Redis)
2. Implement rate limiting
3. Add API key auth
4. Improve error messages
5. Add retry logic for API calls

### Long Term
1. Multi-country queries ("Compare Germany and France")
2. Conversation memory (session-based)
3. Support for images (show flags, maps)
4. Historical data ("Population in 2020")
5. Real-time updates (subscribe to changes)

## Conclusion

This architecture prioritizes:
- ✅ Clarity and maintainability
- ✅ Production-readiness
- ✅ Scalability
- ✅ Testability
- ✅ Error resilience

It's designed to be extended and scaled as requirements grow.
