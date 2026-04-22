"""
Country Information AI Agent using LangGraph
Implements a three-node graph: intent identification, tool invocation, and answer synthesis
"""
from typing import TypedDict, Annotated, Sequence
import operator
import os
import logging
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from tools import CountryAPITool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State object for the agent graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_question: str
    identified_intent: dict
    api_response: dict
    final_answer: str
    error: str


class CountryInfoAgent:
    """
    LangGraph-based agent for answering country-related questions
    Uses a three-node architecture:
    1. Intent Identification: Extracts country name and requested fields
    2. Tool Invocation: Calls REST Countries API
    3. Answer Synthesis: Generates natural language response
    """

    def __init__(self):
        """Initialize the agent with LLM and build the graph"""
        self.llm = self._initialize_llm()
        self.graph = self._build_graph()

    def _initialize_llm(self):
        """Initialize the language model based on environment variables"""
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

        if os.getenv("ANTHROPIC_API_KEY"):
            logger.info(f"Using Anthropic Claude model: {model_name}")
            return ChatAnthropic(
                model=model_name if "claude" in model_name else "claude-3-5-sonnet-20241022",
                temperature=0,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif os.getenv("OPENAI_API_KEY"):
            logger.info(f"Using OpenAI model: {model_name}")
            return ChatOpenAI(
                model=model_name if "gpt" in model_name else "gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            raise ValueError(
                "No API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file"
            )

    def _build_graph(self):
        """Build the LangGraph state graph"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("intent_identification", self.intent_identification_node)
        workflow.add_node("tool_invocation", self.tool_invocation_node)
        workflow.add_node("answer_synthesis", self.answer_synthesis_node)

        # Define edges
        workflow.set_entry_point("intent_identification")
        workflow.add_edge("intent_identification", "tool_invocation")
        workflow.add_edge("tool_invocation", "answer_synthesis")
        workflow.add_edge("answer_synthesis", END)

        return workflow.compile()

    def intent_identification_node(self, state: AgentState) -> dict:
        """
        Node 1: Identify the user's intent
        Extracts:
        - Country name mentioned in the question
        - Specific fields/information requested (population, capital, currency, etc.)
        """
        logger.info("=== INTENT IDENTIFICATION NODE ===")

        user_question = state["user_question"]

        system_prompt = """You are an intent analyzer for a country information system.
Your job is to extract:
1. The country name mentioned in the question
2. The specific information fields requested (e.g., population, capital, currency, language, area, etc.)

Return your analysis in this exact format:
COUNTRY: [country name]
FIELDS: [comma-separated list of requested fields]

If the country is not clear, respond with:
COUNTRY: UNCLEAR
FIELDS: [fields if any]

If no specific fields are mentioned, respond with:
FIELDS: general_info

Examples:
Question: "What is the population of Germany?"
COUNTRY: Germany
FIELDS: population

Question: "What currency does Japan use?"
COUNTRY: Japan
FIELDS: currency

Question: "Tell me about France"
COUNTRY: France
FIELDS: general_info

Question: "What is the capital and population of Brazil?"
COUNTRY: Brazil
FIELDS: capital, population"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {user_question}")
        ]

        response = self.llm.invoke(messages)
        response_text = response.content

        # Parse the response
        intent = self._parse_intent_response(response_text)

        logger.info(f"Identified country: {intent.get('country', 'UNCLEAR')}")
        logger.info(f"Identified fields: {intent.get('fields', [])}")

        return {
            "identified_intent": intent,
            "messages": [AIMessage(content=f"Intent analysis: {response_text}")]
        }

    def _parse_intent_response(self, response_text: str) -> dict:
        """Parse the LLM response to extract country and fields"""
        lines = response_text.strip().split("\n")
        intent = {"country": None, "fields": []}

        for line in lines:
            line = line.strip()
            if line.startswith("COUNTRY:"):
                country = line.replace("COUNTRY:", "").strip()
                intent["country"] = country if country != "UNCLEAR" else None
            elif line.startswith("FIELDS:"):
                fields_str = line.replace("FIELDS:", "").strip()
                intent["fields"] = [f.strip() for f in fields_str.split(",")]

        return intent

    def tool_invocation_node(self, state: AgentState) -> dict:
        """
        Node 2: Invoke the REST Countries API tool
        Makes API call based on identified country
        """
        logger.info("=== TOOL INVOCATION NODE ===")

        intent = state["identified_intent"]
        country = intent.get("country")

        if not country:
            logger.warning("No country identified, cannot call API")
            return {
                "api_response": {
                    "success": False,
                    "error": "no_country_identified",
                    "message": "Could not identify a country name in your question."
                },
                "messages": [AIMessage(content="No country identified in the question")]
            }

        # Call the API tool
        logger.info(f"Calling REST Countries API for: {country}")
        api_response = CountryAPITool.fetch_country_data(country)

        logger.info(f"API call {'successful' if api_response.get('success') else 'failed'}")

        return {
            "api_response": api_response,
            "messages": [AIMessage(content=f"API response received for {country}")]
        }

    def answer_synthesis_node(self, state: AgentState) -> dict:
        """
        Node 3: Synthesize the final answer
        Generates natural language response based on API data and requested fields
        """
        logger.info("=== ANSWER SYNTHESIS NODE ===")

        api_response = state["api_response"]
        intent = state["identified_intent"]
        user_question = state["user_question"]

        # Handle API errors
        if not api_response.get("success"):
            error_message = api_response.get("message", "An error occurred")
            logger.warning(f"Synthesizing error response: {error_message}")

            final_answer = self._generate_error_response(error_message, user_question)

            return {
                "final_answer": final_answer,
                "error": error_message,
                "messages": [AIMessage(content=final_answer)]
            }

        # Extract country data
        country_data = api_response.get("data", {})
        requested_fields = intent.get("fields", ["general_info"])

        # Generate natural language answer
        system_prompt = """You are a helpful assistant that answers questions about countries.
You have access to accurate data from the REST Countries API.

Your job is to:
1. Answer the user's question directly and concisely
2. Use the provided country data
3. Focus on the specific fields they asked about
4. If they asked for general info, provide a brief overview
5. Format numbers with commas for readability (e.g., 83,000,000 not 83000000)
6. Be conversational and natural

DO NOT:
- Make up information not in the data
- Provide information they didn't ask for (unless it's general_info)
- Apologize or add unnecessary preamble"""

        # Prepare data context
        data_context = self._format_country_data(country_data, requested_fields)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""User Question: {user_question}

Requested Fields: {', '.join(requested_fields)}

Country Data:
{data_context}

Please answer the user's question using this data.""")
        ]

        response = self.llm.invoke(messages)
        final_answer = response.content

        logger.info("Answer synthesized successfully")

        return {
            "final_answer": final_answer,
            "messages": [AIMessage(content=final_answer)]
        }

    def _format_country_data(self, country_data: dict, requested_fields: list) -> str:
        """Format country data for the synthesis prompt"""
        lines = []

        # Basic info (always include)
        lines.append(f"Country: {country_data.get('name', {}).get('common', 'N/A')}")
        lines.append(f"Official Name: {country_data.get('name', {}).get('official', 'N/A')}")

        # Add requested fields
        if "general_info" in requested_fields:
            # Include common fields for general info
            lines.append(f"Capital: {country_data.get('capital', 'N/A')}")
            lines.append(f"Population: {country_data.get('population', 'N/A'):,}" if isinstance(country_data.get('population'), int) else f"Population: {country_data.get('population', 'N/A')}")
            lines.append(f"Region: {country_data.get('region', 'N/A')}")
            lines.append(f"Subregion: {country_data.get('subregion', 'N/A')}")

            currencies = country_data.get('currencies', [])
            if currencies:
                curr_str = ", ".join([f"{c['name']} ({c['code']})" for c in currencies])
                lines.append(f"Currency: {curr_str}")

            languages = country_data.get('languages', [])
            if languages:
                lines.append(f"Languages: {', '.join(languages)}")
        else:
            # Include only requested fields
            field_mapping = {
                "population": lambda: f"Population: {country_data.get('population', 'N/A'):,}" if isinstance(country_data.get('population'), int) else f"Population: {country_data.get('population', 'N/A')}",
                "capital": lambda: f"Capital: {country_data.get('capital', 'N/A')}",
                "currency": lambda: f"Currency: {self._format_currencies(country_data.get('currencies', []))}",
                "currencies": lambda: f"Currency: {self._format_currencies(country_data.get('currencies', []))}",
                "language": lambda: f"Languages: {', '.join(country_data.get('languages', []))}",
                "languages": lambda: f"Languages: {', '.join(country_data.get('languages', []))}",
                "area": lambda: f"Area: {country_data.get('area', 'N/A'):,} km²" if isinstance(country_data.get('area'), (int, float)) else f"Area: {country_data.get('area', 'N/A')}",
                "region": lambda: f"Region: {country_data.get('region', 'N/A')}",
                "subregion": lambda: f"Subregion: {country_data.get('subregion', 'N/A')}",
                "timezone": lambda: f"Timezones: {', '.join(country_data.get('timezones', []))}",
                "timezones": lambda: f"Timezones: {', '.join(country_data.get('timezones', []))}",
                "borders": lambda: f"Bordering Countries: {', '.join(country_data.get('borders', [])) if country_data.get('borders') else 'None'}",
                "continents": lambda: f"Continents: {', '.join(country_data.get('continents', []))}",
            }

            for field in requested_fields:
                field_lower = field.lower().strip()
                if field_lower in field_mapping:
                    lines.append(field_mapping[field_lower]())

        return "\n".join(lines)

    def _format_currencies(self, currencies: list) -> str:
        """Format currency list for display"""
        if not currencies:
            return "N/A"
        return ", ".join([f"{c['name']} ({c['code']}) {c.get('symbol', '')}" for c in currencies])

    def _generate_error_response(self, error_message: str, user_question: str) -> str:
        """Generate a user-friendly error response"""
        error_prompts = {
            "country_not_found": "I couldn't find information about that country. Please check the spelling or try a different country name.",
            "no_country_identified": "I couldn't identify which country you're asking about. Could you please rephrase your question and mention a specific country?",
            "timeout": "I'm having trouble connecting to the country information service. Please try again in a moment.",
            "api_error": "I encountered an error while fetching country information. Please try again later."
        }

        # Try to match error type
        for error_type, response in error_prompts.items():
            if error_type in error_message.lower():
                return response

        # Default error response
        return f"I'm sorry, I encountered an issue: {error_message}"

    def run(self, user_question: str) -> dict:
        """
        Run the agent on a user question

        Args:
            user_question: The user's question about a country

        Returns:
            Dictionary containing the final answer and intermediate states
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing question: {user_question}")
        logger.info(f"{'='*60}\n")

        # Initialize state
        initial_state = {
            "messages": [],
            "user_question": user_question,
            "identified_intent": {},
            "api_response": {},
            "final_answer": "",
            "error": ""
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        result = {
            "question": user_question,
            "answer": final_state.get("final_answer", ""),
            "intent": final_state.get("identified_intent", {}),
            "api_success": final_state.get("api_response", {}).get("success", False),
            "error": final_state.get("error", "")
        }

        logger.info(f"\nFinal Answer: {result['answer']}\n")

        return result


# For testing
if __name__ == "__main__":
    agent = CountryInfoAgent()

    # Test questions
    test_questions = [
        "What is the population of Germany?",
        "What currency does Japan use?",
        "What is the capital and population of Brazil?",
        "Tell me about France",
        "What is the capital of XYZ123?"  # Invalid country
    ]

    for question in test_questions:
        result = agent.run(question)
        print(f"\nQ: {question}")
        print(f"A: {result['answer']}")
        print("-" * 60)
