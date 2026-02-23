"""
Seed Cosmos DB with the two static JSON log files.
Loads log.json and log2.json into:
  - claims container (patient_details as claim docs)
  - agent_logs container (full log data)
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from api.cosmos_service import get_cosmos_service


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed():
    cosmos = get_cosmos_service()

    log_files = {
        "CLM001-2024-LAKSHMI": os.path.join("health-insurance-frontend", "src", "log.json"),
        "CLM010-2025-AHSAN": os.path.join("health-insurance-frontend", "src", "log2.json"),
    }

    for claim_id, path in log_files.items():
        print(f"\n{'='*60}")
        print(f"Processing: {claim_id} from {path}")
        data = load_json(path)

        now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None).isoformat() \
            if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat()

        # --- 1. Upsert into 'claims' container ---
        patient = data["patient_details"]
        claim_doc = {
            **patient,
            "id": claim_id,
            "created_at": now,
            "updated_at": now,
        }
        cosmos.claims_container.upsert_item(claim_doc)
        print(f"  ✅ Claim upserted into 'claims' container")

        # --- 2. Upsert into 'agent_logs' container ---
        log_doc = {
            **data,
            "id": f"{claim_id}_seed",
            "claim_id": claim_id,
            "created_at": now,
        }
        cosmos.logs_container.upsert_item(log_doc)
        print(f"  ✅ Agent log upserted into 'agent_logs' container")

    print(f"\n{'='*60}")
    print("🎉 Seeding complete! Both claims and logs are now in Cosmos DB.")


if __name__ == "__main__":
    seed()
