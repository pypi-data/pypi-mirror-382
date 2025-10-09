"""
Quick start example for Verbatim RAG.
"""

from verbatim_rag import VerbatimRAG, VerbatimIndex
from verbatim_rag.ingestion import DocumentProcessor


def main():
    # Step 1: Process documents
    print("📄 Processing documents...")
    processor = DocumentProcessor()

    # Process a PDF from URL
    try:
        documents = [
            processor.process_url(
                url="https://aclanthology.org/2025.bionlp-share.8.pdf",
                title="KR Labs at ArchEHR-QA 2025: A Verbatim Approach for Evidence-Based Question Answering",
                authors=["Adam Kovacs", "Paul Schmitt", "Gabor Recski"],
            )
        ]
        print(f"✅ Processed {len(documents)} documents")
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        print("💡 Install with: pip install 'verbatim-rag[document-processing]'")
        return

    # Step 2: Create RAG system
    print("\n🔍 Creating RAG system...")
    index = VerbatimIndex(
        dense_model=None, sparse_model="naver/splade-v3", db_path="./index.db"
    )
    index.add_documents(documents)

    rag = VerbatimRAG(index)

    # Step 3: Ask questions
    print("\n❓ Asking questions...")

    questions = [
        "What are the main findings?",
        "What dataset was used?",
        "What is the methodology?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        response = rag.query(question)
        print(f"A: {response.answer[:150]}...")
        print(
            f"📚 {len(response.structured_answer.citations)} citations from {len(response.documents)} documents"
        )


if __name__ == "__main__":
    main()
