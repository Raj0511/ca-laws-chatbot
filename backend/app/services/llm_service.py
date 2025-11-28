import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.runnables import RunnablePassthrough
from app.models.chat import RoleEnum
from app.services.vector_service import get_retriever

load_dotenv()

# Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"   # free-tier friendly
)

# --- 1. History-Aware Query Rewriter Prompt ---
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Rewrite the user's message into a standalone question using the chat history. "
     "Do NOT answer. Only rewrite."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# --- 2. Final Answer Prompt ---
qa_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Chartered Accountant Law Assistant. Use the provided context to answer. "
     "If answer is not in the context, say: "
     "'I cannot answer this based on the provided Chartered Accountant Law documents.'\n\n"
     "--- CONTEXT START ---\n{context}\n--- CONTEXT END ---"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])


async def generate_response(user_message: str, chat_history: list):
    # Convert DB history → LangChain Messages
    lang_history = []
    for msg in chat_history:
        if msg.role == RoleEnum.user:
            lang_history.append(HumanMessage(content=msg.content))
        else:
            lang_history.append(AIMessage(content=msg.content))

    # Retriever
    retriever = get_retriever()

    # --- Build RAG Pipeline ---
    # Step 1: Rewrite query
    rewrite_chain = contextualize_prompt | llm | (lambda x: x.content)

    # Step 2: Retrieve using rewritten question
    rag_retriever_chain = {
    "context": lambda x: retriever.invoke(rewrite_chain.invoke({
        "input": x["input"],
        "chat_history": x["chat_history"]
    })),
    "input": lambda x: x["input"],
    "chat_history": lambda x: x["chat_history"],   # <-- FIX HERE
    }

    rag_chain = rag_retriever_chain | qa_prompt | llm

    # --- Run the RAG pipeline ---
    result = await rag_chain.ainvoke({
        "input": user_message,
        "chat_history": lang_history
    })

    return result.content
