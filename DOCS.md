# SmolRAG Docs

This document provides essential information for developers working with the SmolRAG project.

## Build/Configuration Instructions

### Environment Setup

1. **Python Environment**:
   - Python 3.10+ is recommended
   - Create a virtual environment: `python -m venv .venv`
   - Activate the virtual environment:
     - Windows: `.venv\Scripts\activate`
     - macOS/Linux: `source .venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

2. **Environment Variables**:
   - Create a `.env` file in the project root with the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```
   - The application uses OpenAI's API for embeddings and completions, so a valid API key is required

3. **Directory Structure**:
   - The application expects certain directories to exist:
     - `app/data`: Stores vector databases, knowledge graph, and key-value stores
     - `app/cache`: Stores query and embedding caches
     - `app/logs`: Stores log files
     - `app/input_docs`: Place documents here to be ingested by the system

4. **Docker Support**:
   - The project includes a Dockerfile for containerized deployment
   - Build the container: `docker build -t smol-rag .`
   - Run the container: `docker run -p 8000:8000 --env-file .env smol-rag`

## Testing Information

### Running Tests

1. **Evaluation Tests**:
   - The system includes a test evaluation framework in `app/evaluation/`
   - Run evaluation on test set: `python app/evaluation/evaluate_test_set.py`
   - This evaluates the system's responses against a predefined test set

### Creating Tests

1. **Generate Test Set**:
   - Use `app/evaluation/generate_test_set.py` to create a test set from documents
   - This extracts pull quotes from documents and generates queries and expected responses
   - Run with: `python app/evaluation/generate_test_set.py`

2. **Evaluate Test Set**:
   - Use `app/evaluation/evaluate_test_set.py` to run evaluation on the test set.
   - The script generates responses, compares them against expected pull quotes, and computes an accuracy score.
   - Execute with: `python app/evaluation/evaluate_test_set.py`

3. **Test Example**:
   ```python
   # Import required modules
   from app.smol_rag import SmolRag
   
   # Initialize test components
   rag = SmolRag()
   
   # Run test operation
   result = rag.query("Test query")
   
   # Verify results
   assert result is not None, "Query should return a response"
   print("Test passed!")
   ```

## Development Information

### Code Organization

1. **Core Components**:
   - `smol_rag.py`: Main RAG implementation
   - `openai_llm.py`: OpenAI API integration
   - `vector_store.py`: Vector database implementation
   - `graph_store.py`: Knowledge graph implementation
   - `kv_store.py`: Key-value store implementation
   - `chunking.py`: Document chunking utilities
   - `prompts.py`: System prompts for various operations
   - `utilities.py`: General utility functions

2. **API Layer**:
   - `api/main.py`: FastAPI implementation exposing the RAG functionality

### Query Types

The system supports multiple query types, each optimized for different use cases:

1. **Vector Search Query** (`query`): Uses pure semantic similarity
2. **Local Knowledge Graph Query** (`local_kg_query`): Focuses on low-level keywords
3. **Global Knowledge Graph Query** (`global_kg_query`): Focuses on high-level keywords
4. **Hybrid Knowledge Graph Query** (`hybrid_kg_query`): Combines local and global approaches
5. **Mix Query** (`mix_query`): Most comprehensive, combines vector search and KG reasoning

### Document Ingestion

Documents are processed through several steps:
1. Documents are split into overlapping chunks (~2000 characters)
2. Each chunk is summarized
3. Chunks and summaries are embedded using OpenAI's embedding API
4. Entities and relationships are extracted and stored in a knowledge graph
5. All data is indexed for retrieval

### Debugging Tips

1. **Logging**:
   - The application uses Python's logging module
   - Logs are stored in `app/logs/`
   - The main log file is `main.log`

2. **Caching**:
   - Query and embedding results are cached to improve performance and reduce API costs
   - Clear caches in `app/cache/` if you need to force recomputation

3. **API Testing**:
   - Use the `requests.http` file to test API endpoints
   - The API exposes a single endpoint at `/query` that accepts POST requests