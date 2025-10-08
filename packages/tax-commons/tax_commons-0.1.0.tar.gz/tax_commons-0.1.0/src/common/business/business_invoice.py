from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class BusinessInvoice(BaseModel):
    """Vendor/payee details for tax documentation"""
    vendor_name: str = Field(..., description="Legal name of vendor/payee")
    vendor_tax_id: Optional[str] = Field(None, description="Vendor's tax ID or registration number")
    vendor_address: Optional[str] = Field(None, description="Vendor's business address")
    vendor_country: Optional[str] = Field(None, description="Vendor's country")
    vendor_phone: Optional[str] = Field(None, description="Vendor contact phone")
    vendor_email: Optional[str] = Field(None, description="Vendor contact email")
    invoice_number: Optional[str] = Field(None, description="Invoice or receipt number")
    requires_tax_form: bool = Field(False, description="Whether vendor requires tax reporting form")
    tax_form_type: Optional[str] = Field(None, description="Type of tax form required (e.g., 1099, T4A, etc.)")
