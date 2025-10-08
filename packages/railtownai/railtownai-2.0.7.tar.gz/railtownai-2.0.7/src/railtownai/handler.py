"""Logging handler for the Railtown AI Python SDK."""

from __future__ import annotations

#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
import datetime
import json
import logging
import time
import traceback
import uuid
from typing import Any

from .api_client import get_http_client
from .breadcrumbs import get_breadcrumbs
from .config import get_api_key, get_config
from .models import RailtownPayload


class RailtownHandler(logging.Handler):
    """Custom logging handler that sends log records to Railtown AI."""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._config = None

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log record to Railtown AI."""
        try:
            config = self._get_config()
            if not config:
                return

            # Get breadcrumbs
            breadcrumbs = get_breadcrumbs()

            # Convert log level to string
            level_map = {
                logging.DEBUG: "debug",
                logging.INFO: "info",
                logging.WARNING: "warning",
                logging.ERROR: "error",
                logging.CRITICAL: "critical",
            }
            level_str = level_map.get(record.levelno, "info")

            # Get exception info if available
            exception_info = ""
            if record.exc_info:
                exception_info = "".join(traceback.format_exception(*record.exc_info))

            # Prepare properties from record
            properties = {}
            if hasattr(record, "extra_data"):
                if isinstance(record.extra_data, dict):
                    properties.update(record.extra_data)
                else:
                    properties["extra_data"] = record.extra_data

            # Add breadcrumbs to properties
            if breadcrumbs:
                properties["Breadcrumbs"] = breadcrumbs

            # Add any extra fields from the record
            excluded_fields = {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "extra_data",
            }

            for key, value in record.__dict__.items():
                if key not in excluded_fields:
                    properties[key] = value

            # Transform specific fields from snake_case to PascalCase
            properties = self._transform_property_keys(properties)

            payload = [
                {
                    "Body": json.dumps(
                        RailtownPayload(
                            Message=record.getMessage(),
                            Level=level_str,
                            Exception=exception_info,
                            OrganizationId=config["o"],
                            ProjectId=config["p"],
                            EnvironmentId=config["e"],
                            Runtime="python-traceback",
                            TimeStamp=datetime.datetime.now().isoformat(),
                            Properties=properties,
                        ).model_dump()
                    ),
                    "UserProperties": {
                        "AuthenticationCode": config["h"],
                        "ClientVersion": "Python-2.0.7",  # VERSION Must match __version__ in __init__.py
                        "Encoding": "utf-8",
                        "ConnectionName": config["u"],
                    },
                }
            ]

            http_client = get_http_client()
            http_client.post(
                "https://" + config["u"],
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "railtown-py(python)",
                },
                json_data=payload,
                timeout=10,
            )

        except Exception as e:
            # Avoid infinite recursion by not logging handler errors
            print(f"Railtown handler error: {e}")

    def _get_config(self) -> dict[str, Any] | None:
        """Get the Railtown configuration."""
        if self._config is None:
            try:
                self._config = get_config()
            except Exception:
                return None
        return self._config

    def _transform_property_keys(self, properties: dict[str, Any]) -> dict[str, Any]:
        """
        Transform property keys from snake_case to PascalCase.

        Args:
            properties: The properties dictionary to transform

        Returns:
            A new dictionary with transformed keys
        """
        # Define specific mappings for special cases
        specific_mappings = {
            "run_id": "ConductrAgentRunId",
            "session_id": "ConductrAgentSessionId",
            "node_id": "ConductrAgentNodeId",
        }

        transformed_properties = {}

        for key, value in properties.items():
            # Check if this key has a specific mapping first
            if key in specific_mappings:
                transformed_properties[specific_mappings[key]] = value
            # Convert other snake_case keys to PascalCase
            elif "_" in key:
                # Split by underscore and capitalize each word
                words = key.split("_")
                pascal_key = "".join(word.capitalize() for word in words)
                transformed_properties[pascal_key] = value
            else:
                # Keep the original key if it's not snake_case
                transformed_properties[key] = value

        return transformed_properties

    def _get_platform_api_url(self) -> str | None:
        """
        Internal method to get the platform URL from the Railtown API.
        """
        config = self._get_config()
        if not config:
            return None

        url = config["u"]

        if url.startswith("tst"):
            return "https://testcndr.railtown.ai/api"
        elif url.startswith("ovr"):
            return "https://overwatch.railtown.ai/api"
        else:
            return "https://cndr.railtown.ai/api"

    def _get_conductr_presigned_sas_url(self) -> str | None:
        """
        Internal method to get a presigned SAS URL from the Railtown API.

        Returns:
            str | None: The presigned SAS URL if successful, None otherwise
        """
        try:
            config = self._get_config()
            if not config:
                return None

            platform_api_url = self._get_platform_api_url()
            endpoint_url = f"{platform_api_url}/observe/exchange"
            railtown_api_key = get_api_key()

            # Prepare the request headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "railtown-py(python)",
                "Authorization": f"Bearer {config['h']}",
            }

            # Prepare the payload as the Railtown API key with encapsulating double quotes
            payload = f'"{railtown_api_key}"'

            # Make the request to get the presigned SAS URL
            http_client = get_http_client()
            response = http_client.post(
                endpoint_url,
                headers=headers,
                data=payload,
                timeout=10,
            )

            if response.ok:
                logging.info(f"✅ Successfully got presigned SAS URL: {response.text.strip()}")
                return response.text.strip()
            else:
                logging.error(f"Failed to get presigned SAS URL: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error getting presigned SAS URL: {e}")
            return None

    def _is_session_format(self, data: dict[str, Any]) -> bool:
        """
        Check if the data is in the new session format by looking for the 'runs' field.

        Args:
            data: The data payload to check

        Returns:
            bool: True if this is session format, False otherwise
        """
        return "runs" in data and isinstance(data.get("runs"), list)

    def _validate_session_format(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate that session format data has all required fields.

        Args:
            data: The session data to validate

        Returns:
            tuple: (is_valid, missing_fields_list)
        """
        # Check for either 'name' or 'session_name' field (railtracks uses 'session_name')
        # Allow them to be null/empty since we can fallback to session_id
        has_name_field = "name" in data or "session_name" in data
        if not has_name_field:
            return False, ["missing 'name' or 'session_name' field"]

        required_session_fields = ["session_id", "start_time", "end_time", "runs"]
        missing_fields = [field for field in required_session_fields if field not in data]

        if missing_fields:
            return False, missing_fields

        # Validate that runs is a non-empty list
        runs = data.get("runs", [])
        if not isinstance(runs, list) or len(runs) == 0:
            return False, ["runs must be a non-empty list"]

        # Validate each run has required fields (make start_time, end_time, status optional)
        required_run_fields = ["run_id", "name"]
        for i, run in enumerate(runs):
            missing_run_fields = [field for field in required_run_fields if field not in run]
            if missing_run_fields:
                return False, [f"run[{i}] missing: {missing_run_fields}"]

            # Validate run has required arrays
            for array_field in ["nodes", "steps", "edges"]:
                if array_field not in run or not isinstance(run[array_field], list):
                    return False, [f"run[{i}] missing or invalid {array_field} array"]

        return True, []

    def _enrich_run_with_session_data(self, session_data: dict[str, Any], run_data: dict[str, Any]) -> dict[str, Any]:
        """
        Enrich a run with session metadata and rename run fields for clarity.

        Args:
            session_data: The session data containing metadata
            run_data: The individual run data to enrich

        Returns:
            dict: The enriched run data with session metadata and renamed fields
        """
        enriched_data = {}

        # Add session metadata - use the session_id from the session data
        enriched_data["session_id"] = session_data["session_id"]

        # Handle both 'name' and 'session_name' fields (railtracks uses 'session_name')
        # Fallback to session_id if session_name is null or empty
        session_name = session_data.get("name") or session_data.get("session_name")
        if not session_name:  # Handle None, empty string, etc.
            session_name = session_data.get("session_id", "Unknown Session")
        enriched_data["session_name"] = session_name
        enriched_data["session_start_time"] = session_data["start_time"]
        enriched_data["session_end_time"] = session_data["end_time"]

        # Add run metadata with renamed fields (handle missing fields gracefully)
        enriched_data["run_id"] = run_data["run_id"]
        enriched_data["run_name"] = run_data["name"]  # Run name

        # Handle optional run fields with defaults - use current timestamp for missing times
        current_timestamp = time.time()
        enriched_data["run_start_time"] = run_data.get("start_time", current_timestamp)
        enriched_data["run_end_time"] = run_data.get("end_time", current_timestamp)
        enriched_data["run_status"] = run_data.get("status", "Unknown")

        # Add the original arrays
        enriched_data["nodes"] = run_data["nodes"]
        enriched_data["steps"] = run_data["steps"]
        enriched_data["edges"] = run_data["edges"]

        return enriched_data

    def _enrich_old_format_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Enrich old format data with default values for new session and run fields.
        Only generates new session_id if one doesn't exist. Preserves null values.
        Preserves original fields for backward compatibility.

        Args:
            data: The old format data to enrich

        Returns:
            dict: The enriched data with session and run metadata matching the required structure
        """
        # Start with a copy of original data to preserve all fields
        enriched_data = dict(data)

        current_time = int(time.time() * 1000)  # Convert to milliseconds

        # Only generate new session_id if one doesn't exist
        if "session_id" not in enriched_data or not enriched_data["session_id"]:
            enriched_data["session_id"] = str(uuid.uuid4())

        # Session name should be stable - use existing name or default
        enriched_data["session_name"] = data.get("name", "Agent Run")
        enriched_data["session_start_time"] = data.get("start_time", current_time)
        enriched_data["session_end_time"] = data.get("end_time", current_time)

        # Run metadata
        if "run_id" not in enriched_data or not enriched_data["run_id"]:
            enriched_data["run_id"] = str(uuid.uuid4())
        enriched_data["run_name"] = data.get("name", "Agent Run")
        enriched_data["run_start_time"] = data.get("start_time", current_time)
        enriched_data["run_end_time"] = data.get("end_time", current_time)
        enriched_data["run_status"] = data.get("status", "Completed")

        # Ensure arrays exist and are not null
        enriched_data["nodes"] = data.get("nodes", [])
        enriched_data["steps"] = data.get("steps", [])
        enriched_data["edges"] = data.get("edges", [])

        # Return enriched data preserving null values
        return enriched_data

    def _upload_single_agent_run(self, data: dict[str, Any]) -> bool:
        """
        Internal method to upload a single JSON object to blob storage using a presigned SAS URL.
        Only uploads if the data contains nodes, steps, and edges with length > 0.
        Also validates that the data contains required fields: name, session_id, and run_id.

        Args:
            data: The JSON object to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate required fields - support both old and new formats
            # New enriched format has session_* and run_* fields
            # Old format has direct name, session_id, run_id fields
            is_enriched_format = (
                "session_id" in data and "session_name" in data and "run_id" in data and "run_name" in data
            )

            if is_enriched_format:
                # This is enriched session format data
                required_fields = [
                    "session_id",
                    "session_name",
                    "session_start_time",
                    "session_end_time",
                    "run_id",
                    "run_name",
                    "run_start_time",
                    "run_end_time",
                    "run_status",
                ]
            else:
                # This is old format data
                required_fields = ["name", "session_id", "run_id"]

            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                logging.error(f"Skipping upload: data missing required fields: {missing_fields}")
                return False

            # Enrich old format data with session and run metadata for consistency
            if not is_enriched_format:
                logging.info("Enriching old format data with session and run metadata")
                data = self._enrich_old_format_data(data)
            # For enriched format, preserve existing session_id

            # Check if data has the required fields with length > 0
            nodes = data.get("nodes", [])
            steps = data.get("steps", [])
            edges = data.get("edges", [])

            if not (len(nodes) > 0 and len(steps) > 0 and len(edges) > 0):
                logging.info("Skipping upload: data missing required fields (nodes, steps, edges) or they are empty")
                return False

            # sort the root keys in the following order:
            # - session_id, session_name, session_start_time, session_end_time, run_id, run_name,
            # - run_start_time, run_end_time, run_status, nodes, edges, steps
            key_order = [
                "session_id",
                "session_name",
                "session_start_time",
                "session_end_time",
                "run_id",
                "run_name",
                "run_start_time",
                "run_end_time",
                "run_status",
                "nodes",
                "edges",
                "steps",
            ]
            data = dict(
                sorted(data.items(), key=lambda x: key_order.index(x[0]) if x[0] in key_order else len(key_order))
            )

            # Get the presigned SAS URL
            sas_url = self._get_conductr_presigned_sas_url()
            if not sas_url:
                logging.error("Failed to get presigned SAS URL")
                return False

            logging.info(f"upload_agent_run(): Uploading JSON data to blob: {sas_url}")
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, ensure_ascii=False)

            # Upload the JSON data to the blob storage
            http_client = get_http_client()
            response = http_client.put(
                sas_url,
                data=json_data.encode("utf-8"),
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "x-ms-version": "2022-11-02",
                    "x-ms-blob-type": "BlockBlob",
                },
                timeout=30,
            )

            if response.ok:
                logging.info(f"✅ Successfully saved to blob: {response.status_code}")
                return True
            else:
                logging.error(f"Failed to save to blob: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error saving to blob: {e}")
            return False

    def upload_agent_run(self, payloads: str | dict[str, Any] | list[dict[str, Any]]) -> bool:
        """
        Public method to save JSON object(s) to blob storage using presigned SAS URLs.
        Accepts either a single JSON object or an array of JSON objects.
        Only uploads if each payload contains nodes, steps, and edges with length > 0.
        When an array is provided, each payload gets its own fresh SAS URL.

        Args:
            payloads: Either a single JSON object or a list of JSON objects to save

        Returns:
            bool: True if all uploads succeed, False if any upload fails
        """
        try:
            # Normalize input: if single dict, wrap in list for uniform processing
            if isinstance(payloads, dict):
                payload_list = [payloads]
            elif isinstance(payloads, list):
                payload_list = payloads
            elif isinstance(payloads, str):
                loaded = json.loads(payloads)
                if isinstance(loaded, list):
                    payload_list = loaded
                else:
                    payload_list = [loaded]

            if not payload_list:
                logging.info("No payloads to upload")
                return True

            logging.info(f"Processing {len(payload_list)} payload(s) for upload")

            # Process each payload individually
            success_count = 0
            total_count = len(payload_list)

            for i, payload in enumerate(payload_list):
                logging.info(f"Processing payload {i + 1}/{total_count}")

                # Check if this is session format
                if self._is_session_format(payload):
                    # Process session format: validate and extract runs
                    is_valid, validation_errors = self._validate_session_format(payload)
                    if not is_valid:
                        logging.error(
                            f"❌ Session payload {i + 1}/{total_count} validation failed: {validation_errors}"
                        )
                        continue

                    # Process each run in the session
                    session_runs = payload["runs"]
                    logging.info(f"Session payload {i + 1}/{total_count} contains {len(session_runs)} runs")

                    session_success_count = 0
                    for j, run in enumerate(session_runs):
                        logging.info(f"Processing run {j + 1}/{len(session_runs)} in session {i + 1}")

                        # Enrich run with session data
                        enriched_run = self._enrich_run_with_session_data(payload, run)

                        if self._upload_single_agent_run(enriched_run):
                            session_success_count += 1
                            logging.info(f"✅ Run {j + 1}/{len(session_runs)} in session {i + 1} uploaded successfully")
                        else:
                            logging.error(f"❌ Run {j + 1}/{len(session_runs)} in session {i + 1} failed to upload")

                    # Session is successful if all runs succeed
                    if session_success_count == len(session_runs):
                        success_count += 1
                        logging.info(f"✅ Session payload {i + 1}/{total_count} uploaded successfully")
                    else:
                        logging.error(
                            f"❌ Session payload {i + 1}/{total_count} partially failed: "
                            f"{session_success_count}/{len(session_runs)} runs uploaded"
                        )
                else:
                    # Process old format payload
                    if self._upload_single_agent_run(payload):
                        success_count += 1
                        logging.info(f"✅ Payload {i + 1}/{total_count} uploaded successfully")
                    else:
                        logging.error(f"❌ Payload {i + 1}/{total_count} failed to upload")

            # Return True only if ALL uploads succeed
            all_succeeded = success_count == total_count
            if all_succeeded:
                logging.info(f"✅ All {total_count} payload(s) uploaded successfully")
            else:
                logging.error(f"❌ {total_count - success_count}/{total_count} payload(s) failed to upload")

            return all_succeeded

        except Exception as e:
            logging.error(f"Error in batch upload processing: {e}")
            return False
