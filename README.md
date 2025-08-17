# langgraph-data-monitoring-agent

## Running the Agent Locally in LangGraph Studio

To run the agent locally in LangGraph Studio, follow these steps:

1. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the Project**:
   ```bash
   pip install -e .
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following content:
   ```env
   OPENAI_API_KEY=<your_openai_api_key>
   LANGSMITH_API_KEY=
   ```

   Replace `<your_openai_api_key>` with your actual OpenAI API key. Leave `LANGSMITH_API_KEY` empty if not used.

4. **Run LangGraph Studio**:
   ```bash
   langgraph dev
   ```