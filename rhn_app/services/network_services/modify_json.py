import json
import os

def modify_json(modifications):
    # Get the current file's directory (network_services)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to saved_networks/input_rhn.json
    json_path = os.path.join(base_dir, "..", "..", "saved_networks", "input_rhn.json")
    json_path = os.path.normpath(json_path)

    print(f"📂 JSON path resolved to: {json_path}")
    
    # Optional: Validate or log parts of incoming data
    print("📝 Incoming keys:", list(modifications.keys()))

    # Overwrite JSON with modifications
    with open(json_path, "w") as f:
        json.dump(modifications, f, indent=2)

    print("✅ JSON file overwritten successfully.")
