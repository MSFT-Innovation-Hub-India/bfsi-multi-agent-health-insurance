# Medical Insurance Final Billing Agent
# This agent serves as the authoritative source for medical insurance final billing and settlement,
# providing definitive billing calculations, settlement amounts, and payment processing guidance.
# It acts as the primary billing reference for all other agents in the medical insurance system.

# Step 1: Load packages
import os
import sys
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool, Tool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized instructions
from core.instructions import AZURE_AGENT_INSTRUCTIONS, SEARCH_FIELD_MAPPINGS

# Load environment variables
load_dotenv()

# Azure AI Project config from environment variables
ENDPOINT = os.getenv("AZURE_ENDPOINT", "https://eastus2.api.azureml.ms")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "")
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
PROJECT_NAME = os.getenv("AZURE_PROJECT_NAME", "")
INDEX_NAME = os.getenv("AZURE_SEARCH_BILLING_INDEX", "clm001-folder1-index")

# Step 2: Connect to your Azure AI Project
project_client = AIProjectClient(
    endpoint=ENDPOINT,
    resource_group_name=RESOURCE_GROUP,
    subscription_id=SUBSCRIPTION_ID,
    project_name=PROJECT_NAME,
    credential=DefaultAzureCredential()
)
# Step 3: Connect to Azure AI Search (dataexc1)
conn_list = project_client.connections.list()
conn_id = ""

print("🔍 Available connections:")
for conn in conn_list:
    if conn.connection_type == "CognitiveSearch":
        print(f"   - {conn.id}")

# Try to find dataexc1 connection first
print("🔍 Searching for dataexc1 connection...")
for conn in conn_list:
    if conn.connection_type == "CognitiveSearch" and "dataexc1" in conn.id.lower():
        conn_id = conn.id
        print(f"✅ Found dataexc1 connection: {conn_id}")
        break

# If not found, try dataexc
if not conn_id:
    for conn in conn_list:
        if conn.connection_type == "CognitiveSearch" and "dataexc" in conn.id.lower():
            conn_id = conn.id
            print(f"✅ Found dataexc connection: {conn_id}")
            break

# Final fallback
if not conn_id:
    for conn in conn_list:
        if conn.connection_type == "CognitiveSearch":
            conn_id = conn.id
            print(f"⚠️ Using fallback connection: {conn_id}")
            break

# Step 4: Define the AI Search tool
try:
    ai_search = AzureAISearchTool(
        index_connection_id=conn_id,
        index_name=INDEX_NAME,
        field_mappings=SEARCH_FIELD_MAPPINGS
    )
    
except TypeError:
    print("⚠️ 'field_mappings' not supported by SDK. Proceeding without mappings.")
    ai_search = AzureAISearchTool(
        index_connection_id=conn_id,
        index_name=INDEX_NAME
    )

# Step 5: Define the Agent with centralized instructions
search_agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="medical-insurance-billing-specialist",
    instructions=AZURE_AGENT_INSTRUCTIONS["billing_specialist"],
    tools=ai_search.definitions,
    tool_resources=ai_search.resources,
)

# Step 6: Create a thread and get summary
thread = project_client.agents.create_thread()

print("\n💬 Generating Medical Insurance Final Billing Analysis...")

# Step 7: Create message for complete analysis
policy_expert_query = (
    "Show me the bill details from the medical documents in the index."
)

# Add message
project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content=policy_expert_query
)

# Run the agent
run = project_client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=search_agent.id
)

# Display output
if run.status == "failed":
    print(f"❌ Medical insurance billing analysis failed: {run.last_error}")
else:
    messages = project_client.agents.list_messages(thread_id=thread.id)
    last_msg = messages.get_last_text_message_by_role("assistant")
    print("\n📋 Medical Insurance Final Billing Analysis:")
    print("=" * 60)
    print(last_msg.text.value)
    print("=" * 60)

# Step 8: Clean up (optional)
project_client.agents.delete_agent(search_agent.id)
print("\n✅ Medical insurance billing analysis complete and agent cleaned up.")