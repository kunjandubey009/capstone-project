"""
Tool 2/5: knowledge_base_tool

Stubbed internal-document retrieval. In production, back this with a real
vector store (pgvector, Pinecone, Weaviate, Chroma...) — swap the body of
`_retrieve` and keep the same function signature.
"""
from agents import function_tool

# Toy in-memory "knowledge base" standing in for a real vector index.
_DOCS = [
    {"id": "doc-1", "title": "FY25 Operating Cost Breakdown", "text": "Logistics and warehousing account for 34% of operating costs region-wide."},
    {"id": "doc-2", "title": "Market Entry Playbook", "text": "Prior market entries succeeded fastest when paired with a local distribution partner in year one."},
    {"id": "doc-3", "title": "Customer Retention Study 2025", "text": "Customers churn most in months 2-4 of the lifecycle; proactive outreach in that window cut churn by 18%."},
    {"id": "doc-4", "title": "Compliance Policy Summary", "text": "Any new facility or market entry requires legal and compliance sign-off before public announcement."},
]


def _retrieve(query: str, top_k: int) -> list[dict]:
    query_terms = set(query.lower().split())
    scored = []
    for doc in _DOCS:
        overlap = len(query_terms & set(doc["text"].lower().split()))
        scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]


@function_tool
def knowledge_base_tool(query: str, top_k: int = 2) -> list[dict]:
    """Retrieve the most relevant internal company documents for a query.

    Args:
        query: What to search the internal knowledge base for.
        top_k: How many documents to return.
    """
    return _retrieve(query, top_k)
