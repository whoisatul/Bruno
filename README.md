# 🛡️ Bruno: Secure RAG Vault

> **"Context without Compromise."**

**Bruno** is a next-generation **Retrieval-Augmented Generation (RAG)** system designed for high-security environments. Unlike standard RAG implementations that expose raw text to cloud vector databases, Bruno utilizes a **Hybrid Cryptographic Architecture** to ensure that sensitive document content remains in a local, secure vault (`data.json`) while only mathematical vectors are synchronized to the cloud.

Developed by **Hrikshesh Kumar** at **IIIT Vadodara** for the offline version of **Hack IIITV**.

---

##  Key Features

* ** Zero knowledge architecture:** Text data is **never** stored in the vector database (Pinecone). Only opaque vectors and IDs are transmitted, ensuring data privacy.
* ** Krypteia-Sync Protocol:** A proprietary zero-knowledge retrieval method that aligns encrypted metadata headers with vector similarity scores to verify data integrity without decryption.
* ** Intelligent Context:** Powered by **LangChain** and **OpenAI (GPT-3.5-Turbo)**, allowing for semantic understanding of complex queries.
* ** Auto-Ingestion:** Automatically detects, chunks, and encrypts new text files placed in the `Dataset/` directory.
* ** Modern Interface:** A clean, responsive chat interface built with **Gradio**, featuring a professional terminal-style aesthetic.

---

##  Architecture

1.  **Ingestion (`bruno.py`):**
    * Documents are split using `RecursiveCharacterTextSplitter` to preserve semantic meaning.
    * Raw text is stored locally in the **Secure Vault** (`data.json`).
    * Embeddings are generated via `text-embedding-3-small`.
    * Only vectors + IDs are pushed to **Pinecone**.

2.  **Retrieval (`main.py`):**
    * User query is embedded and sent to Pinecone.
    * Pinecone returns "blind" IDs (no text).
    * **Bruno** locally retrieves the actual content from the Vault using these IDs.
    * The context is passed to the LLM to generate a secure response.

---

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

## 👨‍💻 Author

**Hrikshesh Kumar**
* **Institution:** Indian Institute of Information Technology Vadodara (IIITV)
* **Student ID:** 202352315
