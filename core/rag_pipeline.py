from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
import os

class RAGPipeline:
    def __init__(self, retriever, groq_api_key, model="openai/gpt-oss-120b"):
        self.retriever = retriever
        self.llm = ChatGroq(model=model, temperature=0.1, api_key=groq_api_key)
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
                "You are a highly factual assistant.\n"
                "Answer questions using only the information explicitly provided in the context.\n"
                "- Do not rely on outside knowledge.\n"
                "- Do not make assumptions or guesses.\n"
                "- If the answer cannot be determined from the provided context, respond with:\n"
                "  'I don't know based on the provided context.'\n"
                "- Cite the source of your answer by **copying exactly** the citation tags provided in the context, e.g., [Final_FREQUENTLY_ASKED_QUESTIONS_-PATENT.pdf, Page 1].\n"
                "Respond clearly and concisely based strictly on the context."
            ),
            ("human",
                "Context: {context}\n"
                "Conversation history:\n{history}\n\n"
                "Question:\n{question}"
            )
        ])
        self.output_parser = StrOutputParser()

    # def format_docs(self, docs):
    #     return "\n\n".join(doc.page_content for doc in docs)
    def format_docs(self, docs):
        formatted = []
        for i, doc in enumerate(docs, start=1):
            filename = os.path.basename(doc.metadata.get("source", f"Doc {i}"))
            print(filename)
            page = doc.metadata.get("page", None)
            citation = f"{filename}, Page {page}" if page is not None else filename
            content = doc.page_content.strip()
            formatted.append(f"[{citation}]:\n{content}")
        return "\n\n".join(formatted)



    def format_history(self, history):
        return "\n".join(
            f"{'User' if i['role'] == 'human' else 'AI'}: {i['content']}"
            for i in history
        )
    
    def get_response(self, question, history):
        docs = self.retriever.invoke(question)
        context = self.format_docs(docs)
        formatted_history = self.format_history(history)
    
        # print("Retrieved Docs:\n", [doc.page_content for doc in docs])
        # print("Formatted Context:\n", context)
        # print("Formatted History:\n", formatted_history)
    
        inputs = {
            "context": context,
            "history": formatted_history,
            "question": question,
        }
    
        formatted_prompt = self.prompt.format_prompt(**inputs)
        print("📝 Final Prompt:\n", formatted_prompt.to_string())
    
        result = self.llm.invoke(formatted_prompt.to_messages())
        return self.output_parser.invoke(result)

    
