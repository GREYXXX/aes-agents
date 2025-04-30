import os
from dotenv import load_dotenv
import json

# Load environment variables first
load_dotenv()

import streamlit as st
from agents.input_understanding import InputUnderstandingAgent
from agents.requirement_expansion import RequirementExpansionAgent
from agents.multi_agent_search import MultiAgentProductSearch
from agents.evaluation import EvaluationAgent
from agents.action_decision import ActionDecisionAgent
from agents.communication import CommunicationAgent
from agents.order_execution import OrderExecutionAgent
from agents.clarification import ClarificationAgent
from agents.providers.llm_provider import LLMProvider
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
llm_provider = LLMProvider()
search_provider = BraveSearchProvider()
order_provider = PlaywrightOrderProvider(headless=True)

# Initialize agents with providers
input_agent = InputUnderstandingAgent(llm_provider)
clarification_agent = ClarificationAgent(llm_provider)
expansion_agent = RequirementExpansionAgent(llm_provider)
search_agent = MultiAgentProductSearch(search_provider, llm_provider)
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
            extracted_info = input_agent.extract_info(procurement_request)
            
            # Translate extracted info to English if needed
            if any(isinstance(value, str) and not value.isascii() for value in extracted_info.values()):
                st.write("Translating requirements to English...")
                translation_prompt = f"""
                Translate the following procurement requirements to English:
                {json.dumps(extracted_info, indent=2, ensure_ascii=False)}
                
                Return a JSON object with the same structure but with all text translated to English.
                """
                
                try:
                    translated_response = llm_provider.generate_completion(
                        prompt=translation_prompt,
                        system_prompt="You are a professional translator specializing in procurement documents.",
                        response_format={"type": "json_object"}
                    )
                    extracted_info = json.loads(translated_response)
                    st.success("Translation completed successfully!")
                except Exception as e:
                    st.warning(f"Translation failed: {str(e)}")
                    st.info("Continuing with original text...")
            
            # Display extracted information in user-friendly format
            st.markdown("### 📋 Extracted Requirements")
            for key, value in extracted_info.items():
                if isinstance(value, list):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        st.markdown(f"- {item}")
                else:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Step 2: Key Information Collection
            st.subheader("Step 2: Provide Key Information")
            
            # Check if all required information is already available
            required_fields = {
                "product_type": "Product Type",
                "quantity": "Quantity",
                "budget": "Budget",
                "location": "Location"
            }
            
            missing_fields = []
            for field, label in required_fields.items():
                if field not in extracted_info or not extracted_info[field]:
                    missing_fields.append(label)
            
            if missing_fields:
                st.write(f"Please provide the following missing information: {', '.join(missing_fields)}")
                
                with st.form("key_info_form"):
                    # Product Type
                    if "Product Type" in missing_fields:
                        product_type = st.selectbox(
                            "Product Type",
                            options=["Laptop", "Desktop", "Monitor", "Printer", "Server", "Network Equipment", "Other"],
                            index=0
                        )
                    else:
                        product_type = extracted_info["product_type"]
                    
                    # Quantity
                    if "Quantity" in missing_fields:
                        quantity = st.number_input(
                            "Quantity",
                            min_value=1,
                            value=1,
                            step=1
                        )
                    else:
                        quantity = extracted_info["quantity"]
                    
                    # Budget
                    if "Budget" in missing_fields:
                        budget = st.text_input(
                            "Budget (e.g., 1000 AUD)",
                            value=""
                        )
                    else:
                        budget = extracted_info["budget"]
                    
                    # Location
                    if "Location" in missing_fields:
                        location = st.selectbox(
                            "Delivery Location",
                            options=["Perth", "Sydney", "Melbourne", "Brisbane", "Adelaide", "Other"],
                            index=0
                        )
                    else:
                        location = extracted_info["location"]
                    
                    # Special Requirements (optional)
                    special_requirements = st.multiselect(
                        "Special Requirements (Optional)",
                        options=[
                            "Fast Delivery",
                            "Bulk Discount",
                            "Warranty Required",
                            "Installation Service",
                            "Technical Support",
                            "Other"
                        ]
                    )
                    
                    submitted = st.form_submit_button("Submit Information")
                    
                    if submitted:
                        # Validate inputs
                        if "Budget" in missing_fields and not budget:
                            st.error("Please provide a budget")
                        else:
                            # Update extracted_info with form data
                            extracted_info.update({
                                "product_type": product_type,
                                "quantity": quantity,
                                "budget": budget,
                                "location": location,
                                "special_requirements": special_requirements
                            })
                            
                            st.success("Information collected successfully!")
                            # The form will be hidden after successful submission
                            st.experimental_rerun()
            else:
                st.success("All required information is available. Proceeding to search...")
                
                # Step 3: Product Search
                st.subheader("Step 3: Searching for Products")
                with st.spinner("🔍 Searching web for products..."):
                    search_results = search_agent.search(extracted_info)
                    if not search_results:
                        st.warning("No search results found. Please try a different search query or check your API connection.")
                        return
                
                st.success("✅ Search completed! Found {} products.".format(len(search_results)))
                
                # Step 4: Product Recommendations
                st.subheader("Step 4: Product Recommendations")
                with st.spinner("🤔 Analyzing and generating recommendations..."):
                    recommendations = evaluation_agent.evaluate(search_results, extracted_info)
                    
                    # Display recommendations (default 5)
                    st.markdown("### 🎯 Top 5 Recommended Products")
                    for idx, product in enumerate(recommendations[:5], 1):
                        st.markdown(f"#### {idx}. {product['title']}")
                        st.markdown(f"**Price:** {product['price']}")
                        st.markdown(f"**Source:** {product['source']}")
                        st.markdown(f"**Link:** [{product['title']}]({product['url']})")
                        st.markdown(f"**Summary:** {product['summary']}")
                        st.markdown("---")
                    
                    # Product selection
                    st.markdown("### 🤔 Which product would you like to proceed with?")
                    product_options = [f"{idx}. {product['title']}" for idx, product in enumerate(recommendations[:5], 1)]
                    selected_option = st.selectbox(
                        "Select a product",
                        options=product_options,
                        index=0
                    )
                    
                    if st.button("Proceed with Selected Product"):
                        selected_idx = int(selected_option.split('.')[0]) - 1
                        selected_product = recommendations[selected_idx]
                        
                        # Step 5: Next Actions
                        st.subheader("Step 5: Next Steps")
                        st.markdown(f"### Selected Product: {selected_product['title']}")
                        
                        # Display selected product details
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown("**Details:**")
                            st.markdown(f"- Price: {selected_product['price']}")
                            st.markdown(f"- Source: {selected_product['source']}")
                            st.markdown(f"- Link: [{selected_product['title']}]({selected_product['url']})")
                            st.markdown(f"- Summary: {selected_product['summary']}")
                        
                        # Next steps options
                        st.markdown("### Choose your next action:")
                        action = st.radio(
                            "What would you like to do?",
                            ["Request Approval", "Place Order", "Compare with Similar Products"]
                        )
                        
                        if action == "Request Approval":
                            st.info("🔍 Generating approval request...")
                            approval_request = communication_agent.generate_approval_request([selected_product], extracted_info)
                            st.markdown("### 📝 Approval Request")
                            st.markdown(approval_request)
                            
                            # Show approval form
                            with st.form("approval_form"):
                                st.write("Please review the approval request above")
                                approved = st.radio("Do you approve this request?", ["Yes", "No"])
                                submitted = st.form_submit_button("Submit")
                                
                                if submitted and approved == "Yes":
                                    st.success("Approval granted! Proceeding with order execution...")
                                    order_result = order_agent.execute([selected_product], extracted_info['quantity'])
                                    st.markdown("### ✅ Order Execution Result")
                                    st.markdown(order_result)
                                elif submitted and approved == "No":
                                    st.warning("Request denied. Please select a different product or modify your requirements.")
                        
                        elif action == "Place Order":
                            st.info("🛒 Processing order...")
                            order_result = order_agent.execute([selected_product], extracted_info['quantity'])
                            st.markdown("### ✅ Order Execution Result")
                            st.markdown(order_result)
                        
                        elif action == "Compare with Similar Products":
                            st.info("🔍 Finding similar products...")
                            # Add comparison logic here
                            st.markdown("### Similar Products")
                            st.markdown("Feature coming soon...")
        else:
            st.error("Please enter a procurement request.")

if __name__ == "__main__":
    main() 