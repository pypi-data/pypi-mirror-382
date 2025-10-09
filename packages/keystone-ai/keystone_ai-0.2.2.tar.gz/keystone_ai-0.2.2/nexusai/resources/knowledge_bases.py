"""Knowledge base management resource module."""

from typing import List, Optional, Union, BinaryIO
from pathlib import Path
from nexusai.models import KnowledgeBase, DocumentMetadata, SearchResponse, Task
from nexusai._internal._poller import TaskPoller


class KnowledgeBasesResource:
    """
    Knowledge base management resource.

    Provides capabilities for creating, managing, and searching private knowledge bases
    for RAG (Retrieval-Augmented Generation) applications.
    """

    def __init__(self, client):
        """
        Initialize knowledge bases resource.

        Args:
            client: InternalClient instance
        """
        self._client = client
        self._poller = TaskPoller(client)

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        embedding_model: str = "BAAI/bge-base-zh-v1.5",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> KnowledgeBase:
        """
        Create a new knowledge base.

        Args:
            name: Knowledge base name
            description: Optional description
            embedding_model: Embedding model for vectorization.
                           Default: "BAAI/bge-base-zh-v1.5"
            chunk_size: Document chunk size in characters. Default: 1000
            chunk_overlap: Chunk overlap size in characters. Default: 200

        Returns:
            KnowledgeBase object

        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If creation fails

        Example:
            ```python
            from nexusai import NexusAIClient

            client = NexusAIClient()

            kb = client.knowledge_bases.create(
                name="Company Docs",
                description="Internal company documentation",
                chunk_size=800,
                chunk_overlap=150
            )
            print(f"Created KB: {kb.kb_id}")
            ```
        """
        request_body = {
            "name": name,
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }

        if description:
            request_body["description"] = description

        response = self._client.request(
            "POST",
            "/knowledge-bases",
            json_data=request_body,
        )

        return KnowledgeBase(**response)

    def get(self, kb_id: str) -> KnowledgeBase:
        """
        Get knowledge base details.

        Args:
            kb_id: Knowledge base ID

        Returns:
            KnowledgeBase object

        Raises:
            NotFoundError: If knowledge base doesn't exist
            APIError: If retrieval fails

        Example:
            ```python
            kb = client.knowledge_bases.get("kb_xyz789abc123")
            print(f"Documents: {kb.document_count}")
            print(f"Chunks: {kb.total_chunks}")
            ```
        """
        response = self._client.request("GET", f"/knowledge-bases/{kb_id}")
        return KnowledgeBase(**response)

    def list(self) -> List[KnowledgeBase]:
        """
        List all knowledge bases.

        Returns:
            List of KnowledgeBase objects

        Raises:
            APIError: If retrieval fails

        Example:
            ```python
            knowledge_bases = client.knowledge_bases.list()
            for kb in knowledge_bases:
                print(f"{kb.name} ({kb.document_count} docs)")
            ```
        """
        response = self._client.request("GET", "/knowledge-bases")

        # Response is a list of knowledge bases
        if isinstance(response, list):
            return [KnowledgeBase(**kb) for kb in response]
        else:
            # Fallback if wrapped in object
            return [KnowledgeBase(**kb) for kb in response.get("knowledge_bases", [])]

    def delete(self, kb_id: str) -> dict:
        """
        Delete a knowledge base and all its documents.

        Args:
            kb_id: Knowledge base ID

        Returns:
            Deletion confirmation dictionary

        Raises:
            NotFoundError: If knowledge base doesn't exist
            APIError: If deletion fails

        Example:
            ```python
            result = client.knowledge_bases.delete("kb_xyz789abc123")
            print(result["message"])
            ```
        """
        return self._client.request("DELETE", f"/knowledge-bases/{kb_id}")

    def upload_document(
        self,
        kb_id: str,
        file: Union[str, Path, BinaryIO],
        filename: Optional[str] = None,
    ) -> Task:
        """
        Upload a document to a knowledge base.

        This method uses the new two-step unified file architecture:
        1. Upload file to /api/v1/files (returns file_id)
        2. Add file_id to knowledge base via /api/v1/knowledge-bases/{kb_id}/documents

        Document processing is asynchronous. Use the returned task_id
        to poll for processing completion.

        Args:
            kb_id: Knowledge base ID
            file: File path (str or Path) or file-like object
            filename: Optional filename override

        Returns:
            Task object with queued document processing task

        Raises:
            InvalidRequestError: If file is invalid
            NotFoundError: If knowledge base doesn't exist
            APIError: If upload fails

        Example:
            ```python
            # Upload document (internally uses two-step process)
            task = client.knowledge_bases.upload_document(
                kb_id="kb_xyz789abc123",
                file="company_policy.pdf"
            )
            print(f"Task ID: {task.task_id}")

            # Poll for completion
            from time import sleep
            while True:
                result = client._internal_client.request("GET", f"/tasks/{task.task_id}")
                if result["status"] == "completed":
                    print("Document processed successfully!")
                    break
                sleep(2)
            ```
        """
        # Step 1: Upload file to unified file system
        from nexusai.resources.files import FilesResource

        files_resource = FilesResource(self._client)
        file_meta = files_resource.upload(file=file, filename=filename)

        # Step 2: Add file_id to knowledge base
        return self.add_document(kb_id=kb_id, file_id=file_meta.file_id)

    def add_document(self, kb_id: str, file_id: str) -> Task:
        """
        Add an already-uploaded file to a knowledge base.

        This is the new API method that uses the unified file architecture.
        The file must already be uploaded via client.files.upload().

        Args:
            kb_id: Knowledge base ID
            file_id: File ID from previous file upload

        Returns:
            Task object with queued document processing task

        Raises:
            InvalidRequestError: If file_id is invalid
            NotFoundError: If knowledge base or file doesn't exist
            APIError: If operation fails

        Example:
            ```python
            # Step 1: Upload file
            file_meta = client.files.upload("document.pdf")
            print(f"Uploaded file: {file_meta.file_id}")

            # Step 2: Add to knowledge base
            task = client.knowledge_bases.add_document(
                kb_id="kb_xyz789abc123",
                file_id=file_meta.file_id
            )
            print(f"Processing task: {task.task_id}")

            # You can reuse the same file_id for multiple knowledge bases
            task2 = client.knowledge_bases.add_document(
                kb_id="kb_another_kb",
                file_id=file_meta.file_id  # Same file, different KB
            )
            ```
        """
        request_body = {"file_id": file_id}

        response = self._client.request(
            "POST", f"/knowledge-bases/{kb_id}/documents", json_data=request_body
        )

        return Task(**response)

    def list_documents(self, kb_id: str) -> List[DocumentMetadata]:
        """
        List all documents in a knowledge base.

        Args:
            kb_id: Knowledge base ID

        Returns:
            List of DocumentMetadata objects

        Raises:
            NotFoundError: If knowledge base doesn't exist
            APIError: If retrieval fails

        Example:
            ```python
            documents = client.knowledge_bases.list_documents("kb_xyz789abc123")
            for doc in documents:
                print(f"{doc.filename}: {doc.processing_status}")
            ```
        """
        response = self._client.request("GET", f"/knowledge-bases/{kb_id}/documents")

        # Response is a list of documents
        if isinstance(response, list):
            return [DocumentMetadata(**doc) for doc in response]
        else:
            return [DocumentMetadata(**doc) for doc in response.get("documents", [])]

    def search(
        self,
        query: str,
        knowledge_base_ids: List[str],
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> SearchResponse:
        """
        Perform semantic search across knowledge bases.

        Args:
            query: Search query text
            knowledge_base_ids: List of knowledge base IDs to search
            top_k: Number of results to return. Default: 5
            similarity_threshold: Minimum similarity score (0-1). Default: 0.7

        Returns:
            SearchResponse with ranked results

        Raises:
            InvalidRequestError: If parameters are invalid
            APIError: If search fails

        Example:
            ```python
            # Search in knowledge base
            results = client.knowledge_bases.search(
                query="What is the vacation policy?",
                knowledge_base_ids=["kb_xyz789abc123"],
                top_k=3,
                similarity_threshold=0.75
            )

            print(f"Found {results.total_results} results")
            for result in results.results:
                print(f"[{result.similarity_score:.2f}] {result.content[:100]}...")

            # Use results for RAG
            context = "\\n\\n".join([r.content for r in results.results])
            response = client.text.generate(
                prompt=f"Based on this context:\\n{context}\\n\\nQuestion: {query}"
            )
            print(response.text)
            ```
        """
        request_body = {
            "query": query,
            "knowledge_base_ids": knowledge_base_ids,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
        }

        response = self._client.request(
            "POST",
            "/knowledge-bases/search",
            json_data=request_body,
        )

        return SearchResponse(**response)
