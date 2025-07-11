# app/rag_pipeline.py

# --- Core Imports ---
import os
import json
import pickle
import threading

# --- Third-party Imports ---
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# --- Local Application Imports ---
from . import config

# ==============================================================================
# --- 1. GLOBAL STATE VARIABLES ---
# ==============================================================================
embeddings, llm, retriever, rag_chain = None, None, None, None
doc_embeddings_cache = {}
initialization_lock = threading.Lock()
initialization_done = False

# ==============================================================================
# --- 2. PIPELINE INITIALIZATION ---
# ==============================================================================
def get_rag_pipeline_status():
    return initialization_done

def initialize_rag_pipeline():
    global embeddings, llm, retriever, rag_chain, doc_embeddings_cache, initialization_done

    with initialization_lock:
        if initialization_done:
            return

        print("Initializing RAG pipeline...")
        try:
            # --- Step 1: Initialize Models ---
            embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)
            llm = GoogleGenerativeAI(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)

            # --- Step 2: Setup Retriever ---
            parent_splitter = RecursiveCharacterTextSplitter(chunk_size=config.PARENT_CHUNK_SIZE, chunk_overlap=config.PARENT_CHUNK_OVERLAP)
            child_splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHILD_CHUNK_SIZE, chunk_overlap=config.CHILD_CHUNK_OVERLAP)

            if os.path.exists(config.VECTORSTORE_PATH) and os.path.exists(config.DOCSTORE_PATH):
                print("Loading retriever components from cache...")
                vectorstore = FAISS.load_local(config.VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
                with open(config.DOCSTORE_PATH, 'rb') as f: store = pickle.load(f)
                print("✅ Cached components loaded successfully.")
            else:
                print("No cache found. Performing full one-time data ingestion...")
                os.makedirs(config.CACHE_DIR, exist_ok=True)
                loader = DirectoryLoader(config.KNOWLEDGE_BASE_PATH, glob="**/*.md", loader_cls=TextLoader, show_progress=True, use_multithreading=True, loader_kwargs={"encoding": "utf-8"})
                all_docs = loader.load()
                
                vectorstore = FAISS.from_texts(texts=["_"], embedding=embeddings) # Dummy init
                store = InMemoryStore()
                
                temp_retriever = ParentDocumentRetriever(vectorstore=vectorstore, docstore=store, child_splitter=child_splitter, parent_splitter=parent_splitter)
                print(f"Adding {len(all_docs)} documents to the retriever...")
                temp_retriever.add_documents(all_docs, ids=None)
                
                print("Saving populated components to cache...")
                temp_retriever.vectorstore.save_local(config.VECTORSTORE_PATH)
                with open(config.DOCSTORE_PATH, 'wb') as f: pickle.dump(store, f)
                print("✅ Ingestion complete and components cached.")

            retriever = ParentDocumentRetriever(vectorstore=vectorstore, docstore=store, child_splitter=child_splitter, parent_splitter=parent_splitter)

            # --- Step 3: Pre-compute Recommendation Cache ---
            print("Pre-computing embeddings for all documents for recommendations...")
            all_full_docs = list(store.mget(list(store.yield_keys())))
            for doc in all_full_docs:
                filename = os.path.basename(doc.metadata['source'])
                topic_name = os.path.splitext(filename)[0]
                doc.metadata['topic'] = topic_name
                doc_embedding = embeddings.embed_query(doc.page_content)
                doc_embeddings_cache[topic_name] = {"content": doc.page_content, "embedding": doc_embedding}
            print(f"✅ Cached {len(doc_embeddings_cache)} document embeddings.")

            # --- Step 4: Construct the Final Conversational RAG Chain ---
            
            # +++ NEW: Load few-shot examples from the external JSON file. +++
            print("Loading few-shot examples for the system prompt...")
            try:
                with open(config.FEW_SHOT_EXAMPLES_PATH, 'r', encoding='utf-8') as f:
                    few_shot_examples = json.load(f)
                # Format the examples into a single string to be injected into the prompt.
                rag_examples_formatted = "\n\n".join([
                    f"## EXAMPLE {i+1}\n\n**User's Question:**\n{ex['user_query']}\n\n**Retrieved Context Summary (for illustration):**\n{ex['context_summary']}\n\n**Your Ideal Answer:**\n{ex['assistant_answer']}"
                    for i, ex in enumerate(few_shot_examples['rag_examples'])
                ])
                print("✅ Few-shot RAG examples loaded and formatted.")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️ Warning: Could not load or parse '{config.FEW_SHOT_EXAMPLES_PATH}'. Prompts will not include examples. Error: {e}")
                rag_examples_formatted = "*(No examples loaded)*"

            # Recontextualization prompt to make follow-up questions standalone
            recontextualization_prompt = ChatPromptTemplate.from_messages([
                ("system", "Given a chat history and a follow-up question, rephrase the follow-up question to be a standalone question that captures all relevant context."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}")
            ])
            history_aware_retriever = create_history_aware_retriever(llm, retriever, recontextualization_prompt)

            # +++ NEW: Load the main system prompt from the external prompt.md file. +++
            with open(config.SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
                system_template = f.read()
            
            # +++ NEW: Inject the formatted few-shot examples into the prompt template. +++
            final_system_template = system_template.replace("{rag_examples}", rag_examples_formatted)

            # Create the final prompt template for the RAG chain.
            # This uses the dynamically loaded and formatted template.
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", final_system_template),
                MessagesPlaceholder(variable_name="chat_history"),
                # This 'user' message is a LangChain convention for the final step.
                # LangChain will automatically populate {context} from the retriever
                # and {input} from the user's query.
                ("user", "User's Question: {input}\n\nRetrieved Context:\n{context}")
            ])

            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

            initialization_done = True
            print("✅ Advanced Conversational RAG pipeline is ready.")

        except Exception as e:
            print(f"❌ CRITICAL ERROR during RAG pipeline initialization: {e}")
            import traceback
            traceback.print_exc()
            initialization_done = False