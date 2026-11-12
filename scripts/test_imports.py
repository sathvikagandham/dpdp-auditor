def test_imports():
    print("Testing imports...")
    try:
        import fitz
        print("✅ PyMuPDF imported")
    except ImportError as e:
        print(f"❌ PyMuPDF failed: {e}")
    try:
        import chromadb
        print("✅ ChromaDB imported")
    except ImportError as e:
        print(f"❌ ChromaDB failed: {e}")
    try:
        import sentence_transformers
        print("✅ SentenceTransformers imported")
    except ImportError as e:
        print(f"❌ SentenceTransformers failed: {e}")
    try:
        from langgraph.graph import StateGraph
        print("✅ LangGraph imported")
    except ImportError as e:
        print(f"❌ LangGraph failed: {e}")
if __name__=="__main__":
    test_imports()
        