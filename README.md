# 📦 RAG-based PDF Chatbot
```
```

Description of the app ...
This document provides comprehensive developer documentation for a Retrieval-Augmented Generation (RAG) based application designed to interact with multiple PDF documents. It covers the project's architecture, core modules, key functionalities, and setup considerations.

## Demo App

[![Streamlit App]([https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chat-with-your-pdfs-sq3lygvnpmlqmit6qf4bk.streamlit.app/)

## Introduction 

In this assignment, I have developed a RAG (Retrieval-Augmented Generation) based chatbot that allows users to interact with multiple PDF documents. The chatbot uses Generative AI (via Groq LLMs) together with a retrieval mechanism (FAISS + embeddings) to provide accurate and context-based answers. The key idea of RAG is to retrieve relevant text chunks from documents and use them to augment the LLM’s responses, ensuring answers are grounded in the uploaded PDFs instead of relying only on the model’s memory.

## Objectives 
* Build a chatbot that can read and understand PDFs.
* Enable question answering directly from uploaded files.
* Support multiple chat sessions with saved history.
* Use FAISS vector store caching to improve efficiency.
* Provide a simple Streamlit UI for interaction.

## System Architecture 
The system follows a modular design for scalability and clarity:
* **Frontend (app.py):** Streamlit web application for uploading PDFs, chatting, and viewing history.
* **RAG Pipeline (rag_pipeline.py):** Core logic that retrieves document chunks and generates answers.
* **Vector Store Manager (vectorstore_manager.py):** Handles PDF text splitting, embeddings, FAISS indexing, and caching.
* **Chat with Groq (chat_groq.py):** Connects the retriever and LLM, maintaining smooth conversation flow.
* **Session Manager (session_manager.py):** Manages multiple user sessions.
* **History Manager (history_manager.py):** Saves and reloads chat history as JSON files.

## Core Features
* **Document Retrieval** : PDFs are preprocessed, split into chunks, and embedded using HuggingFace Sentence Transformers. The FAISS vector store enables fast similarity search for relevant content.
* **Context-Aware Memory** : The chatbot remembers the previous questions and answers in each session. History is stored in JSON files so that sessions can be resumed later.
* **Performance Optimization** : FAISS caching avoids re-indexing the same PDFs multiple times. This reduces latency and improves response speed.
* **Conversational Q&A** : Users can ask natural language questions. The system retrieves relevant PDF context and passes it to Groq LLM (deepseek-r1-distill-llama-70b). Answers are fact-based and include citations from the documents.

## Setup Instructions
* **Clone Repository :** Obtain the project source code.
* **Create a Virtual Environment:** It's highly recommended to use a virtual environment to manage dependencies.
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate or conda create –n chatpdf python
* **Install Dependencies:** Install all required Python packages. You would typically have a requirements.txt file.
pip install -r requirements.txt or pip3 install -r requirements.txt
* **Configure API Keys:** Ensure your Groq API key is set up, you will be prompted to add the groq api key at the time of the login of the application.
* **Run the Streamlit Application:** streamlit run app.py
This opens the chatbot in a web browser (http://localhost:8501).

## Results 
* The chatbot can answer questions from multiple PDFs simultaneously.
* Chat history is saved and reloadable across sessions.
* The bot gives factual, citation-based responses, avoiding hallucinations.
* Latency is reduced due to vector store caching.

## Future Enhancements
* Add support for other document types (Word, TXT, web pages).
* Implement user authentication for private sessions.
* Replace local FAISS with scalable vector databases like Pinecone or ChromaDB.
* Improve UI/UX with better design and interactive features.
* Add download/export of chat sessions in PDF or text formats.

## Conclusion :
This RAG-based chatbot demonstrates the practical use of Generative AI combined with retrieval techniques for real-world tasks like querying documents. It ensures that the model’s responses remain fact-grounded, reliable, and contextually relevant, making it highly useful for research, learning, and professional document analysis. 
