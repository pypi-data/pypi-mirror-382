"""Pydantic models for Conceptual API responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel






class ApiResponse(BaseModel):
    code: int
    message: str




class ErrorResponse(ApiResponse):
    error: str
    errors: Optional[Dict[str, List[str]]] = None