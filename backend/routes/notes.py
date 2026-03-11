from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

from database import get_db
from models.note import NoteCreate, NoteOut
from routes.auth import get_current_user

router = APIRouter(prefix="/api/crimes", tags=["notes"])


def note_to_out(doc: dict) -> NoteOut:
    return NoteOut(
        id=str(doc["_id"]),
        crime_id=doc["crime_id"],
        content=doc["content"],
        is_anonymous=doc.get("is_anonymous", True),
        author_id=None if doc.get("is_anonymous") else doc.get("author_id"),
        author_name=None if doc.get("is_anonymous") else doc.get("author_name"),
        upvotes=doc.get("upvotes", 0),
        downvotes=doc.get("downvotes", 0),
        created_at=doc.get("created_at", datetime.utcnow()),
    )


@router.get("/{crime_id}/notes", response_model=List[NoteOut])
async def get_notes(crime_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    cursor = db.notes.find({"crime_id": crime_id}).sort("upvotes", -1)
    docs = await cursor.to_list(length=100)
    return [note_to_out(d) for d in docs]


@router.post("/{crime_id}/notes", response_model=NoteOut, status_code=201)
async def add_note(
    crime_id: str,
    data: NoteCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    crime = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    if not crime:
        raise HTTPException(status_code=404, detail="Crime report not found")

    now = datetime.utcnow()
    note = {
        "crime_id": crime_id,
        "content": data.content,
        "is_anonymous": data.is_anonymous,
        "author_id": str(current_user["_id"]) if current_user and not data.is_anonymous else None,
        "author_name": current_user.get("username") if current_user and not data.is_anonymous else None,
        "upvotes": 0,
        "downvotes": 0,
        "created_at": now,
    }
    result = await db.notes.insert_one(note)
    note["_id"] = result.inserted_id

    # Increment notes count on crime
    await db.crimes.update_one({"_id": ObjectId(crime_id)}, {"$inc": {"notes_count": 1}})

    return note_to_out(note)


@router.post("/{crime_id}/notes/{note_id}/vote", response_model=NoteOut)
async def vote_note(
    crime_id: str,
    note_id: str,
    vote_type: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ObjectId.is_valid(note_id):
        raise HTTPException(status_code=400, detail="Invalid note ID")
    doc = await db.notes.find_one({"_id": ObjectId(note_id), "crime_id": crime_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Note not found")

    if vote_type == "up":
        await db.notes.update_one({"_id": ObjectId(note_id)}, {"$inc": {"upvotes": 1}})
    elif vote_type == "down":
        await db.notes.update_one({"_id": ObjectId(note_id)}, {"$inc": {"downvotes": 1}})

    updated = await db.notes.find_one({"_id": ObjectId(note_id)})
    return note_to_out(updated)
