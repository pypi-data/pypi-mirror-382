from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, constr, validator


class Preferences(BaseModel):
    # Communication Channel Preferences
    prefers_email: bool = Field(default=True)
    prefers_sms: bool = Field(default=False)
    prefers_phone: bool = Field(default=False)
    prefers_mail: bool = Field(default=False)
    prefers_secure_portal: bool = Field(default=False)
    
    # Notification Preferences
    notify_tax_deadlines: bool = Field(default=True)
    notify_payment_due: bool = Field(default=True)
    notify_refund_status: bool = Field(default=True)
    notify_document_ready: bool = Field(default=True)
    notify_account_updates: bool = Field(default=True)
    notify_marketing: bool = Field(default=False)
    notify_newsletter: bool = Field(default=False)
    notify_tax_tips: bool = Field(default=True)
    
    # Frequency Preferences
    notification_frequency: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = Field(default="As needed") # type: ignore
    summary_frequency: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = Field(default="Monthly") # type: ignore
    
    # Language & Accessibility
    preferred_language: constr(strip_whitespace=True, min_length=2, max_length=50) = Field(default="English") # type: ignore
    requires_accessibility_features: bool = Field(default=False)
    large_print_documents: bool = Field(default=False)
    screen_reader_compatible: bool = Field(default=False)
    
    # Document Preferences
    document_format: Optional[constr(strip_whitespace=True, min_length=1, max_length=20)] = Field(default="PDF") # type: ignore
    electronic_signature: bool = Field(default=True)
    paperless_billing: bool = Field(default=True)
    auto_download_documents: bool = Field(default=False)
    
    # Privacy & Security
    two_factor_authentication: bool = Field(default=False)
    biometric_login: bool = Field(default=False)
    share_data_with_cra: bool = Field(default=True)
    allow_third_party_access: bool = Field(default=False)
    marketing_consent: bool = Field(default=False)
    data_sharing_consent: bool = Field(default=False)
    
    # Time & Scheduling
    timezone: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = Field(default="America/Toronto") # type: ignore
    preferred_contact_time: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    appointment_reminder_hours: int = Field(default=24, ge=1, le=168)
    
    # Tax Filing Preferences
    auto_file_returns: bool = Field(default=False)
    express_notice_of_assessment: bool = Field(default=True)
    direct_deposit: bool = Field(default=True)
    auto_calculate_instalments: bool = Field(default=True)
    
    # Additional Settings
    show_tax_tips: bool = Field(default=True)
    save_draft_automatically: bool = Field(default=True)
    keep_login_active: bool = Field(default=False)
    session_timeout_minutes: int = Field(default=30, ge=5, le=120)
    
    # Notes
    preference_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None # type: ignore 
    
    # Audit Fields
    created_by: constr(strip_whitespace=True, min_length=1, max_length=255) # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255) # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
