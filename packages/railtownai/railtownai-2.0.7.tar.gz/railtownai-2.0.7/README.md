# Railtown AI Logging Python Package

A Python logging handler that integrates with Railtown AI for error tracking and monitoring, similar to Sentry's approach.

## Setup

1. Sign up for [Railtown AI - Conductr](https://conductr.ai)
2. Create a project, navigate to the Project Configuration page, and copy your API key
3. In your app:

   1. Install the Railtown AI SDK: `pip install railtownai`
   2. Initialize Railtown AI with your API key: `railtownai.init('YOUR_RAILTOWN_API_KEY')`
   3. Use Python's native logging - all logs will automatically be sent to Railtown AI

## Basic Usage

```python
import logging
import railtownai

# Initialize Railtown AI
railtownai.init('YOUR_RAILTOWN_API_KEY')

# Use Python's native logging - all logs are sent to Railtown AI
logging.info("User logged in", extra={"user_id": 123, "action": "login"})
logging.warning("High memory usage detected", extra={"memory_usage": "85%"})
logging.error("Database connection failed", extra={"db_host": "localhost"})

# Log exceptions with full stack traces
try:
    result = 1 / 0
except Exception:
    logging.exception("Division by zero error")
```

## Agent Observability

Track and monitor your AI agent executions with structured data upload. This feature allows you to store detailed information about agent runs, including nodes, steps, and execution flow.

### Quick Setup

1. **[Sign up for Conductr AI for FREE](https://conductr.ai)**
2. **Initialize Conductr AI** with your API key in your Project Configuration (Logs)
3. **Structure your agent data** in the session format
4. **Upload using `upload_agent_run()`**

```python
import json
import logging

import railtownai
import railtracks as rt
from fastapi import FastAPI, Query

logger = logging.getLogger(__name__)

# Initialize SDK
railtownai.init("YOUR_API_KEY")

app = FastAPI()

# Replace with your actual agent
# from your_agents_module import WeatherAgent
WeatherAgent = TicketTriageAgent  # placeholder if you have not renamed it yet


@app.get("/weather")
async def get_weather(
    city: str = Query(..., description="City name like Vancouver"),
    units: str = Query("metric", description="metric or imperial"),
):
    try:
        # Build the message history for the weather request
        message_history = rt.llm.MessageHistory([
            rt.llm.UserMessage(f"Weather request\nCity: {city}\nUnits: {units}")
        ])

        # Call the agent
        with rt.Session(name="agent-session") as session:
            result = await rt.call(WeatherAgent, message_history)

            # Upload agent run data to RailTown AI
            agent_run_data = session.payload()
            success = railtownai.upload_agent_run(agent_run_data)

            if success:
                logger.info("Agent run data uploaded successfully")
            else:
                logger.error("Failed to upload agent run data")

        logger.info("Weather processing completed successfully")

        return {
            "success": True,
            "city": city,
            "units": units,
            "analysis": str(result),
        }

    except Exception as e:
        logger.error(f"Error processing weather request: {e}")
        return {"error": str(e)}


```

If you are using the [Railtown AI Python Logger](https://pypi.org/project/railtownai/), [RailTracks Frameworkr](https://pypi.org/project/railtracks/)
automatically propagates any errors at run-time and attaches the `node_id`, `run_id`, and `session_id` via the python
`logging` package, so that Conductr Agent Observability platform can show you exactly which nodes
failed or retried.

## Breadcrumbs

Railtown AI supports breadcrumbs - contextual information that gets attached to log events. This is useful for tracking user actions or system state leading up to an error.

```python
import logging
import railtownai

railtownai.init('YOUR_RAILTOWN_API_KEY')

# Add breadcrumbs throughout your application
railtownai.add_breadcrumb("User clicked login button", category="ui")
railtownai.add_breadcrumb("Validating user credentials", category="auth")
railtownai.add_breadcrumb("Database query executed", category="database",
                         data={"query": "SELECT * FROM users", "duration_ms": 45})

# When an error occurs, all breadcrumbs are automatically attached
try:
    # Some operation that might fail
    result = risky_operation()
except Exception:
    logging.exception("Operation failed")  # This will include all the breadcrumbs above
```

## Advanced Usage

### Custom Logging Configuration

```python
import logging
import railtownai

# Initialize Railtown AI
railtownai.init('YOUR_RAILTOWN_API_KEY')

# Configure your own logger
logger = logging.getLogger('myapp')
logger.setLevel(logging.DEBUG)

# Add console handler for local development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Railtown handler is automatically added to root logger
logger.info("Application started")
logger.error("Something went wrong", extra={"component": "payment_processor"})
```

## Configuration

The Railtown handler automatically:

- Sets the root logger level to INFO (if it was higher)
- Adds itself to the root logger
- Handles API key validation
- Manages breadcrumbs across all loggers

### Key Features:

- Use Python's native `logging.info()`, `logging.error()`, `logging.exception()`
- All logs automatically include breadcrumbs
- Seamless integration with Python's logging ecosystem
- Support for structured logging with `extra` parameter

## Contributing

See the [contributing guide](./CONTRIBUTING.md) for more information.

## License

The MIT License is a permissive license that allows you to:

- Use the software for any purpose
- Modify the software
- Distribute the software
- Use it commercially
- Use it privately
- Sublicense it

The only requirement is that the original copyright notice and license must be included in all copies or substantial portions of the software.
