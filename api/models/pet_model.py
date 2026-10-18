"""Pydantic data models for API serialization and deserialization."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Category(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Tag(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class PetModel(BaseModel):
    id: Optional[int] = None
    category: Optional[Category] = None
    name: str
    photoUrls: List[str] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)
    status: Optional[str] = "available"


class ApiResponse(BaseModel):
    code: Optional[int] = None
    type: Optional[str] = None
    message: Optional[str] = None
