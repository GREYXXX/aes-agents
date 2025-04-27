# Procurement Assistant System

A multi-agent procurement assistant system that helps automate and streamline the procurement process.

## Features

- Input Understanding: Extracts key information from procurement requests
- Clarification: Generates questions for missing or ambiguous information
- Product Search: Finds relevant products using various search APIs
- Evaluation: Ranks and recommends products based on requirements
- Action Decision: Determines next steps based on company rules
- Communication: Generates approval requests and confirmations
- Order Execution: Simulates or automates the order placement process

## Prerequisites

- Python 3.12
- UV (Python package manager)
- Playwright (for order execution)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aes-agents
   ```

2. Install UV (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Create and activate a Python 3.12 virtual environment using UV:
   ```bash
   uv venv .venv --python 3.12
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. Install dependencies using UV:
   ```bash
   uv pip install -r requirements.txt
   ```

5. Install Playwright browsers:
   ```bash
   playwright install
   ```

6. Set up API keys:
   - Create a `.env` file in the root directory
   - Add your API keys for the providers you want to use:
     ```env
     # API Keys
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     GOOGLE_API_KEY=your_google_api_key_here
     BRAVE_API_KEY=your_brave_api_key_here

     # Default Providers
     DEFAULT_LLM_PROVIDER=openai
     DEFAULT_SEARCH_PROVIDER=brave
     DEFAULT_ORDER_PROVIDER=playwright

     # LLM Model Settings
     OPENAI_MODEL=gpt-4-turbo-preview
     ANTHROPIC_MODEL=claude-3-opus-20240229
     GOOGLE_MODEL=gemini-pro

     # Browser Settings
     BROWSER_HEADLESS=true
     ```
   - You only need to add the API keys for the providers you plan to use
   - The system will work with any combination of providers

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to the provided URL (usually http://localhost:8501)

3. Check the API connection status in the sidebar:
   - ✅ indicates a connected API
   - ❌ indicates a missing API key

4. Select your preferred providers in the sidebar:
   - LLM Provider (OpenAI, Anthropic, Google)
   - Search Provider (Brave, Google, Bing)

5. Enter your procurement request in the text area

6. Click "Process Request" to start the workflow

## System Flow

1. The system processes your procurement request
2. If clarification is needed, it will ask for additional information
3. It searches for relevant products
4. Evaluates and ranks the products
5. Determines if approval is needed based on company rules
6. Either generates an approval request or proceeds with order execution
7. Provides confirmation and tracking information

## Troubleshooting

1. API Connection Issues:
   - Check your `.env` file for correct API keys
   - Verify that the API keys are valid and have sufficient quota
   - Ensure you have internet connectivity

2. Search Issues:
   - Try different search queries
   - Check the Brave Search API documentation for query limitations
   - Verify your Brave Search API key

3. Playwright Issues:
   - Ensure Playwright browsers are installed correctly
   - Check system requirements for Playwright
   - Verify browser compatibility

## Notes

- This is a Proof of Concept (PoC) implementation
- No real email integration is included
- Order execution can be simulated or automated using Playwright
- The system supports multiple LLM providers (OpenAI, Anthropic, Google)
- The system supports multiple search providers (Brave, Google)
- The system supports multiple order execution methods (simulation, Playwright automation)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
