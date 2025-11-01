# Project Samarth - Event-Driven Architecture - Loom Video Script (2 minutes)

## Opening (15 seconds)
"Hi! I'm presenting Project Samarth with Event-Driven Architecture - a highly scalable, decoupled Q&A system over India's agricultural and climate data from data.gov.in. This version demonstrates asynchronous event-driven design patterns used in modern microservices."

## Architecture Choice: Why Event-Driven? (25 seconds)

**The Challenge:**
Traditional synchronous systems create tight coupling. Components call each other directly, making it hard to scale, monitor, or distribute across services.

**The Solution: Pub/Sub Event Pipeline**
- Components communicate only through events
- Event bus acts as central message broker
- Each stage subscribes to input events, publishes output events
- Complete decoupling → Independent scaling and deployment

**Show Diagram:**
```
Query → Event Bus → [Parse] → [DataLoad] → [Analysis] → [Format] → Response
         ↓ events    ↓ events   ↓ events    ↓ events     ↓ events
    query.received  .parsed    .loaded     .complete    .ready
```

## Key Architecture Components (35 seconds)

### 1. Event Bus (`app/event_bus.py`)
```python
class EventBus:
    def publish(self, topic: str, data: dict):
        # Notify all subscribers

    def subscribe(self, topic: str, handler: Callable):
        # Register handler for topic
```

**Why this matters:**
- **Pub/Sub pattern** → Loose coupling
- **Observable** → Every event can be logged/monitored
- **Scalable** → Replace with Redis/Kafka for distributed systems

**Show event flow:**
```
1. query.received   → ParseStage listens
2. query.parsed     → DataLoadStage listens
3. data.loaded      → AnalysisStage listens
4. analysis.complete → FormatStage listens
5. response.ready   → QueryExecutor returns result
```

### 2. Pipeline Stages (`app/pipeline/`)
```
pipeline/
├── base_stage.py          # Abstract stage template
├── parse_stage.py         # Stage 1: Parse question
├── data_load_stage.py     # Stage 2: Load datasets
├── analysis_stage.py      # Stage 3: Analyze data
└── format_stage.py        # Stage 4: Format results
```

**Show code snippet:**
Open `app/pipeline/parse_stage.py`:
```python
class ParseStage(PipelineStage):
    def input_topic(self) -> str:
        return "query.received"

    def output_topic(self) -> str:
        return "query.parsed"

    def process(self, data, metadata):
        # Parse question
        return parsed_result
```

**Template Method Pattern:**
- Base class handles event subscriptions
- Subclasses define `input_topic`, `output_topic`, `process`
- Auto-wiring at initialization

### 3. Async Orchestration (`app/query_executor.py`)
```python
async def execute_query(self, question: str):
    # Create future
    self.result_future = loop.create_future()

    # Publish initial event
    event_bus.publish("query.received", {"question": question})

    # Wait for final result (with timeout)
    result = await asyncio.wait_for(self.result_future, timeout=30.0)
    return result
```

**Why async?**
- Non-blocking execution
- Can process multiple queries concurrently
- Timeout handling for pipeline failures

## Live Demo (30 seconds)

**[Show terminal + browser side by side]**

1. **Start Server:**
```bash
cd backend
uvicorn app.main:app --reload --port 8002
```

2. **Test Query:** "Compare rainfall in Kerala and Punjab over 3 years"

**Show Logs - Event Flow:**
```
INFO: Publishing event: query.received
INFO: ParseStage processing event
INFO: Publishing event: query.parsed
INFO: DataLoadStage processing event
INFO: Publishing event: data.loaded
INFO: AnalysisStage processing event
INFO: Publishing event: analysis.complete
INFO: FormatStage processing event
INFO: Publishing event: response.ready
INFO: Query completed successfully
```

**Point out:**
- Each stage executes independently
- Events flow through the pipeline
- Clear audit trail of data processing

3. **Show Response:**
- Same answer quality as other architectures
- Went through 4 stages asynchronously
- All events logged for observability

## Adding a New Stage - Live Code (15 seconds)

**Show how easy it is to extend:**

Create `app/pipeline/cache_stage.py`:
```python
class CacheStage(PipelineStage):
    def input_topic(self) -> str:
        return "query.parsed"  # Listen after parsing

    def output_topic(self) -> str:
        return "cache.checked"

    def process(self, data, metadata):
        # Check cache, return if found
        # Otherwise pass through
        return data
```

**That's it!** Stage automatically:
- Subscribes to events
- Processes data
- Publishes results
- Integrates with pipeline

No changes to other stages. True decoupling.

## Technical Highlights (15 seconds)

**Architectural Patterns:**
1. **Event-Driven Architecture** - Pub/sub communication
2. **Observer Pattern** - Stages observe event bus
3. **Template Method** - Base stage defines workflow
4. **Async/Await** - Non-blocking execution
5. **Future Pattern** - Async result handling

**Production Benefits:**
- **Scalability:** Each stage can be separate microservice
- **Observability:** Every event is traceable
- **Resilience:** Stage failures isolated via events
- **Flexibility:** Add/remove stages without code changes

## Comparison to Other Architectures (10 seconds)

| Architecture | Coupling | Scalability | Observability | Async |
|--------------|----------|-------------|---------------|-------|
| Monolithic | High | Limited | Manual | No |
| Plugin | None | Moderate | Manual | No |
| **Event-Driven** | Minimal | Excellent | Built-in | Yes |

**Event-Driven wins when:** You need maximum scalability, observability, and distributed system readiness.

## Path to Microservices (10 seconds)

**Current:** All stages in one process
```
FastAPI → Event Bus (in-memory) → 4 Stages (same process)
```

**Future:** Distributed across services
```
API Service → Redis Pub/Sub → Stage1 Service
                            → Stage2 Service
                            → Stage3 Service
                            → Stage4 Service
```

**Migration is simple:** Replace EventBus with Redis client. Same code, different deployment.

## Closing (5 seconds)
"This event-driven architecture demonstrates enterprise-grade scalability. From monolith to microservices with the same codebase. Perfect for cloud-native, distributed systems. Thank you!"

---

## Demo Checklist

**Preparation:**
- [ ] Server running on port 8002
- [ ] Browser ready with test queries
- [ ] Terminal showing event logs
- [ ] Code editor with pipeline stages open

**Show During Demo:**
- [ ] Event flow in logs (5 events per query)
- [ ] Pipeline stage files
- [ ] Base stage template method
- [ ] Async/await in query_executor.py
- [ ] Timeout handling

**Code to Highlight:**
- [ ] Event bus `publish()` and `subscribe()`
- [ ] Pipeline stage `input_topic()` and `output_topic()`
- [ ] Template method in base_stage.py
- [ ] Future pattern in query_executor.py

## Key Differentiators to Emphasize

1. **Pub/Sub Decoupling:** Stages don't call each other directly
2. **Event Observability:** Every action is an observable event
3. **Async Processing:** Non-blocking, concurrent query handling
4. **Cloud-Native:** Ready for Kubernetes, Redis, Kafka
5. **Audit Trail:** Complete event history for debugging
6. **Production Pattern:** Netflix, Uber, Amazon all use event-driven architectures
