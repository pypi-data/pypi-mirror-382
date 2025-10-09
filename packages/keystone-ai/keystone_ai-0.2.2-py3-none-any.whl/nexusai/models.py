"""Pydantic data models for Nexus AI SDK."""

from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# Task models
class Task(BaseModel):
    """Task model for async operations."""

    task_id: str = Field(..., description="Unique task identifier")
    status: Literal["pending", "queued", "running", "completed", "failed"] = Field(
        ..., description="Current task status"
    )
    task_type: Optional[str] = Field(None, description="Type of task")
    created_at: Optional[datetime] = Field(None, description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    finished_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    progress: Optional[int] = Field(None, description="Task progress percentage (0-100)")
    output: Optional[Dict[str, Any]] = Field(None, description="Task output data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")


# Image models
class Image(BaseModel):
    """Image generation result."""

    image_url: str = Field(..., description="URL of the generated image")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    revised_prompt: Optional[str] = Field(None, description="Revised prompt used for generation")


# Text models
class Usage(BaseModel):
    """Token usage information."""

    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")


class TextResponse(BaseModel):
    """Text generation response."""

    text: str = Field(..., description="Generated text content")
    usage: Optional[Usage] = Field(None, description="Token usage information")
    model: Optional[str] = Field(None, description="Model used for generation")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")


# Session models
class Message(BaseModel):
    """Chat message in a session."""

    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SessionResponse(BaseModel):
    """Response from a session invoke call."""

    session_id: str = Field(..., description="Session identifier")
    response: Message = Field(..., description="Assistant's response message")
    usage: Optional[Usage] = Field(None, description="Token usage information")


class SessionModel(BaseModel):
    """Session metadata model."""

    id: Optional[int] = Field(None, description="Database ID")
    session_id: str = Field(..., description="Unique session identifier")
    agent_type: str = Field(..., description="Type of agent")
    agent_config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    name: Optional[str] = Field(None, description="Session name")
    is_active: bool = Field(True, description="Whether session is active")
    created_at: Optional[datetime] = Field(None, description="Session creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Session last update timestamp")


# Audio models
class TranscriptionResponse(BaseModel):
    """Speech-to-text transcription response."""

    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Transcription segments")


class TTSResponse(BaseModel):
    """Text-to-speech response."""

    audio_url: str = Field(..., description="URL of the generated audio")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")


# File models
class FileMetadata(BaseModel):
    """File metadata model."""

    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size: int = Field(..., description="File size in bytes")
    created_at: Optional[datetime] = Field(None, description="Upload timestamp")

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        """Parse datetime, handling trailing 'Z' suffix."""
        if isinstance(v, str) and v.endswith("Z"):
            # Remove trailing 'Z' and parse
            v = v[:-1]
        return v


class FileListResponse(BaseModel):
    """File list response with pagination."""

    files: List["FileMetadata"] = Field(..., description="List of files")
    total: int = Field(..., description="Total number of files")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


# Knowledge base models
class KnowledgeBase(BaseModel):
    """Knowledge base model."""

    kb_id: str = Field(..., description="Unique knowledge base identifier")
    name: str = Field(..., description="Knowledge base name")
    description: Optional[str] = Field(None, description="Knowledge base description")
    embedding_model: str = Field(..., description="Embedding model used")
    chunk_size: int = Field(..., description="Document chunk size")
    chunk_overlap: int = Field(..., description="Document chunk overlap")
    document_count: int = Field(0, description="Number of documents")
    total_chunks: Optional[int] = Field(None, description="Total number of chunks")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class DocumentMetadata(BaseModel):
    """Document metadata in knowledge base."""

    doc_id: str = Field(..., description="Unique document identifier")
    kb_id: str = Field(..., description="Knowledge base identifier")
    filename: str = Field(..., description="Document filename")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    processing_status: Literal["queued", "processing", "completed", "failed"] = Field(
        ..., description="Processing status"
    )
    chunk_count: int = Field(0, description="Number of chunks")
    uploaded_at: Optional[datetime] = Field(None, description="Upload timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")
    content_preview: Optional[str] = Field(None, description="Content preview")
    error: Optional[str] = Field(None, description="Error message if failed")


class SearchResult(BaseModel):
    """Search result from knowledge base."""

    chunk_id: str = Field(..., description="Chunk identifier")
    doc_id: str = Field(..., description="Document identifier")
    kb_id: str = Field(..., description="Knowledge base identifier")
    content: str = Field(..., description="Chunk content")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response from knowledge base search."""

    query: str = Field(..., description="Search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
