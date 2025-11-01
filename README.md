# Project Samarth - Event-Driven Architecture

A scalable, decoupled data analysis API built with **Event-Driven Architecture** pattern for analyzing Indian agriculture and rainfall data from data.gov.in.

## Architecture Highlights

### Event-Driven Pipeline

This project uses a **pub/sub event-driven architecture** with asynchronous event flow through specialized pipeline stages.

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  QueryExecutor   │
                    │  (Orchestrator)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    Event Bus     │
                    │  (Pub/Sub Core)  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐      ┌──────▼──────┐      ┌──────▼──────┐
   │  Parse   │──┐   │  DataLoad   │──┐   │  Analysis   │──┐
   │  Stage   │  │   │   Stage     │  │   │   Stage     │  │
   └──────────┘  │   └─────────────┘  │   └─────────────┘  │
                 │                    │                    │
        query.received          query.parsed         data.loaded
                 │                    │                    │
                 │                    │                    │
   ┌─────────────▼────────────────────▼────────────────────▼─────┐
   │                         Format Stage                         │
   └──────────────────────────┬───────────────────────────────────┘
                              │
                       response.ready
```

### Event Flow

1. **query.received** → ParseStage parses natural language
2. **query.parsed** → DataLoadStage fetches required datasets
3. **data.loaded** → AnalysisStage performs calculations
4. **analysis.complete** → FormatStage formats results
5. **response.ready** → QueryExecutor returns to user

### Key Architectural Benefits

- **Decoupling**: Stages communicate only through events
- **Scalability**: Stages can be distributed across services
- **Observability**: Every event can be logged/monitored
- **Flexibility**: Easy to add stages or modify flow
- **Async Processing**: Non-blocking event propagation

### How It Works

1. **Event Bus**: Central pub/sub message broker
2. **Pipeline Stages**: Independent processors subscribing to specific topics
3. **Future Pattern**: QueryExecutor waits asynchronously for final result
4. **Error Handling**: Errors propagated through `pipeline.error` event

## Project Structure

```
project-samarth-events/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── query_executor.py       # Pipeline orchestrator
│   │   ├── event_bus.py            # Pub/sub event bus
│   │   ├── question_parser.py      # NLP intent parser
│   │   ├── data_manager.py         # Data.gov.in API client
│   │   ├── config.py               # Configuration
│   │   └── pipeline/
│   │       ├── base_stage.py       # Abstract pipeline stage
│   │       ├── parse_stage.py      # Stage 1: Parse question
│   │       ├── data_load_stage.py  # Stage 2: Load datasets
│   │       ├── analysis_stage.py   # Stage 3: Analyze data
│   │       └── format_stage.py     # Stage 4: Format results
│   └── requirements.txt
└── README.md
```

## Features

- **Event-Driven Processing**: Fully async pipeline with event bus
- **4 Analysis Types**: Compare rainfall, district extremes, trends, policy arguments
- **Real-time Data**: Fetches latest data from data.gov.in API
- **Timeout Handling**: 30-second query timeout with proper error handling
- **Observability**: Comprehensive logging at each stage

## Setup Instructions

### Prerequisites

- **Python 3.12** (Required - pandas 2.1.4 incompatible with Python 3.14)
- data.gov.in API key

### Installation

```bash
# Navigate to backend folder
cd backend

# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set your data.gov.in API key:

```bash
export DATAGOV_API_KEY=your_api_key_here
```

### Run the Server

```bash
uvicorn app.main:app --reload --port 8002
```

The API will be available at `http://localhost:8002`

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{"status": "ok"}
```

### Query Endpoint
```bash
POST /ask
Content-Type: application/json

{
  "question": "Compare rainfall in Kerala and Punjab over 3 years"
}
```

Response:
```json
{
  "answer": "Compared rainfall for Kerala and Punjab over 3 year(s). Kerala averaged 3050.0 mm while Punjab averaged 683.3 mm.",
  "tables": [
    {
      "title": "Average annual rainfall (mm)",
      "headers": ["Year", "Kerala", "Punjab"],
      "rows": [[2020, 3100.0, 710.0], [2021, 3000.0, 650.0], [2022, 3050.0, 690.0]]
    }
  ],
  "citations": [...],
  "debug": {
    "intent": "compare_rainfall_and_crops",
    "params": {...}
  }
}
```

### Refresh Data
```bash
POST /refresh
```

Clears cache and fetches fresh data from data.gov.in

## Event Bus API

### Publishing Events

```python
from app.event_bus import event_bus

event_bus.publish(
    topic="your.event.topic",
    data={"key": "value"},
    metadata={"source": "your_stage"}
)
```

### Subscribing to Events

```python
from app.event_bus import event_bus, Event

def handler(event: Event):
    print(f"Received: {event.data}")

event_bus.subscribe("your.event.topic", handler)
```

## Creating a New Pipeline Stage

Create a new stage in `app/pipeline/your_stage.py`:

```python
from typing import Any
from .base_stage import PipelineStage

class YourStage(PipelineStage):
    """Your custom pipeline stage."""

    def input_topic(self) -> str:
        """Event topic to listen to."""
        return "previous.stage.output"

    def output_topic(self) -> str:
        """Event topic to publish to."""
        return "your.stage.output"

    def process(self, data: Any, metadata: dict) -> Any:
        """
        Process the data and return result.

        Args:
            data: Input data from previous stage
            metadata: Event metadata

        Returns:
            Processed data for next stage
        """
        # Your processing logic
        result = do_something(data)
        return result
```

Register in `query_executor.py`:

```python
from .pipeline.your_stage import YourStage

self.your_stage = YourStage(event_bus)
```

The stage automatically subscribes to its input topic and publishes to output topic!

## Example Queries

```
"Compare rainfall in Kerala and Punjab over 3 years"
"Which district in Punjab had the highest wheat production in 2020?"
"Show rice production trend in Tamil Nadu over 5 years"
"Why should Karnataka shift from cotton to sugarcane?"
```

## Event Topics

| Topic | Publisher | Subscriber | Data |
|-------|-----------|------------|------|
| `query.received` | QueryExecutor | ParseStage | `{question: str}` |
| `query.parsed` | ParseStage | DataLoadStage | `{question, intent, params}` |
| `data.loaded` | DataLoadStage | AnalysisStage | `{intent, params, datasets}` |
| `analysis.complete` | AnalysisStage | FormatStage | `{intent, params, results}` |
| `response.ready` | FormatStage | QueryExecutor | `{answer, tables, citations}` |
| `pipeline.error` | Any Stage | QueryExecutor | `{error: str, stage: str}` |

## Technology Stack

- **FastAPI**: Modern async web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Asyncio**: Asynchronous event handling
- **Uvicorn**: ASGI server
- **Python 3.12**: Runtime environment

## Data Sources

- **Agriculture**: District-wise crop production statistics
  - Source: https://data.gov.in/resources/district-wise-crop-production-statistics

- **Rainfall**: Sub-division wise rainfall distribution
  - Source: https://data.gov.in/resources/rainfall-sub-division-wise-distribution

## Architecture Advantages

### Scalability
- Stages can run as separate microservices
- Event bus can be replaced with Redis/Kafka for distribution
- Horizontal scaling of individual stages

### Maintainability
- Each stage is isolated and testable
- Clear event contracts between stages
- Easy to debug with event logging

### Flexibility
- Add/remove stages without touching other code
- Change stage order by adjusting subscriptions
- A/B test different implementations

### Observability
- Every event can be logged
- Easy to add monitoring/metrics
- Clear audit trail of data flow

## Extending to Distributed System

To scale across multiple servers:

1. Replace `EventBus` with Redis Pub/Sub or Kafka
2. Deploy each stage as a separate service
3. Use message queue for reliable delivery
4. Add distributed tracing (OpenTelemetry)

```python
# Example with Redis
import redis
from rq import Queue

redis_conn = redis.Redis()
queue = Queue(connection=redis_conn)

# Publish
queue.enqueue('your.topic', data)

# Subscribe
queue.listen('your.topic', handler)
```

## License

This project is part of the Project Samarth prototype series.
