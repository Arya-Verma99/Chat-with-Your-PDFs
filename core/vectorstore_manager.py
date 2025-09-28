import os
import tempfile
import hashlib
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document

from langchain_groq import ChatGroq  # ✅ LLM for question suggestion


class PDFVectorStoreManager:
    def __init__(
        self,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        cache_dir: str = "faiss_cache",
        groq_api_key: str = None
    ):
        self.embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        # Content & questions will be extracted after PDF upload
        self.full_text = ""
        # self.suggested_questions = []
        self.groq_api_key = groq_api_key

    def _hash_file_names(self, files: List) -> str:
        names = "".join(sorted([f.name for f in files]))
        return hashlib.md5(names.encode()).hexdigest()

    def _load_and_split_pdfs(self, uploaded_files: List) -> List[Document]:
        all_docs = []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        for file in uploaded_files:
            original_filename = file.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            os.remove(tmp_path)
            for doc in docs:
                doc.metadata["source"] = original_filename
            all_docs.extend(docs)
            print(original_filename)
            print(all_docs[0].metadata)

        split_docs = splitter.split_documents(all_docs)

        self.full_text = "\n".join([doc.page_content for doc in split_docs])

        return split_docs

    def _get_index_path(self, file_hash: str) -> str:
        return os.path.join(self.cache_dir, file_hash)

    def create_or_load_vectorstore(self, uploaded_files: List) -> VectorStoreRetriever:
        file_hash = self._hash_file_names(uploaded_files)
        index_path = self._get_index_path(file_hash)

        if os.path.exists(index_path):
            print(f"📁 Loading cached FAISS index from: {index_path}")
            vectordb = FAISS.load_local(
                folder_path=index_path,
                embeddings=self.embedder,
                allow_dangerous_deserialization=True,
            )

            # ✅ ALSO: load docs again for question suggestion
            print("📄 Extracting text from PDF for question suggestions...")
            doc_chunks = self._load_and_split_pdfs(uploaded_files)
            # self.suggested_questions = self._generate_question_suggestions(self.full_text)

        else:
            print(f"📄 Creating new FAISS index at: {index_path}")
            doc_chunks = self._load_and_split_pdfs(uploaded_files)
            vectordb = FAISS.from_documents(doc_chunks, self.embedder)
            vectordb.save_local(folder_path=index_path)
            # self.suggested_questions = self._generate_question_suggestions(self.full_text)

        return vectordb.as_retriever(search_kwargs={"k": 4})

    # def _generate_question_suggestions(self, text: str, n: int = 5, max_chars: int = 2000) -> List[str]:
    #     if not text:
    #         return []

    #     if len(text) > max_chars:
    #         text = text[:max_chars] + "..."

    #     prompt = (
    #         f"You're an AI assistant. Your task is to suggest {n} highly insightful questions "
    #         f"a user might ask after reading the following document:\n\n"
    #         f"{text}\n\n"
    #         "Return them as a numbered list."
    #     )

    #     try:
    #         llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0,groq_api_key=self.groq_api_key)
    #         raw_response = llm.invoke(prompt)
    #         # Extract content from the AI message object
    #         response_text = getattr(raw_response, "content", str(raw_response))
    #         lines = response_text.splitlines()
    #         print(lines)
    #         questions = [line.strip("1234567890.-)• ").strip() for line in lines if "?" in line]
    #         return questions[:n]

    #     except Exception as e:
    #         print(f"[❌ Error generating questions]: {e}")
    #         return ["(Failed to generate suggested questions)"] 

    # def get_suggested_questions(self) -> List[str]:
    #     return self.suggested_questions