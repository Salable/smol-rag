from typing import Optional, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.smol_rag import SmolRag

app = FastAPI(title="Salable Docs RAG API")

smol_rag = SmolRag()


class QueryRequest(BaseModel):
    text: str
    query_type: Optional[str] = "standard"


class QueryResponse(BaseModel):
    result: str


query_map = {
    "standard": smol_rag.query,
    "hybrid_kg": smol_rag.hybrid_kg_query,
    "local_kg": smol_rag.local_kg_query,
    "global_kg": smol_rag.global_kg_query,
    "mix": smol_rag.mix_query,
}


def get_query_function(request: QueryRequest) -> Callable:
    """Validate the query request and return the appropriate query function."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    query_func = query_map.get(request.query_type.lower(), None)

    if not query_func:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query_type: {request.query_type}. Valid types are: {', '.join(query_map.keys())}"
        )

    return query_func


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a query using SmolRag.
    Query types: standard, hybrid_kg, local_kg, global_kg, mix
    """
    try:
        query_func = get_query_function(request)

        result = await query_func(request.text)
        return QueryResponse(result=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
