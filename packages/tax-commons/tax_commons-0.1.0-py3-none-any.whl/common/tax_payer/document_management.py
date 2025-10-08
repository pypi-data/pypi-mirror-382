from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class DocumentManagement(BaseModel):
    """Document management information"""
    documents_folder_path: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = None # type: ignore
    has_digital_documents: bool = Field(default=False)
    has_paper_documents: bool = Field(default=False)
    document_retention_years: int = Field(default=7, ge=1, le=20)
    documents_last_updated: Optional[datetime] = None

    @validator("document_retention_years")
    def validate_retention_years(cls, v):
        if v < 1 or v > 20:
            raise ValueError("document_retention_years must be between 1 and 20")
        return v
