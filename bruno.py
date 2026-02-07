import os
import json
import logging
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Configuration & Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Bruno-Core")

# Initialize Clients
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

INDEX_NAME = "bruno-vault-index"
# UPDATED: File is now 'data.json' in the same directory
MAPPING_FILE = "data.json"

# Ensure Data File exists
if not os.path.exists(MAPPING_FILE):
    logger.info(f"{MAPPING_FILE} not found. Creating a new empty vault.")
    with open(MAPPING_FILE, "w") as f:
        json.dump({}, f)

def initialize_vector_db():
    """Creates the Pinecone index if it doesn't exist."""
    existing_indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        logger.info(f"Creating new index: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    else:
        logger.info(f"Index {INDEX_NAME} already exists.")

# 2. Ingestion Engine
def ingest_document(file_name, text_content, chunk_size=1000, chunk_overlap=200):
    """
    Splits text, updates local 'data.json', and pushes ONLY vectors to Pinecone.
    """
    logger.info(f"Processing file: {file_name}")
    
    # A. Intelligent Chunking (LangChain)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_text(text_content)
    
    # B. Update Local Vault (data.json)
    try:
        with open(MAPPING_FILE, "r") as f:
            vault_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        vault_data = {}

    vectors_to_upsert = []
    
    # C. Embed & Prepare
    vectors = embeddings.embed_documents(chunks)
    
    base_id = file_name.lower().replace(".", "_").replace(" ", "_")
    
    for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
        chunk_id = f"{base_id}_chunk_{i}"
        
        # 1. Store TEXT in local data.json
        vault_data[chunk_id] = chunk_text
        
        # 2. Store VECTOR in Pinecone
        vectors_to_upsert.append({
            "id": chunk_id,
            "values": vector,
            "metadata": {
                "source": file_name,
                "chunk_index": i,
                "project": "Bruno"
            }
        })

    # Save Vault
    with open(MAPPING_FILE, "w") as f:
        json.dump(vault_data, f, indent=4)
    
    # D. Push to Pinecone
    index = pc.Index(INDEX_NAME)
    index.upsert(vectors=vectors_to_upsert)
    logger.info(f"Successfully ingested {len(chunks)} chunks for {file_name}.")

# 3. Retrieval Engine
def query_bruno(prompt, k=3):
    """
    1. Search Pinecone for vectors.
    2. Retrieve actual text from 'data.json' using IDs.
    3. Generate answer using LangChain.
    """
    index = pc.Index(INDEX_NAME)
    
    # A. Semantic Search
    query_embedding = embeddings.embed_query(prompt)
    search_results = index.query(vector=query_embedding, top_k=k, include_metadata=True)
    
    # B. Fetch Content from data.json
    with open(MAPPING_FILE, "r") as f:
        vault_data = json.load(f)
        
    retrieved_docs = []
    for match in search_results['matches']:
        chunk_id = match['id']
        if chunk_id in vault_data:
            retrieved_docs.append(vault_data[chunk_id])
        else:
            logger.warning(f"Chunk ID {chunk_id} found in Pinecone but missing in data.json!")

    if not retrieved_docs:
        return "I couldn't find any relevant documents in the Bruno vault."

    context_text = "\n\n".join(retrieved_docs)

    # C. Generation with LangChain
    system_prompt = """You are Bruno, a specialized RAG-enhanced AI assistant developed by Hrikshesh Kumar at IIIT Vadodara.
    
    Your Architecture:
    - You use Hybrid Cryptography: The user's documents are stored in a local secure vault (data.json).
    - You use Vector Search: You retrieve context based on semantic similarity.
    - You possess knowledge of 'Krypteia-Sync', a proprietary zero-knowledge retrieval protocol.

    Instructions:
    - Answer the question strictly based on the provided Context.
    - If the context mentions 'Krypteia-Sync' or specific project details, explain them clearly.
    - Maintain a professional, academic, yet helpful tone suitable for a research assistant.
    
    Context:
    {context}
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{question}")
    ])

    chain = prompt_template | llm | StrOutputParser()

    response = chain.invoke({
        "context": context_text,
        "question": prompt
    })
    
    return response

# Initialize on import
initialize_vector_db()