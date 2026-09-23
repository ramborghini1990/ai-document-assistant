\# 📄 AI Document Assistant (RAG MVP)



An end-to-end, lightweight Retrieval-Augmented Generation (RAG) assistant built from scratch with Python, Streamlit, Google Gemini API, ChromaDB, and SQLite.



This project is a functional MVP developed to demonstrate direct implementation of the core components of modern RAG architectures without relying on high-level orchestration abstractions (such as LangChain or LlamaIndex).



\---



\## 🏗️ Architecture \& Data Flow



The application isolates structured conversational data from vector retrieval:



\[ User Interaction ]

│

▼

\[ Streamlit Web UI ] ── (Store/Retrieve Messages) ──▶ \[ SQLite DB (UUIDv4) ]

│

├──▶ 1. Ingestion Pipeline:

│       PDF ──▶ pypdf (Text + Page Extraction)

│            ──▶ Chunking (1000 chars, 200 overlap + metadata)

│            ──▶ Embeddings (gemini-embedding-001, 3072 dim)

│            ──▶ ChromaDB (Local Persistent Vector Store)

│

└──▶ 2. Retrieval \& Generation Pipeline:

User Query ──▶ Query Embedding

──▶ ChromaDB Cosine Search (top\_k chunks)

──▶ Grounded Prompt Construction

──▶ Gemini API (gemini-3.6-flash)

──▶ Context-Grounded Answer + Source Pages





\---



\## 🚀 Key Features



\* \*\*Direct Pipeline Implementation:\*\* Clear, modular Python code implementing document extraction, text chunking, embedding generation, vector storage, and prompt engineering without framework bloat.

\* \*\*Strict Anti-Hallucination Guardrails:\*\* Prompt engineering strictly binds Gemini responses to retrieved context chunks, instructing the model to declare insufficient information when data is missing.

\* \*\*Source \& Page Attribution:\*\* Preserves page-level metadata from PDFs across chunking and vector storage to display source evidence to the user.

\* \*\*Dual Database Architecture:\*\*

&#x20; \* \*\*ChromaDB:\*\* Local persistent vector storage for semantic embeddings.

&#x20; \* \*\*SQLite:\*\* Relational schema storing users, documents, conversation sessions, and message history using programmatic UUIDv4 primary keys.

\* \*\*Interactive UI:\*\* Built with Streamlit featuring asynchronous file ingestion, chat containers, session management, and context inspection tools.



\---



\## 🛠️ Technology Stack



| Layer | Component | Details |

| :--- | :--- | :--- |

| \*\*Language\*\* | Python 3.12+ | Core application logic |

| \*\*Frontend\*\* | Streamlit | Web UI \& Session State Management |

| \*\*LLM Provider\*\* | Google Gemini API | `gemini-3.6-flash` via official `google-genai` SDK |

| \*\*Embeddings\*\* | Google Gemini API | `gemini-embedding-001` (3072-dimensional vectors) |

| \*\*Vector DB\*\* | ChromaDB | Local persistent vector store with cosine distance |

| \*\*Relational DB\*\*| SQLite3 | Relational persistence (`users`, `documents`, `conversations`, `messages`) |

| \*\*PDF Extraction\*\*| pypdf | Text extraction with page-level mapping |

| \*\*Identifiers\*\* | UUID (v4) | Standard programmatic primary keys |



\---



\## 📁 Repository Structure



```text

ai-document-assistant/

├── app/

│   ├── ai/

│   │   ├── gemini.py          # Gemini API client \& generation logic

│   │   └── prompts.py         # Grounded RAG prompt template builder

│   ├── database/

│   │   └── database.py        # SQLite schema \& conversation history CRUD

│   ├── rag/

│   │   ├── loader.py          # PDF text extraction with page numbers

│   │   ├── chunker.py         # Windowed text chunking with overlap \& UUIDs

│   │   ├── embeddings.py      # Vector embeddings via gemini-embedding-001

│   │   ├── vectorstore.py     # ChromaDB persistence \& collection indexing

│   │   └── retriever.py       # Semantic vector search \& distance ranking

│   ├── ui/

│   │   └── streamlit\_app.py   # Multi-column interactive web interface

│   └── main.py                # Application entrypoint \& path resolution

├── tests/

│   ├── test\_gemini.py         # Standalone LLM integration check

│   ├── test\_embeddings.py     # Embedding dimensions \& batching test

│   ├── test\_chromadb.py       # Vector indexing \& retrieval verification

│   ├── test\_retriever.py      # Semantic similarity search verification

│   ├── test\_database.py       # SQLite CRUD \& schema integrity test

│   └── test\_edge\_cases.py     # Boundary \& error handling tests

├── .env.example               # Secret template

├── .gitignore                 # Artifact and secret exclusion rules

├── INSTRUCTIONS.md            # Master development rules \& acceptance criteria

├── PROJECT\_STATE.md           # Continuous phase-by-phase status tracker

├── requirements.txt           # Minimal pinned dependencies

└── README.md                  # System documentation

⚙️ Installation \& Setup

1\. Prerequisites

Python 3.10+ installed



A valid Google Gemini API Key



2\. Clone and Setup Environment

Bash

git clone \[https://github.com/ramborghini1990/ai-document-assistant.git](https://github.com/ramborghini1990/ai-document-assistant.git)

cd ai-document-assistant



\# Create virtual environment

python -m venv venv



\# Activate virtual environment

\# Windows (CMD):

venv\\Scripts\\activate

\# Linux / macOS:

source venv/bin/activate



\# Install dependencies

pip install --upgrade pip

pip install -r requirements.txt

3\. Configure API Credentials

Create a .env file in the root directory based on .env.example:



Bash

cp .env.example .env

Open .env and insert your Gemini API key:



Code snippet

GEMINI\_API\_KEY=your\_actual\_gemini\_api\_key\_here

🖥️ Running the Application

Launch the Streamlit web application:



Bash

streamlit run app/main.py

Open http://localhost:8501 in your browser.



Upload a PDF: In the left column, upload a text-based PDF. The system will extract pages, split chunks, compute embeddings, and index the vectors.



Chat with Document: In the right column, enter questions regarding the document.



Inspect Context: Expand the evidence inspector below any answer to examine the exact retrieved passages, page numbers, and cosine distance scores.



🧪 Running Automated Tests

Run the standalone verification suites:



Bash

python test\_gemini.py

python test\_embeddings.py

python test\_chromadb.py

python test\_retriever.py

python test\_database.py

python test\_edge\_cases.py

📌 Known Limitations \& Future Improvements (Version 2)

Current MVP Scope: Single-user session isolation, synchronous batch ingestion, and text-based PDF extraction.



Planned Improvements:



Support for scanned PDFs via OCR integration.



Multi-document simultaneous querying and cross-document referencing.



Hybrid search (BM25 lexical + dense vector embeddings) and re-ranking models.



Containerization with Docker and deployment pipelines.

