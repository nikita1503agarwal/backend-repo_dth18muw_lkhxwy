import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Reservation, Review

app = FastAPI(title="FMRENTALPRESTIGE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FMRENTALPRESTIGE Backend attivo"}

@app.get("/test")
def test_database():
    """Verifica connessione database"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ----------------------------------------------------------------------------
# Booking endpoints
# ----------------------------------------------------------------------------

class ReservationCreate(BaseModel):
    nome: str
    cognome: str
    email: EmailStr
    telefono: str
    auto: str
    ritiro_data: str
    riconsegna_data: str
    ritiro_luogo: str
    riconsegna_luogo: str
    messaggio: Optional[str] = None
    sorgente: Optional[str] = None

@app.post("/api/reservations")
def create_reservation(payload: ReservationCreate):
    # Simple unique code with timestamp
    code = f"FM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    reservation = Reservation(
        code=code,
        nome=payload.nome,
        cognome=payload.cognome,
        email=payload.email,
        telefono=payload.telefono,
        auto=payload.auto,
        ritiro_data=payload.ritiro_data,
        riconsegna_data=payload.riconsegna_data,
        ritiro_luogo=payload.ritiro_luogo,
        riconsegna_luogo=payload.riconsegna_luogo,
        messaggio=payload.messaggio,
        sorgente=payload.sorgente,
    )
    inserted_id = create_document("reservation", reservation)
    return {"success": True, "code": code, "id": inserted_id}

@app.get("/api/reservations")
def list_reservations(limit: int = 50):
    docs = get_documents("reservation", limit=limit)
    # Make _id JSON serializable
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}

@app.post("/api/checkin/{code}")
def do_checkin(code: str):
    # Mark reservation as checked-in
    if db is None:
        raise HTTPException(status_code=500, detail="Database non disponibile")
    res = db["reservation"].find_one({"code": code})
    if not res:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    db["reservation"].update_one({"_id": res["_id"]}, {"$set": {"check_in_status": "checked_in", "check_in_at": datetime.utcnow()}})
    return {"success": True}

# ----------------------------------------------------------------------------
# Reviews endpoints
# ----------------------------------------------------------------------------
class ReviewCreate(BaseModel):
    nome: str
    rating: int = Field(ge=1, le=5)
    commento: str
    fonte: Optional[str] = None

@app.post("/api/reviews")
def create_review(payload: ReviewCreate):
    review = Review(**payload.model_dump())
    inserted_id = create_document("review", review)
    return {"success": True, "id": inserted_id}

@app.get("/api/reviews")
def list_reviews(limit: int = 12):
    docs = get_documents("review", limit=limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return {"items": docs}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
