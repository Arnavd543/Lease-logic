# LeaseLogic Architecture

Technical architecture documentation for the LeaseLogic multi-agent lease analysis system.

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Agent System](#agent-system)
- [RAG Pipeline](#rag-pipeline)
- [State Management](#state-management)
- [Technology Stack](#technology-stack)

## System Overview

LeaseLogic implements a multi-agent Retrieval-Augmented Generation (RAG) system that analyzes residential lease agreements against state tenant protection laws. The system uses LangGraph for agent orchestration, ChromaDB for vector storage, and OpenAI's GPT models for analysis and synthesis.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface                         │
│                  (Streamlit Web App)                      │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ HTTP Request
                       ▼
┌──────────────────────────────────────────────────────────┐
│              Application Layer (app.py)                   │
│  - Session Management                                     │
│  - File Upload Handling                                   │
│  - State Selection                                        │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ invoke()
                       ▼
┌──────────────────────────────────────────────────────────┐
│          LangGraph Supervisor (supervisor.py)             │
│  - State Machine Orchestration                            │
│  - Conditional Routing Logic                              │
│  - Agent Coordination                                     │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ State Object
                       ▼
┌──────────────────────────────────────────────────────────┐
│                   Agent Layer                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Classifier → Lease → Law → Verifier → Synthesizer│   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Lease RAG  │ │   Law RAG   │ │  OpenAI API │
│  (ChromaDB) │ │  (ChromaDB) │ │  (GPT-4o)   │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Component Architecture

### 1. User Interface Layer

**File**: `app.py`

**Responsibilities**:
- Render Streamlit web interface
- Handle PDF file uploads
- Manage user session state
- Display query results and metadata
- Show classification reasoning and scope

**Key Components**:
```python
# Session state management
st.session_state.lease_uploaded
st.session_state.collection_name
st.session_state.chat_history

# PDF upload and processing
uploaded_file = st.file_uploader("Upload Lease", type=['pdf'])
processor = LeaseDocumentProcessor()
chunks = processor.process_lease_pdf(file_path)

# Analysis invocation
result = run_analysis(
    user_query=question,
    lease_collection_name=collection_name,
    state_location=state
)
```

### 2. Orchestration Layer

**File**: `src/agents/supervisor.py`

**Responsibilities**:
- Build LangGraph state machine
- Define agent node connections
- Implement conditional routing logic
- Enforce maximum iteration limits (3)

**Graph Structure**:
```python
graph = StateGraph(LeaseAnalysisState)

# Add nodes
graph.add_node("classifier", classifier_node)
graph.add_node("lease_agent", lease_agent_node)
graph.add_node("law_agent", law_agent_node)
graph.add_node("verifier", verifier_agent_node)
graph.add_node("synthesizer", synthesis_agent_node)

# Conditional routing
graph.add_conditional_edges(
    "classifier",
    route_after_classifier,  # Routes based on query_scope
    {
        "lease_agent": "lease_agent",
        "law_agent": "law_agent"
    }
)
```

**Routing Decision Functions**:

1. **route_after_classifier()**
   - Input: query_scope from classifier
   - Output: "lease_agent" | "law_agent"
   - Logic: Determine initial agent based on query intent

2. **route_after_lease()**
   - Input: query_scope from state
   - Output: "law_agent" | "verifier"
   - Logic: Skip law search if lease_only

3. **should_requery()**
   - Input: retrieval_quality_grade, needs_requery, requery_count
   - Output: "requery" | "synthesize"
   - Logic: Loop back if quality < 7 and iterations < 3

### 3. Agent Layer

**Files**: `src/agents/*.py`

#### Classifier Agent

**File**: `classifier_agent.py`

**Purpose**: Analyze query intent and classify as lease_only, law_only, or both

**Input**:
```python
{
    "user_query": "Is my $300 late fee legal?"
}
```

**Output**:
```python
{
    "query_scope": "both",
    "classification_reasoning": "Question requires comparing lease terms to legal requirements"
}
```

**Implementation**:
```python
def classifier_node(state: LeaseAnalysisState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_template(CLASSIFIER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({"query": state["user_query"]})
    result = json.loads(response.content)

    return {
        "query_scope": result["category"],
        "classification_reasoning": result["reasoning"]
    }
```

#### Lease Agent

**File**: `lease_agent.py`

**Purpose**: Search and analyze user's lease document

**Process**:
1. Initialize LeaseRAG with collection name
2. Run corrective RAG (max 3 iterations)
3. Extract retrieval score and findings
4. Return analysis to state

**Output**:
```python
{
    "lease_context": [documents],
    "lease_finding": "Analysis text",
    "lease_retrieval_score": 8.5
}
```

#### Law Agent

**File**: `law_agent.py`

**Purpose**: Search and analyze state/federal tenant protection laws

**Process**:
1. Initialize LawRAG with state location
2. Run corrective RAG (max 3 iterations)
3. Distinguish federal vs state laws
4. Return legal analysis to state

**Output**:
```python
{
    "law_context": [documents],
    "law_finding": "Legal analysis text",
    "law_retrieval_score": 9.0
}
```

#### Verifier Agent

**File**: `verifier_agent.py`

**Purpose**: Grade retrieval quality and determine if requery needed

**Scope-Aware Grading**:
```python
# Only grade documents that were actually searched
scope = state.get("query_scope", "both")

combined_docs = []
if scope in ["lease_only", "both"] and state.get("lease_context"):
    combined_docs.extend(state["lease_context"])

if scope in ["law_only", "both"] and state.get("law_context"):
    combined_docs.extend(state["law_context"])

# Grade combined documents
grade_result = grader.grade(query, combined_docs)
```

**Output**:
```python
{
    "retrieval_quality_grade": 7,
    "needs_requery": False,
    "requery_reasoning": "Documents directly answer question",
    "requery_count": current_count + 1
}
```

#### Synthesizer Agent

**File**: `synthesis_agent.py`

**Purpose**: Generate final answer using scope-aware prompts

**Scope-Aware Synthesis**:
```python
scope = state.get("query_scope", "both")

if scope == "lease_only":
    prompt = SYNTHESIS_LEASE_ONLY_PROMPT
elif scope == "law_only":
    prompt = SYNTHESIS_LAW_ONLY_PROMPT
else:
    prompt = SYNTHESIS_COMPARISON_PROMPT

# Generate answer
response = llm.invoke(prompt.format(...))
```

**Output**:
```python
{
    "final_answer": "Synthesized analysis",
    "confidence": "HIGH"  # Based on quality grade
}
```

### 4. RAG Layer

**Files**: `src/chains/*.py`

#### Base RAG Chains

**File**: `rag_chain.py`

**LeaseRAG Class**:
```python
class LeaseRAG:
    def __init__(self, collection_name: str):
        self.vectorstore = Chroma(
            collection_name=collection_name,
            persist_directory="data/vector_stores"
        )
        self.llm = ChatOpenAI(model="gpt-4o-mini")

    def run(self, query: str) -> dict:
        # Retrieve documents
        docs = self.vectorstore.similarity_search_with_score(query, k=5)

        # Analyze with LLM
        analysis = self.analyze(query, docs)

        return {
            "retrieved_docs": docs,
            "analysis": analysis,
            "retrieval_score": avg_score
        }
```

**LawRAG Class**: Similar structure, searches law corpus

#### Corrective RAG

**File**: `corrective_rag.py`

**Key Components**:

1. **RetrievalGrader**
   - Grades retrieval quality (0-10 scale)
   - Returns grade, reasoning, needs_requery flag

2. **QueryRefiner**
   - Iteration 1: Add legal keywords
   - Iteration 2: Simplify to core concept
   - Iteration 3+: LLM-based reformulation

3. **CorrectiveRAG Class**
   - Wraps base RAG chain
   - Implements iterative refinement loop
   - Tracks best result across iterations

**Corrective Loop**:
```python
while iteration < max_iterations:
    # Retrieve
    result = base_rag.run(current_query)

    # Grade
    grade = grader.grade(original_query, result['docs'])

    if grade >= threshold:
        return result  # Quality sufficient

    # Refine and retry
    current_query = refiner.refine(original_query, grade['reasoning'], iteration)
    iteration += 1

return best_result
```

### 5. Data Layer

#### Vector Stores

**Location**: `data/vector_stores/`

**Structure**:
```
vector_stores/
├── chroma_law_california/    # California tenant laws
├── chroma_law_newyork/       # New York tenant laws
├── test_lease_phase1/        # Test lease documents
└── user_lease_*/             # User-uploaded leases
```

**Initialization**:
```python
# Law vectorstore
vsm = VectorStoreManager()
vsm.create_law_vectorstore("california")

# Lease vectorstore
chunks = processor.process_lease_pdf("lease.pdf")
vsm.create_lease_vectorstore(chunks, "collection_name")
```

#### Document Processing

**File**: `src/tools/pdf_processor.py`

**Pipeline**:
```
PDF File
  ↓
PyPDF2 Text Extraction
  ↓
Section Detection (heuristic)
  ↓
Semantic Chunking (500 chars, 50 overlap)
  ↓
Metadata Assignment (section, page)
  ↓
Chunk List
```

**Chunking Strategy**:
```python
chunks = []
for section in sections:
    text = section['text']
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append({
            'text': chunk,
            'metadata': {
                'section': section['title'],
                'chunk_index': i
            }
        })
```

## Data Flow

### Query Processing Flow

```
1. User submits query
   ↓
2. Streamlit captures input
   ↓
3. Supervisor invokes graph with initial state
   ↓
4. Classifier analyzes query intent
   ↓
5a. Route to Lease Agent (if lease_only or both)
   ↓
   LeaseRAG retrieves and analyzes
   ↓
5b. Route to Law Agent (if law_only or both)
   ↓
   LawRAG retrieves and analyzes
   ↓
6. Verifier grades combined retrieval
   ↓
7a. If quality < 7: Loop back to step 5
   ↓
7b. If quality >= 7 or max iterations: Continue
   ↓
8. Synthesizer generates final answer
   ↓
9. Return result to Streamlit
   ↓
10. Display answer with metadata
```

### State Object Evolution

**Initial State**:
```python
{
    "user_query": "Is my $300 late fee legal?",
    "current_query": "Is my $300 late fee legal?",
    "lease_collection_name": "user_lease_sample",
    "state_location": "california",
    "requery_count": 0
}
```

**After Classifier**:
```python
{
    ...previous fields,
    "query_scope": "both",
    "classification_reasoning": "Requires comparing lease vs law"
}
```

**After Lease Agent**:
```python
{
    ...previous fields,
    "lease_context": [Document(text="Late fee: $300", metadata={...})],
    "lease_finding": "Lease specifies $300 late fee...",
    "lease_retrieval_score": 8.5
}
```

**After Law Agent**:
```python
{
    ...previous fields,
    "law_context": [Document(text="Late fees must be reasonable...", metadata={...})],
    "law_finding": "California law requires reasonableness...",
    "law_retrieval_score": 9.0
}
```

**After Verifier**:
```python
{
    ...previous fields,
    "retrieval_quality_grade": 8,
    "needs_requery": False,
    "requery_reasoning": "Both sources provide specific information",
    "requery_count": 1
}
```

**Final State (After Synthesizer)**:
```python
{
    ...all previous fields,
    "final_answer": "Your lease allows a $300 late fee, however...",
    "confidence": "HIGH"
}
```

## State Management

### LeaseAnalysisState TypedDict

**File**: `src/utils/state.py`

```python
class LeaseAnalysisState(TypedDict):
    # Input fields
    user_query: str
    current_query: str
    state_location: str
    lease_collection_name: str

    # Classifier outputs
    query_scope: Optional[str]
    classification_reasoning: Optional[str]

    # Lease agent outputs
    lease_context: Optional[List[Any]]
    lease_finding: Optional[str]
    lease_retrieval_score: Optional[float]

    # Law agent outputs
    law_context: Optional[List[Any]]
    law_finding: Optional[str]
    law_retrieval_score: Optional[float]

    # Verifier outputs
    retrieval_quality_grade: Optional[float]
    needs_requery: Optional[bool]
    requery_count: Optional[int]
    requery_reasoning: Optional[str]

    # Synthesizer outputs
    final_answer: Optional[str]
    confidence: Optional[str]

    # Metadata
    messages: Optional[List[str]]
    agent_logs: Optional[Dict[str, Any]]
```

### State Update Mechanism

LangGraph merges node return values into state:

```python
def agent_node(state: LeaseAnalysisState) -> dict:
    # Process state
    result = process(state)

    # Return only updated fields
    return {
        "field_to_update": new_value,
        "another_field": another_value
    }
    # LangGraph automatically merges these into the state
```

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | LangGraph | Multi-agent state machine |
| LLM Framework | LangChain | RAG chains and prompts |
| Language Models | OpenAI GPT-4o, GPT-4o-mini | Analysis and synthesis |
| Embeddings | OpenAI text-embedding-3-small | Document vectorization |
| Vector Database | ChromaDB | Similarity search |
| Web Framework | Streamlit | User interface |
| PDF Processing | PyPDF2 | Text extraction |
| Configuration | YAML | System settings |

### Python Dependencies

**Key Libraries**:
```
langchain>=0.1.0
langgraph>=0.0.1
langchain-openai>=0.0.1
langchain-community>=0.0.1
chromadb>=0.4.0
streamlit>=1.28.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
```

### External Services

- **OpenAI API**: LLM inference and embeddings
- **LangSmith** (Optional): Tracing and evaluation
- **Streamlit Cloud** (Optional): Hosting platform

## Performance Characteristics

### Latency

| Query Type | Avg Response Time | Components |
|-----------|-------------------|------------|
| Lease-only | 10-15s | Classifier + Lease + Verifier + Synthesis |
| Law-only | 10-15s | Classifier + Law + Verifier + Synthesis |
| Comparison | 15-25s | Classifier + Lease + Law + Verifier + Synthesis |

### Throughput

- **Sequential processing**: One query at a time per session
- **Concurrent sessions**: Limited by Streamlit (single-threaded)
- **Scalability**: Horizontal scaling via multiple instances

### Resource Usage

- **Memory**: ~500MB base + ~100MB per loaded vectorstore
- **CPU**: Minimal (I/O bound, API calls)
- **Storage**: ~10MB per 100-page lease document (vectorized)

## Security Considerations

### Data Privacy

- User-uploaded leases stored in session-specific collections
- Collections can be deleted after session
- No persistent storage of user queries without consent

### API Key Management

- Never commit keys to version control
- Use environment variables or secret management
- Rotate keys periodically

### Input Validation

- PDF file type validation
- File size limits (configurable)
- Query sanitization before LLM processing

## Extensibility

### Adding New States

1. Create law corpus: `data/laws/{state}_laws.txt`
2. Run vectorstore builder
3. Update state dropdown in UI
4. No code changes required

### Custom Agents

```python
# Add new agent to supervisor.py
graph.add_node("custom_agent", custom_agent_node)
graph.add_edge("verifier", "custom_agent")
```

### Alternative LLMs

```python
# Replace in config.yaml
models:
  smart_model: "anthropic/claude-3-opus"
  fast_model: "anthropic/claude-3-haiku"
```

## Future Enhancements

### Planned Improvements

1. **Asynchronous Processing**: Parallelize lease and law searches
2. **Caching Layer**: Redis cache for repeated queries
3. **Advanced Chunking**: Semantic chunking based on content
4. **Multi-Modal**: Support images and tables in leases
5. **Feedback Loop**: Use user feedback to improve classification
6. **Production DB**: Migrate from ChromaDB to Pinecone/Weaviate

### Architecture Evolution

```
Current: Single-tenant, session-based
  ↓
Phase 2: Multi-tenant with user accounts
  ↓
Phase 3: Microservices (separate PDF, RAG, LLM services)
  ↓
Phase 4: Event-driven with message queues
```

## References

- [LangChain Documentation](https://docs.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
