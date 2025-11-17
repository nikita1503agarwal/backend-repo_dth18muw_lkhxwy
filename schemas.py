"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.

Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Reservation -> "reservation" collection
- Review -> "review" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ----------------------------------------------------------------------------
# Core business schemas for FMRENTALPRESTIGE
# ----------------------------------------------------------------------------

class Reservation(BaseModel):
    """
    Reservation collection schema
    Collection name: "reservation"
    """
    code: str = Field(..., description="Codice prenotazione univoco")
    nome: str = Field(..., description="Nome del conducente")
    cognome: str = Field(..., description="Cognome del conducente")
    email: EmailStr = Field(..., description="Email di contatto")
    telefono: str = Field(..., description="Telefono/WhatsApp")

    auto: str = Field(..., description="Modello dell'auto richiesta")
    ritiro_data: str = Field(..., description="Data e ora di ritiro ISO (YYYY-MM-DD HH:mm)")
    riconsegna_data: str = Field(..., description="Data e ora di riconsegna ISO")
    ritiro_luogo: str = Field(..., description="Luogo di ritiro")
    riconsegna_luogo: str = Field(..., description="Luogo di riconsegna")

    messaggio: Optional[str] = Field(None, description="Note aggiuntive")
    sorgente: Optional[str] = Field(None, description="Canale di provenienza (sito, instagram, tiktok)")

    stato: str = Field("in_review", description="Stato prenotazione: in_review, confermata, rifiutata")
    check_in_status: str = Field("not_checked_in", description="Stato check-in: not_checked_in, checked_in")
    check_in_at: Optional[datetime] = Field(None, description="Timestamp del check-in")


class Review(BaseModel):
    """
    Review collection schema
    Collection name: "review"
    """
    nome: str = Field(..., description="Nome del cliente")
    rating: int = Field(..., ge=1, le=5, description="Valutazione 1-5")
    commento: str = Field(..., description="Testo della recensione")
    fonte: Optional[str] = Field(None, description="Piattaforma: Google, Instagram, TikTok")

# You can keep adding more schemas as needed
