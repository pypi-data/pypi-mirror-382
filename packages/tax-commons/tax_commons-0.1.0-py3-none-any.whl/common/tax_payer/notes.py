from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class TaxpayerNotes(BaseModel):
    """Notes and comments"""
    internal_notes: Optional[constr(strip_whitespace=True, max_length=5000)] = None # type: ignore
    client_notes: Optional[constr(strip_whitespace=True, max_length=2000)] = None # type: ignore
    special_instructions: Optional[constr(strip_whitespace=True, max_length=1000)] = None # type: ignore
