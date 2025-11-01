# Project Samarth - Event-Driven Architecture Implementation Guide

## 🎯 What You Need to Complete

This scaffold demonstrates the **Event-Driven Architecture** pattern. I've created the core event bus and pipeline stages - you need to implement the analysis and formatting logic.

### ✅ Already Done (Core Architecture):
- ✅ Event bus with pub/sub system (`app/event_bus.py`)
- ✅ Base pipeline stage class (`app/pipeline/base_stage.py`)
- ✅ Parse stage - fully implemented (`app/pipeline/parse_stage.py`)
- ✅ Data load stage - fully implemented (`app/pipeline/data_stage.py`)
- ✅ Analysis stage - structure ready, TODOs marked (`app/pipeline/analysis_stage.py`)
- ✅ Format stage - structure ready, TODOs marked (`app/pipeline/format_stage.py`)
- ✅ Query executor - coordinates pipeline (`app/query_executor.py`)
- ✅ Data manager and parser (reused from Project 1)

### 🔨 What YOU Need to Implement:

#### 1. Complete the Analysis Stage (1 hour)

Open `app/pipeline/analysis_stage.py` and complete the 4 analysis methods:

**TODO sections marked in code:**
```python
# TODO: Implement _analyze_compare_rainfall_crops()
# TODO: Implement _analyze_district_extremes()
# TODO: Implement _analyze_production_trend()
# TODO: Implement _analyze_policy_arguments()
```

**Reference:** Copy logic from Project 1's `analytics.py` - each method has the same logic, just needs to be adapted to return dictionaries instead of formatted responses.

**Sample Prompt for testing:**
```
How does annual rainfall in Kerala compare to Punjab over 5 years?
List top Wheat and Maize crops by district.
```

#### 2. Complete the Format Stage (45 minutes)

Open `app/pipeline/format_stage.py` and complete the 4 formatting methods:

**TODO sections marked in code:**
```python
# TODO: Implement _format_compare_rainfall_crops()
# TODO: Implement _format_district_extremes()
# TODO: Implement _format_production_trend()
# TODO: Implement _format_policy_arguments()
```

**Reference:** Project 1's `analytics.py` has the formatting logic - extract the parts that generate answer text, tables, and citations.

#### 3. Update main.py (15 minutes)

Replace the analytics engine with the event-driven query executor:

```python
# OLD (Project 1):
from .analytics import AnalyticsEngine
analytics = AnalyticsEngine(data_manager)

# NEW (Project 3 - Event-Driven):
from .query_executor import QueryExecutor
executor = QueryExecutor(parser, data_manager)

# In /ask endpoint (make it async):
@app.post("/ask")
async def ask_question(question_request: QuestionRequest):
    try:
        result = await executor.execute_query(question_request.question)
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 4. Update Sample Data (15 minutes)

Add states/crops needed for new prompts:
- Kerala: Wheat, Maize (add if missing)
- Punjab: Wheat, Maize (already exists)
- Maharashtra: Soybean, Pearl Millet (add if missing)
- Tamil Nadu: Pearl Millet (add if missing)

Edit `backend/data/sample_agriculture.csv` to add missing crop data.

#### 5. Test (10 minutes)

```bash
cd backend
python test_prompts.py
```

Should see: **100% success rate (4/4 prompts)**

---

## 🏗️ Architecture Highlights (Explain in Loom)

### Event-Driven Pipeline Flow

```
1. API receives question
         ↓
2. QueryExecutor publishes "query.received" event
         ↓
3. ParseStage listens → parses → publishes "query.parsed"
         ↓
4. DataLoadStage listens → loads data → publishes "data.loaded"
         ↓
5. AnalysisStage listens → analyzes → publishes "analysis.complete"
         ↓
6. FormatStage listens → formats → publishes "response.ready"
         ↓
7. QueryExecutor receives result and returns to API
```

### Pub/Sub Pattern
```python
# Each stage subscribes to events:
event_bus.subscribe("query.parsed", self._handle_event)

# And publishes results:
event_bus.publish(
    topic="data.loaded",
    data={"datasets": {...}},
    metadata={...}
)
```

**Benefits:**
- Loose coupling - stages don't know about each other
- Easy to add/remove stages without changing others
- Asynchronous processing
- Event history for debugging

### Observer Pattern
Pipeline stages observe the event bus and react to events - they don't directly call each other.

### Template Method Pattern
Base `PipelineStage` class defines workflow, stages implement specific `process()` logic.

---

## 📝 Completion Checklist

- [ ] Complete `_analyze_compare_rainfall_crops()` in analysis_stage.py
- [ ] Complete `_analyze_district_extremes()` in analysis_stage.py
- [ ] Complete `_analyze_production_trend()` in analysis_stage.py
- [ ] Complete `_analyze_policy_arguments()` in analysis_stage.py
- [ ] Complete `_format_compare_rainfall_crops()` in format_stage.py
- [ ] Complete `_format_district_extremes()` in format_stage.py
- [ ] Complete `_format_production_trend()` in format_stage.py
- [ ] Complete `_format_policy_arguments()` in format_stage.py
- [ ] Update `main.py` to use QueryExecutor with async/await
- [ ] Add missing states/crops to sample data
- [ ] Update frontend with 4 new sample prompts
- [ ] Run tests - achieve 100% pass rate
- [ ] Update README with architecture diagram
- [ ] Deploy to Render + Netlify
- [ ] Record Loom video

**Estimated Time:** 2-3 hours

---

## 🎬 Loom Video Talking Points

**Highlight these architectural decisions:**

1. **Event-Driven Architecture** - "Each pipeline stage is completely independent, communicating only through events"
2. **Pub/Sub Pattern** - "Stages subscribe to events they care about and publish events for next stages"
3. **Loose Coupling** - "Adding a new stage means creating a new class that listens to one event and publishes another - no changes to existing stages"
4. **Async Processing** - "The pipeline can run asynchronously, enabling parallel processing in the future"
5. **Comparison to Project 1** - "Original had a monolithic analytics class. This separates parsing, data loading, analysis, and formatting into independent stages."

**Demo:**
- Show event bus publishing "query.received" and trace through the pipeline
- Show event history to demonstrate how data flows through stages
- Execute a query and explain each event: received → parsed → loaded → complete → ready
- Show how easy it is to add a new pipeline stage (e.g., a caching stage or validation stage)

---

## 🆘 Need Help?

**Stuck on implementation?**
- Reference Project 1's `analytics.py` - it has all the logic
- Analysis methods return dictionaries instead of formatted responses
- Formatting methods take dictionaries and create answer text, tables, citations

**Architecture questions?**
- Review `app/event_bus.py` - the core pub/sub system
- Review `app/pipeline/base_stage.py` - the template pattern
- Pattern: Each stage listens → processes → publishes

**Event flow debugging?**
- The event bus keeps history: `event_bus.get_event_history()`
- Add logging to see events flowing through pipeline
- Each event has a timestamp and metadata

**Async/await confusion?**
- The QueryExecutor uses asyncio to wait for the final result
- FastAPI natively supports async endpoints
- Just add `async` to the endpoint and `await` the executor

Good luck! This architecture showcases advanced design patterns. 🚀
