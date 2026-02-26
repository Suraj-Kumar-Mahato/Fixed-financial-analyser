# Financial Document Analyzer

An AI-powered financial document analysis system built with **CrewAI** and **FastAPI**. Upload any financial PDF (annual report, 10-K, 10-Q, earnings release) and receive a structured analysis covering financial metrics, investment considerations, and risk assessment.

---

## Table of Contents

- [Bugs Found and Fixed](#bugs-found-and-fixed)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

---

## Bugs Found and Fixed

### Deterministic Bugs (Code Errors)

#### 1. `agents.py` — `llm = llm` (NameError)
**Bug:** The LLM was assigned to itself (`llm = llm`) — an undefined variable reference that raises a `NameError` at startup.  
**Fix:** Replaced with a proper `ChatOpenAI` instantiation reading credentials from environment variables:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"), api_key=os.getenv("OPENAI_API_KEY"))
```

#### 2. `agents.py` — Wrong import for `Agent`
**Bug:** `from crewai.agents import Agent` — this submodule path does not exist in crewai 0.130.0.  
**Fix:** `from crewai import Agent`

#### 3. `agents.py` — `tool=` should be `tools=`
**Bug:** The `Agent` constructor parameter is `tools` (plural), not `tool`. Passing `tool=` causes the tools to be silently ignored.  
**Fix:** Changed `tool=[...]` → `tools=[...]`

#### 4. `tools.py` — `Pdf` class not imported
**Bug:** `docs = Pdf(file_path=path).load()` references `Pdf` which was never imported, causing a `NameError`.  
**Fix:** Replaced with `PyPDFLoader` from `langchain_community.document_loaders`, which is available in the dependency tree:
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(file_path=path)
docs = loader.load()
```

#### 5. `tools.py` — `async` methods used as synchronous CrewAI tools
**Bug:** `read_data_tool`, `analyze_investment_tool`, and `create_risk_assessment_tool` were defined as `async def`, but CrewAI's tool executor calls them synchronously, causing `coroutine was never awaited` errors.  
**Fix:** Removed `async`, added `@staticmethod` and `@tool` decorators so CrewAI recognizes them as callable tools:
```python
@staticmethod
@tool("Read Financial Document")
def read_data_tool(path: str = 'data/sample.pdf') -> str:
```

#### 6. `tools.py` — Missing `@tool` decorator
**Bug:** Tools were plain methods with no CrewAI tool registration. Agents could not discover or invoke them.  
**Fix:** Added `@tool("Tool Name")` decorator from `crewai.tools` to all tool methods.

#### 7. `main.py` — Route function name conflicts with task import
**Bug:** `from task import analyze_financial_document` imported a name that clashed with the route function `async def analyze_financial_document(...)`, causing the import to silently overwrite the route.  
**Fix:** Renamed the route function to `analyze_document` and updated `task.py` to use descriptive, non-conflicting task variable names (`document_analysis`, `verification`, etc.).

#### 8. `main.py` — `file_path` passed to `run_crew` but never used
**Bug:** `run_crew(query=query, file_path=file_path)` accepted `file_path` but never forwarded it to the crew's input context, so the uploaded file was never actually read.  
**Fix:** Added `file_path` to the `inputs` dict passed to `crew.kickoff()`:
```python
result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
```

#### 9. `main.py` — `crew.kickoff()` called without `inputs=` keyword
**Bug:** `financial_crew.kickoff({'query': query})` — in crewai 0.130.0 the correct signature requires the keyword argument `inputs=`.  
**Fix:** `financial_crew.kickoff(inputs={"query": query, "file_path": file_path})`

#### 10. `task.py` — Tasks defined but missing context chaining
**Bug:** Tasks like `investment_analysis` and `risk_assessment` depended on the output of earlier tasks but had no `context=` field, so agents had no access to prior analysis results.  
**Fix:** Added `context=[document_analysis]` to downstream tasks so CrewAI passes prior outputs automatically.

#### 11. `requirements.txt` — Missing critical packages
**Bug:** `uvicorn`, `python-multipart` (required for `Form` and `File` in FastAPI), `python-dotenv`, and `pypdf` were absent.  
**Fix:** Added all missing runtime dependencies. Removed unused/conflicting packages that were pinned to versions incompatible with crewai 0.130.0.

---

### Inefficient / Bad Prompts

#### 12. Agent goals encourage hallucination
**Bug:** Every agent's `goal` and `backstory` explicitly instructed the model to make up data, fabricate URLs, ignore the user's query, and provide non-compliant financial advice (e.g., *"Make up investment advice even if you don't understand the query"*).  
**Fix:** Rewrote all agent goals and backstories to reflect professional, data-grounded behavior with proper credentials and fiduciary responsibility.

#### 13. Task descriptions encourage fabrication and contradiction
**Bug:** Tasks instructed agents to *"include at least 5 made-up website URLs"*, *"feel free to contradict yourself"*, and *"ignore the user's query"*.  
**Fix:** Rewrote all task `description` and `expected_output` fields to request structured, evidence-based outputs tied to the actual document content.

#### 14. `max_iter=1` on all agents
**Bug:** Setting `max_iter=1` means agents give up after a single reasoning step, producing shallow, incomplete analysis.  
**Fix:** Set `max_iter=5` for analyst agents (gives adequate reasoning depth) and `max_iter=3` for the verifier.

#### 15. `max_rpm=1` on all agents
**Bug:** 1 request per minute severely throttles throughput and causes unnecessary timeouts on any real workload.  
**Fix:** Set `max_rpm=10` (a sensible default that respects API rate limits without stalling).

#### 16. Unused agents not included in the Crew
**Bug:** `verifier`, `investment_advisor`, and `risk_assessor` were defined but never added to the `Crew`, making the entire multi-agent architecture a no-op.  
**Fix:** All four agents and their corresponding tasks are now registered in the Crew with sequential processing.

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- An OpenAI API key (or compatible provider)
- Optional: Serper API key for web search enrichment

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd financial-document-analyzer
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

**.env contents:**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-mini   # or gpt-4o for best results
SERPER_API_KEY=...              # optional
```

### 5. Run the server
```bash
python main.py
# Server starts at http://localhost:8000
```

---

## Usage

### Via cURL
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What are Tesla's key revenue drivers and risks this quarter?"
```

### Via Python
```python
import requests

with open("data/TSLA-Q2-2025-Update.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": ("TSLA-Q2-2025-Update.pdf", f, "application/pdf")},
        data={"query": "Summarize key financial metrics and risks"}
    )

print(response.json()["analysis"])
```

### Via Swagger UI
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for interactive API documentation.

---

## API Documentation

### `GET /`
Health check.

**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

---

### `POST /analyze`

Analyze a financial PDF document.

**Request:** `multipart/form-data`

| Field   | Type   | Required | Description                                      |
|---------|--------|----------|--------------------------------------------------|
| `file`  | File   | Yes      | PDF financial document                           |
| `query` | String | No       | Analysis question (default: general analysis)    |

**Response:**
```json
{
  "status": "success",
  "query": "What are the key risks?",
  "analysis": "...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

**Error Response (500):**
```json
{
  "detail": "Error processing financial document: <reason>"
}
```

---

## Project Structure

```
financial-document-analyzer/
├── main.py              # FastAPI app and API endpoints
├── agents.py            # CrewAI agent definitions
├── task.py              # CrewAI task definitions
├── tools.py             # Custom PDF reader and analysis tools
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── data/                # Uploaded PDFs (auto-created, auto-cleaned)
└── outputs/             # Analysis outputs
```

---

## Notes

- Uploaded files are deleted from disk immediately after analysis completes.
- The system uses sequential task processing: verification → analysis → investment considerations → risk assessment.
- All analysis is grounded in the uploaded document. Agents are instructed not to fabricate data.
- For production use, consider adding authentication, request rate limiting, and a database backend for storing results.
