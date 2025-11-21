import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Speaker, Event, TicketOrder, Highlight

app = FastAPI(title="RSCOE E-Club E-Summit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert ObjectId to str

def serialize_doc(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    # Convert datetime fields to isoformat
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


@app.get("/")
def read_root():
    return {"message": "RSCOE E-Club E-Summit Backend Running"}


@app.get("/test")
def test_database():
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
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Speakers
@app.post("/api/speakers", response_model=dict)
def create_speaker(speaker: Speaker):
    try:
        sid = create_document("speaker", speaker)
        return {"id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speakers", response_model=List[dict])
def list_speakers():
    try:
        docs = get_documents("speaker")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Events
@app.post("/api/events", response_model=dict)
def create_event(event: Event):
    try:
        eid = create_document("event", event)
        return {"id": eid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events", response_model=List[dict])
def list_events():
    try:
        docs = get_documents("event")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ticket Orders
@app.post("/api/tickets", response_model=dict)
def create_ticket(order: TicketOrder):
    try:
        # Basic amount calculation fallback if not provided
        if order.amount_paid == 0 and order.quantity > 0:
            # Attempt to fetch event price
            evt = db.event.find_one({"_id": ObjectId(order.event_id)}) if db else None
            price = float(evt.get("price", 0)) if evt else 0.0
            order.amount_paid = price * order.quantity
        oid = create_document("ticketorder", order)
        return {"id": oid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets", response_model=List[dict])
def list_tickets():
    try:
        docs = get_documents("ticketorder")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Highlights (last year details)
@app.post("/api/highlights", response_model=dict)
def create_highlight(h: Highlight):
    try:
        hid = create_document("highlight", h)
        return {"id": hid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/highlights", response_model=List[dict])
def list_highlights():
    try:
        docs = get_documents("highlight")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
