# Medical Consultation Records Processing Agent
# This agent serves as the authoritative source for medical consultation records and treatment history,
# providing definitive medical record interpretations, treatment validations, and clinical documentation guidance.
# It acts as the primary medical records reference for all other agents in the medical insurance system.

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
INDEX_NAME = os.getenv("AZURE_SEARCH_MEDICAL_INDEX", "healthmedicalrecords")

# Step 2: Connect to your Azure AI Project
project_client = AIProjectClient(
    endpoint=ENDPOINT,
    resource_group_name=RESOURCE_GROUP,
    subscription_id=SUBSCRIPTION_ID,
    project_name=PROJECT_NAME,
    credential=DefaultAzureCredential()
)
# Step 3: Connect to Azure AI Search (fsisearchindex)
conn_list = project_client.connections.list()
conn_id = ""

print("🔍 Available connections:")
for conn in conn_list:
    if conn.connection_type == "CognitiveSearch":
        print(f"   - {conn.id}")

# Try to find fsisearchindex connection first
print("🔍 Searching for fsisearchindex connection...")
for conn in conn_list:
    if conn.connection_type == "CognitiveSearch" and "fsisearchindex" in conn.id.lower():
        conn_id = conn.id
        print(f"✅ Found fsisearchindex connection: {conn_id}")
        break

# If not found, try fsi
if not conn_id:
    for conn in conn_list:
        if conn.connection_type == "CognitiveSearch" and "fsi" in conn.id.lower():
            conn_id = conn.id
            print(f"✅ Found fsi connection: {conn_id}")
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
    name="medical-records-specialist",
    instructions=AZURE_AGENT_INSTRUCTIONS["medical_specialist"],
    tools=ai_search.definitions,
    tool_resources=ai_search.resources,
)

# Step 6: Create a thread and get summary
thread = project_client.agents.create_thread()

print("\n💬 Generating Medical Records Analysis...")

# Step 7: Create message for complete analysis
policy_expert_query = (
    "Provide a comprehensive medical records analysis including: "
    "1) Medical consultation history and treatment timeline "
    "2) Diagnostic reports evaluation and lab results interpretation "
    "3) Pre-existing conditions assessment and medical history review "
    "4) Treatment appropriateness and medical necessity validation "
    "5) Prescription medications review and dosage verification "
    "6) Hospitalization records and discharge summary analysis "
    "7) Medical coding accuracy check (ICD-10, CPT codes) "
    "8) Documentation completeness and fraud risk assessment "
    "Please provide detailed medical analysis and cite specific medical records with proper clinical terminology."
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
    print(f"❌ Medical records analysis failed: {run.last_error}")
else:
    messages = project_client.agents.list_messages(thread_id=thread.id)
    last_msg = messages.get_last_text_message_by_role("assistant")
    print("\n📋 Medical Records Analysis:")
    print("=" * 60)
    print(last_msg.text.value)
    print("=" * 60)

# Step 8: Clean up (optional)
project_client.agents.delete_agent(search_agent.id)
print("\n✅ Medical records analysis complete and agent cleaned up.")