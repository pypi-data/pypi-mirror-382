"""Interactive chat pop-up application using Azure OpenAI or local Ollama.

Supports document ingestion into ChromaDB and retrieval-augmented generation.
"""

from gemini_application.application_abstract import ApplicationAbstract
import os
import time
from langchain_community.document_loaders import PyPDFLoader
from ollama import Client
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
import re


class ChatPopup(ApplicationAbstract):
    """Chat popup application for LLM interactions."""

    def __init__(self):
        """Initialize chat popup application."""
        super().__init__()

        self.azure_openai = False
        self.azure_openai_key = None
        self.azure_openai_host = None
        self.azure_openai_client = None

        self.ollama_client = None
        self.ollama_embeddings_model = None
        self.ollama_llm_model = None
        self.chroma_client = None
        self.chroma_collection = None

        # Variables
        self.langchain_api_key = None
        self.chunks = None
        self.docs_dir = None
        self.chroma_dir = None
        self.text_splitter = None
        self.prompt = None
        self.chunk_size = None
        self.collection_name = None
        self.chromadb_host = None
        self.chromadb_port = None
        self.ollama_host = None
        self.ollama_port = None
        self.similarity_threshold = None
        self.num_relevant_docs = None

    def init_parameters(self, parameters):
        """Initialize parameters."""
        for key, value in parameters.items():
            setattr(self, key, value)

        self.initialize_model()

    def calculate(self):
        """Calculate chat popup functionality."""
        return "Output calculated"

    def initialize_model(self):
        """Initialize the chat model."""
        # API key for accessing langchain model
        os.environ["LANGCHAIN_API_KEY"] = (
            self.langchain_api_key
        )

        if self.azure_openai:
            self.azure_openai_client = AzureChatOpenAI(
                azure_deployment="gpt-35-turbo",
                api_version="2023-06-01-preview",
                api_key=self.azure_openai_key,
                azure_endpoint=self.azure_openai_host,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )
            self.azure_embedding_client = AzureOpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=self.azure_openai_key,
                azure_endpoint=self.azure_openai_host
            )
        else:
            # Http ollama connection
            self.ollama_client = Client(host=f"http://{self.ollama_host}:{self.ollama_port}")

        # Http chromaDB storage, on Docker container
        self.chroma_client = chromadb.HttpClient(host=self.chromadb_host, port=self.chromadb_port)

        # Now create or retrieve the collection
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def delete_collection(self):
        """Delete the collection."""
        self.chroma_client.delete_collection(name=self.collection_name)

    def update_data(self):
        """Update data for the chat popup."""
        # Step 1: Fetch existing metadata from the collection
        tic = time.time()
        existing_sources = set()
        all_metadata = self.chroma_collection.get(include=["documents", "metadatas"])

        if "metadatas" in all_metadata:
            for meta in all_metadata["metadatas"]:
                if meta and "source" in meta:
                    existing_sources.add(meta["source"])
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Fetched existing metadata from collection ({elapsed_time:.5f} s)")

        # Step 2: List all files and filter out existing ones
        if not os.path.exists(self.docs_dir):
            print("Model: No directory found")
            return

        all_files = [
            f for f in os.listdir(self.docs_dir)
            if os.path.isfile(os.path.join(self.docs_dir, f))
        ]
        new_files = [f for f in all_files if f not in existing_sources]
        print(f"Model: Found {len(new_files)} new files to process")

        # Step 3: Read only new files
        tic = time.time()
        docs_data = self.readfiles(self.docs_dir, filenames=new_files)
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: Documents read ({elapsed_time:.5f} s)")

        # Step 4: Process and add new files to ChromaDB
        tic = time.time()
        for filename, text in docs_data.items():
            chunks = self.chunksplitter(text, self.chunk_size)
            embeds = self.get_embedding_list(chunks)
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename} for _ in range(len(chunks))]

            # Add the embeddings to the chromadb
            self.chroma_collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeds,
                metadatas=metadatas
            )
        toc = time.time()
        elapsed_time = toc - tic
        print(f"Model: New files processed ({elapsed_time:.5f} s)")

        # Step 5: Delete missing files for searching
        missing_files = [f for f in existing_sources if f not in all_files]
        for missing_file in missing_files:
            self.chroma_collection.delete(where={"source": missing_file})
            print(f"Model: Delete data {missing_file}")

    def get_embedding(self, user_message: str):
        """Get embedding for user message."""
        if self.azure_openai:
            embedding = self.azure_embedding_client.embed_query(user_message)
        else:
            response = self.ollama_client.embeddings(
                model=self.ollama_embeddings_model,
                prompt=user_message
            )
            embedding = response['embedding']
        return embedding

    def get_response(self, prompt: str) -> str:
        """Get response from the model."""
        if self.azure_openai:
            print("using azure open AI...")
            response = self.azure_openai_client.invoke(prompt)
            response_str = response.content
        else:
            print("using ollama...")
            response = self.ollama_client.generate(
                model=self.ollama_llm_model,
                prompt=prompt,
                stream=False
            )
            response_str = response.model_dump().get("response", "")
        # Extract text from response
        return response_str

    def filter_context(self, context):
        """Filter context for relevance."""
        # the function returns the documents with similarity > self.similarity_threshold
        filtered_docs = []
        filtered_metas = []
        filtered_ids = []
        similarities = []

        # Flattened lists (single query embedding assumed)
        documents = context["documents"][0]
        metadatas = context["metadatas"][0]
        ids = context["ids"][0]
        distances = context["distances"][0]
        print(f'conext = {context}')

        for doc, meta, doc_id, distance in zip(documents, metadatas, ids, distances):
            similarity = 1 - distance
            if similarity >= self.similarity_threshold:
                filtered_docs.append(doc)
                filtered_metas.append(meta)
                filtered_ids.append(doc_id)
                similarities.append(similarity)

        print(f'similarities = {similarities}')

        return {
            "documents": filtered_docs,
            "metadatas": filtered_metas,
            "ids": filtered_ids,
            "similarities": similarities
        }

    def process_prompt(self, user_message):
        """Process user prompt."""
        print("processing prompt...")

        # Get embedding of the user query
        tic = time.time()

        query_embed = self.get_embedding(user_message)
        toc = time.time()
        print(f"Model: Embeddings retrieved from user query ({toc - tic:.5f} s)")

        # Retrieve relevant documents
        context = self.chroma_collection.query(
            query_embeddings=query_embed,
            n_results=self.num_relevant_docs,
            include=["documents", "metadatas", "distances"]
        )
        filtered_context = self.filter_context(context)

        documents = filtered_context["documents"]
        ids = filtered_context["ids"]
        metadatas = filtered_context["metadatas"]

        # Build prompt
        related_text = "\n\n".join(documents)
        # prompt = self.prompt.format(question=user_message, context=related_text)
        prompt = f"Use the following pieces of retrieved context to answer the question. " \
                 f"If you don't know the answer, just say that you don't know. " \
                 f"Context: {related_text}\n\nQuestion: {user_message}\nAnswer:"

        # Generate response
        tic = time.time()
        response = self.get_response(prompt)
        toc = time.time()
        print(f"Model: generated response ({toc - tic:.5f} s)")

        # Format shortened citations
        short_citations = []
        short_sources = []

        if not response == "I don't know.":
            for i, meta in enumerate(metadatas):
                short_citations.append(ids[i])
                short_sources.append(meta['source'])

        return {
            "answer": response,
            "citations": short_citations,
            "sources": short_sources
        }

    def get_embedding_list(self, chunks: list[str]):
        """Get embedding list for chunks."""
        if self.azure_openai:
            embeddings = self.azure_embedding_client.embed_documents(chunks)
        else:
            # Embed all chunks at the same time
            response = self.ollama_client.embed(
                model=self.ollama_embeddings_model,
                input=chunks
            )
            embeddings = response.get('embeddings', [])

        return embeddings

    def readfiles(self, docs_dir, filenames=None):
        """Read files from directory."""
        text_contents = {}

        # Use provided filenames or list all from directory
        if filenames is None:
            filenames = os.listdir(docs_dir)

        for filename in filenames:
            file_path = os.path.join(docs_dir, filename)

            if not os.path.isfile(file_path):
                continue

            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                text_contents[filename] = content

            elif filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                content = "\n".join(doc.page_content for doc in documents)
                text_contents[filename] = content

        return text_contents

    def chunksplitter(self, text, chunk_size):
        """Split text into chunks."""
        words = re.findall(r'\S+', text)

        chunks = []
        current_chunk = []
        word_count = 0

        for word in words:
            current_chunk.append(word)
            word_count += 1

            if word_count >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                word_count = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
