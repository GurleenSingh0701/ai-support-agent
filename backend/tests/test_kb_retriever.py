import pytest
from knowledgebase.KB_retriever import KBRetriever, kb_retriever

def test_kb_retriever_default_instance():
    assert kb_retriever is not None
    assert isinstance(kb_retriever, KBRetriever)

def test_kb_retriever_search_fallback():
    retriever = KBRetriever()
    results = retriever.search("xyznonexistentword12345")
    
    assert len(results) > 0
    assert "Returns accepted within 30 days" in results[0]

def test_kb_retriever_search_keyword_match():
    retriever = KBRetriever()
    results = retriever.search("returns policy")
    
    assert len(results) > 0
    assert any("returns" in snippet.lower() or "policy" in snippet.lower() for snippet in results)
