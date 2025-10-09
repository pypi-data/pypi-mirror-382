# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MeRetrieveResponse"]


class MeRetrieveResponse(BaseModel):
    credit_balance: int
    """Credit balance of the tenant"""

    name: str

    plan: Literal["starter", "pro", "enterprise"]
    """Plan of the tenant"""

    bcc_recipient_email: Optional[str] = None
    """BCC recipient email to deliver documents"""

    company_address: Optional[str] = None
    """Address of the company"""

    company_city: Optional[str] = None
    """City of the company"""

    company_country: Optional[str] = None
    """Country of the company"""

    company_email: Optional[str] = None
    """Email of the company"""

    company_name: Optional[str] = None
    """Name of the company"""

    company_number: Optional[str] = None
    """Company number"""

    company_zip: Optional[str] = None
    """Zip code of the company"""

    description: Optional[str] = None

    ibans: Optional[List[str]] = None
    """IBANs of the tenant"""

    peppol_ids: Optional[List[str]] = None
    """Peppol IDs of the tenant"""

    smp_registration: Optional[bool] = None
    """Whether the tenant is registered on our SMP"""

    smp_registration_date: Optional[datetime] = None
    """Date when the tenant was registered on SMP"""
