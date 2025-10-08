#!/usr/bin/env python3
"""
Simple example demonstrating the upload_agent_run method

This example shows how to directly use the public method to upload a minimal JSON payload
to Railtown AI's blob storage using presigned SAS URLs.
"""

import json
import os
import time
import uuid
from typing import Any

import railtownai


def create_simple_test_data(run_id: str | None = None, session_id: str | None = None) -> dict[str, Any]:
    """
    Load mock data from the JSON file for upload testing.

    Returns:
        Dict containing mock test data from tests/integration/mock_data.json
    """
    # Get the path to the mock data file relative to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    mock_data_path = os.path.join(project_root, "tests", "integration", "mock_data.json")

    try:
        with open(mock_data_path) as f:
            data = json.load(f)

            if session_id:
                data["session_id"] = session_id

            else:
                data["session_id"] = str(uuid.uuid4())

            if run_id:
                data["run_id"] = run_id
            else:
                data["run_id"] = str(uuid.uuid4())

            return data
    except FileNotFoundError:
        print(f"Warning: Mock data file not found at {mock_data_path}")
        print("Falling back to simple test data...")
        return {"name": "flight planner", "nodes": [], "edges": []}
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing mock data file: {e}")
        print("Falling back to simple test data...")
        return {"name": "flight planner", "nodes": [], "edges": []}


def create_session_test_data() -> dict[str, Any]:
    """
    Create example session format data with multiple runs.

    Returns:
        Dict containing session format test data
    """
    session_id = str(uuid.uuid4())  # noqa: F841
    current_time = int(time.time())
    return {
        "session_id": session_id,
        "name": "ticket-triage-agent-session",
        "start_time": current_time,
        "end_time": current_time,
        "runs": [
            {
                "run_id": str(uuid.uuid4()),
                "name": "Initial Analysis Run",
                "start_time": current_time,
                "end_time": current_time,
                "status": "Completed",
                "nodes": [
                    {"identifier": "analyzer", "name": "analyzer", "node_type": "Agent"},
                    {"identifier": "classifier", "name": "classifier", "node_type": "Tool"},
                ],
                "steps": [
                    {"step": 1, "time": current_time, "identifier": "analyze_ticket"},
                    {"step": 2, "time": current_time, "identifier": "classify_priority"},
                ],
                "edges": [{"source": "analyzer", "target": "classifier", "identifier": "analysis_to_classification"}],
            },
            {
                "run_id": str(uuid.uuid4()),
                "name": "Response Generation Run",
                "start_time": current_time,
                "end_time": current_time,
                "status": "Completed",
                "nodes": [
                    {"identifier": "responder", "name": "responder", "node_type": "Agent"},
                    {"identifier": "formatter", "name": "formatter", "node_type": "Tool"},
                ],
                "steps": [
                    {"step": 1, "time": current_time, "identifier": "generate_response"},
                    {"step": 2, "time": current_time, "identifier": "format_output"},
                ],
                "edges": [{"source": "responder", "target": "formatter", "identifier": "response_to_format"}],
            },
        ],
    }


def upload_json_payload_example():
    """
    Simple example demonstrating how to use upload_agent_run method.
    """
    print("Railtown AI JSON Payload Upload Examples")
    print("=" * 50)

    # Initialize Railtown AI with your API key
    # Replace 'YOUR_RAILTOWN_API_KEY' with your actual API key
    key = os.getenv("RAILTOWN_API_KEY")
    if not key:
        print("Warning: RAILTOWN_API_KEY not found in environment variables.")
        print("Please set RAILTOWN_API_KEY in your .env file or environment variables.")
        print("Example .env file content:")
        print("RAILTOWN_API_KEY=your_actual_api_key_here")
        return
    railtownai.init(key)

    # Example 1: Single old-format payload
    print("\n1. SINGLE OLD-FORMAT PAYLOAD")
    print("-" * 30)

    test_data = create_simple_test_data()
    print("Old format data to upload:")
    print(json.dumps(test_data, indent=2))

    print("\nUploading single old-format JSON payload...")
    success = railtownai.upload_agent_run(test_data)

    if success:
        print("✅ Single old-format JSON payload uploaded successfully!")
    else:
        print("❌ Failed to upload single old-format JSON payload")

    # Example 2: Session format payload
    print("\n" + "=" * 50)
    print("\n2. SESSION FORMAT PAYLOAD (NEW)")
    print("-" * 30)

    session_data = create_session_test_data()
    print("Session format data to upload:")
    print(json.dumps(session_data, indent=2))

    print("\nUploading session format payload...")
    success = railtownai.upload_agent_run(session_data)

    if success:
        print("✅ Session format payload uploaded successfully!")
        print("   (Each run in the session was uploaded individually)")
    else:
        print("❌ Failed to upload session format payload")

    # Example 3: Mixed format array
    print("\n" + "=" * 50)
    print("\n3. MIXED FORMAT ARRAY")
    print("-" * 30)

    mixed_data_array = [
        create_simple_test_data(),  # Old format
        create_session_test_data(),  # Session format
        create_simple_test_data(),  # Old format
    ]

    print(f"Uploading mixed array with {len(mixed_data_array)} payloads:")
    print("  - Payload 1: Old format")
    print("  - Payload 2: Session format (contains 2 runs)")
    print("  - Payload 3: Old format")

    success = railtownai.upload_agent_run(mixed_data_array)

    if success:
        print("✅ All mixed format payloads uploaded successfully!")
    else:
        print("❌ Failed to upload one or more mixed format payloads")

    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    # Note: Replace 'YOUR_RAILTOWN_API_KEY' with your actual API key
    # If you don't have one, the example will still run but uploads will fail

    upload_json_payload_example()
