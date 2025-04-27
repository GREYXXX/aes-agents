import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

import streamlit as st
from agents.input_understanding import InputUnderstandingAgent
from agents.clarification import ClarificationAgent
from agents.product_search import ProductSearchAgent
from agents.evaluation import EvaluationAgent
from agents.action_decision import ActionDecisionAgent
from agents.communication import CommunicationAgent
from agents.order_execution import OrderExecutionAgent
from agents.providers.openai_provider import OpenAIProvider
from agents.providers.brave_search_provider import BraveSearchProvider
from agents.providers.playwright_order_provider import PlaywrightOrderProvider

def check_api_connections():
    """Check and return the status of all API connections."""
    status = {
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Brave Search": bool(os.getenv("BRAVE_API_KEY")),
        "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "Google": bool(os.getenv("GOOGLE_API_KEY"))
    }
    return status

# Initialize providers
llm_provider = OpenAIProvider()
search_provider = BraveSearchProvider()
order_provider = PlaywrightOrderProvider(headless=True)

# Initialize agents with providers
input_agent = InputUnderstandingAgent(llm_provider)
clarification_agent = ClarificationAgent(llm_provider)
search_agent = ProductSearchAgent(search_provider)
evaluation_agent = EvaluationAgent(llm_provider)
action_agent = ActionDecisionAgent(llm_provider)
communication_agent = CommunicationAgent(llm_provider)
order_agent = OrderExecutionAgent(order_provider)

def main():
    st.title("Procurement Assistant System")
    st.write("Welcome to the Procurement Assistant. Please enter your procurement request below.")
    
    # Display API connection status
    st.sidebar.title("API Connection Status")
    api_status = check_api_connections()
    for api, connected in api_status.items():
        status_emoji = "✅" if connected else "❌"
        st.sidebar.write(f"{status_emoji} {api}")
    
    if not all(api_status.values()):
        st.warning("Some APIs are not connected. Please check your .env file and API keys.")
    
    # Provider selection
    st.sidebar.title("Provider Configuration")
    llm_provider_type = st.sidebar.selectbox(
        "Select LLM Provider",
        ["OpenAI", "Anthropic", "Google"]
    )
    
    search_provider_type = st.sidebar.selectbox(
        "Select Search Provider",
        ["Brave", "Google", "Bing"]
    )
    
    # Input section
    procurement_request = st.text_area("Enter your procurement request email:", height=200)
    
    if st.button("Process Request"):
        if procurement_request:
            # Step 1: Input Understanding
            st.subheader("Step 1: Understanding Your Request")
            extracted_info = input_agent.process(procurement_request)
            st.json(extracted_info)
            
            # Step 2: Clarification if needed
            if clarification_agent.needs_clarification(extracted_info):
                st.subheader("Step 2: Clarification Needed")
                questions = clarification_agent.generate_questions(extracted_info)
                st.write("Please provide additional information:")
                for q in questions:
                    st.write(f"- {q}")
                return
            
            # Step 3: Product Search
            st.subheader("Step 3: Searching for Products")
            search_results = search_agent.search(extracted_info)
            if not search_results:
                st.warning("No search results found. Please try a different search query or check your API connection.")
                return
            st.json(search_results)
            
            # Step 4: Evaluation and Recommendation
            st.subheader("Step 4: Product Evaluation")
            recommendations = evaluation_agent.evaluate(search_results, extracted_info)
            if not recommendations:
                st.warning("No recommendations could be generated. Please try again.")
                return
            st.json(recommendations)
            
            # Step 5: Action Decision
            st.subheader("Step 5: Action Decision")
            action = action_agent.decide(recommendations, extracted_info)
            st.write(f"Recommended Action: {action['action']}")
            
            # Step 6: Communication or Order Execution
            if action['action'] == 'request_approval':
                st.subheader("Step 6: Approval Request")
                approval_request = communication_agent.generate_approval_request(recommendations, extracted_info)
                st.write(approval_request)
            else:
                st.subheader("Step 6: Order Execution")
                order_result = order_agent.execute(recommendations, extracted_info['quantity'])
                st.write(order_result)
        else:
            st.error("Please enter a procurement request.")

if __name__ == "__main__":
    main() 