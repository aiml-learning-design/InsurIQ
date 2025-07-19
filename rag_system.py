from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# Prepare RAG system for underwriting guidelines
def setup_rag():
    # Load underwriting guidelines documents
    loader = DirectoryLoader('underwriting_guidelines/', glob="**/*.pdf")
    docs = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Create vector store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)

    return vectorstore.as_retriever()

# Use in agents
guidelines_retriever = setup_rag()

def get_relevant_guidelines(query):
    docs = guidelines_retriever.get_relevant_documents(query)
    return "\n\n".join(doc.page_content for doc in docs)