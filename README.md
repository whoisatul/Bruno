# Bruno: RAG-Based Application

> **"Context without Compromise."**

**Bruno** is a **Retrieval-Augmented Generation (RAG)** application designed to answer questions based on a collection of documents. It combines **vector search** and **large language models** to retrieve relevant information and generate contextual responses.

Bruno stores **document embeddings** in a **vector database (Pinecone)** while the actual document content is maintained locally in `data.json` for retrieval during query time.

Developed by **Hrikshesh Kumar** at **IIIT Vadodara**.

---

## Key Features

- **RAG-based Question Answering**  
  Uses semantic search to retrieve relevant document chunks before generating answers.

- **Vector Search with Pinecone**  
  Efficient similarity search over document embeddings.

- **LLM-powered Responses**  
  Uses **LangChain** with **OpenAI (GPT-3.5-Turbo)** to generate contextual answers.

- **Automatic Document Ingestion**  
  Detects and processes text files placed inside the `Dataset/` directory.

- **Modern Interface**  
  Clean chat interface built with **Gradio** for interacting with the system.

---

## Architecture

### 1. Ingestion (`bruno.py`)

- Documents are split using **RecursiveCharacterTextSplitter** to preserve semantic context.
- Text chunks are stored locally in **`data.json`**.
- Embeddings are generated using **OpenAI `text-embedding-3-small`**.
- Embeddings are stored in **Pinecone** for fast vector similarity search.

### 2. Retrieval (`main.py`)

- The user query is converted into an embedding.
- Pinecone performs similarity search to find relevant document chunk IDs.
- Corresponding text is retrieved from **`data.json`**.
- The retrieved context is passed to the **LLM** to generate the final response.

---

## Tech Stack

- **Python**
- **LangChain**
- **OpenAI API**
- **Pinecone**
- **Gradio**

---

## How It Works

1. Add text documents to the `Dataset/` folder.
2. Run the ingestion pipeline to generate embeddings and store them in Pinecone.
3. Start the application.
4. Ask questions through the chat interface.
5. Bruno retrieves relevant document chunks and generates an answer using the LLM.

## 📦 Installation

### Prerequisites
* Python 3.10 or higher
* An [OpenAI API Key](https://platform.openai.com/)
* A [Pinecone API Key](https://app.pinecone.io/) (Serverless)

### 1. Clone the Repository

git clone [https://github.com/yourusername/bruno-rag.git](https://github.com/yourusername/bruno-rag.git)
cd bruno-rag
pip install -r requirements.txt

OPENAI_API_KEY=sk-your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here

`Start the secure interface:`
python main.py

Developed by **Hrikshesh Kumar** at **IIIT Vadodara** **
