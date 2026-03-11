from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from database import get_db
from models.crime import CrimeReportCreate, CrimeReportUpdate, CrimeReportOut, VoteModel, HeatmapPoint
from routes.auth import get_current_user, require_user

router = APIRouter(prefix="/api/crimes", tags=["crimes"])

CATEGORY_WEIGHTS = {
    "চাঁদাবাজি": 3,
    "ডাকাতি": 4,
    "হামলা": 4,
    "চুরি": 2,
    "হয়রানি": 2,
    "মাদক": 2,
    "সন্দেহজনক": 1,
}


def calc_trust_score(doc: dict) -> float:
    score = doc.get("upvotes", 0) * 1.0
    score -= doc.get("downvotes", 0) * 1.5
    score += len(doc.get("evidence_urls", [])) * 2.0
    if doc.get("reporter_reputation", 0) > 10:
        score += 5.0
    return max(0.0, round(score, 2))


def doc_to_out(doc: dict, current_user_id: Optional[str] = None) -> CrimeReportOut:
    voters = doc.get("voters", {})
    user_vote = None
    if current_user_id:
        user_vote = voters.get(current_user_id)
    # is_owner uses the real reporter_id from DB regardless of is_anonymous
    is_owner = bool(current_user_id and doc.get("reporter_id") and doc.get("reporter_id") == current_user_id)
    return CrimeReportOut(
        id=str(doc["_id"]),
        category=doc["category"],
        description=doc["description"],
        location=doc["location"],
        incident_time=doc["incident_time"],
        is_anonymous=doc.get("is_anonymous", True),
        reporter_id=None if doc.get("is_anonymous") else doc.get("reporter_id"),
        reporter_name=None if doc.get("is_anonymous") else doc.get("reporter_name"),
        evidence_urls=doc.get("evidence_urls", []),
        upvotes=doc.get("upvotes", 0),
        downvotes=doc.get("downvotes", 0),
        trust_score=doc.get("trust_score", 0.0),
        status=doc.get("status", "active"),
        notes_count=doc.get("notes_count", 0),
        created_at=doc.get("created_at", datetime.utcnow()),
        user_vote=user_vote,
        is_owner=is_owner,
    )


@router.get("", response_model=dict)
async def list_crimes(
    category: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: float = 10.0,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    my_posts: bool = False,
    page: int = 1,
    limit: int = 20,
    db=Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    query: dict = {"status": "active"}

    if my_posts and current_user:
        query["reporter_id"] = str(current_user["_id"])

    if category:
        query["category"] = category

    if from_date or to_date:
        query["incident_time"] = {}
        if from_date:
            query["incident_time"]["$gte"] = from_date
        if to_date:
            query["incident_time"]["$lte"] = to_date

    if lat is not None and lng is not None:
        query["location_point"] = {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": int(radius_km * 1000),
            }
        }

    skip = (page - 1) * limit
    total = await db.crimes.count_documents(query)
    cursor = db.crimes.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)

    uid = str(current_user["_id"]) if current_user else None
    crimes = [doc_to_out(d, uid) for d in docs]

    return {"total": total, "page": page, "limit": limit, "crimes": [c.model_dump() for c in crimes]}


@router.post("", response_model=CrimeReportOut, status_code=201)
async def create_crime(
    data: CrimeReportCreate,
    db=Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    now = datetime.utcnow()
    doc = {
        "category": data.category,
        "description": data.description,
        "location": data.location.model_dump(),
        "location_point": {
            "type": "Point",
            "coordinates": [data.location.lng, data.location.lat],
        },
        "incident_time": data.incident_time,
        "is_anonymous": data.is_anonymous,
        "reporter_id": str(current_user["_id"]) if current_user else None,
        "reporter_name": current_user.get("username") if current_user and not data.is_anonymous else None,
        "reporter_reputation": current_user.get("reputation", 0) if current_user else 0,
        "evidence_urls": data.evidence_urls,
        "upvotes": 0,
        "downvotes": 0,
        "voters": {},
        "trust_score": 0.0,
        "status": "active",
        "notes_count": 0,
        "created_at": now,
    }
    # Calculate initial trust score
    doc["trust_score"] = calc_trust_score(doc)

    result = await db.crimes.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Update reporter stats
    if current_user:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"reports_submitted": 1}},
        )

    uid = str(current_user["_id"]) if current_user else None
    return doc_to_out(doc, uid)


@router.get("/heatmap", response_model=List[HeatmapPoint])
async def get_heatmap(
    category: Optional[str] = None,
    db=Depends(get_db),
):
    query: dict = {"status": "active"}
    if category:
        query["category"] = category

    cursor = db.crimes.find(query, {"location": 1, "category": 1, "trust_score": 1})
    docs = await cursor.to_list(length=2000)

    points = []
    for d in docs:
        loc = d.get("location", {})
        lat = loc.get("lat")
        lng = loc.get("lng")
        if lat is not None and lng is not None:
            weight = max(1.0, d.get("trust_score", 1.0))
            points.append(HeatmapPoint(lat=lat, lng=lng, weight=weight, category=d.get("category", "")))
    return points


@router.get("/{crime_id}", response_model=CrimeReportOut)
async def get_crime(
    crime_id: str,
    db=Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Crime report not found")
    uid = str(current_user["_id"]) if current_user else None
    return doc_to_out(doc, uid)


@router.put("/{crime_id}", response_model=CrimeReportOut)
async def update_crime(
    crime_id: str,
    data: CrimeReportUpdate,
    db=Depends(get_db),
    current_user: dict = Depends(require_user),
):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if doc.get("reporter_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="শুধু রিপোর্টকারী সম্পাদনা করতে পারবে")

    changes: dict = {}
    if data.category is not None:
        changes["category"] = data.category
    if data.description is not None:
        changes["description"] = data.description
    if data.location is not None:
        changes["location"] = data.location.model_dump()
        changes["location_point"] = {
            "type": "Point",
            "coordinates": [data.location.lng, data.location.lat],
        }
    if data.incident_time is not None:
        changes["incident_time"] = data.incident_time
    if data.is_anonymous is not None:
        changes["is_anonymous"] = data.is_anonymous
        if data.is_anonymous:
            # keep reporter_id for ownership tracking; only hide reporter_name publicly
            changes["reporter_name"] = None
        else:
            changes["reporter_name"] = current_user.get("username")
    if data.evidence_urls is not None:
        changes["evidence_urls"] = data.evidence_urls
    changes["updated_at"] = datetime.utcnow()

    await db.crimes.update_one({"_id": ObjectId(crime_id)}, {"$set": changes})
    updated = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    return doc_to_out(updated, str(current_user["_id"]))


@router.delete("/{crime_id}", status_code=204)
async def delete_crime(
    crime_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(require_user),
):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if doc.get("reporter_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="শুধু রিপোর্টকারী মুছতে পারবে")
    await db.crimes.delete_one({"_id": ObjectId(crime_id)})
    await db.notes.delete_many({"crime_id": crime_id})
    if current_user:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"reports_submitted": -1}},
        )


@router.post("/{crime_id}/vote", response_model=CrimeReportOut)
async def vote_on_crime(
    crime_id: str,
    vote: VoteModel,
    db=Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    if not ObjectId.is_valid(crime_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    doc = await db.crimes.find_one({"_id": ObjectId(crime_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    if vote.vote_type not in ("up", "down"):
        raise HTTPException(status_code=400, detail="vote_type must be 'up' or 'down'")

    voters = doc.get("voters", {})
    uid = str(current_user["_id"]) if current_user else None
    voter_key = uid or "anon"

    prev_vote = voters.get(voter_key)
    upvotes = doc.get("upvotes", 0)
    downvotes = doc.get("downvotes", 0)

    # Remove previous vote
    if prev_vote == "up":
        upvotes = max(0, upvotes - 1)
    elif prev_vote == "down":
        downvotes = max(0, downvotes - 1)

    # Toggle or apply new vote
    if prev_vote == vote.vote_type:
        voters.pop(voter_key, None)
    else:
        voters[voter_key] = vote.vote_type
        if vote.vote_type == "up":
            upvotes += 1
        else:
            downvotes += 1

    updated = {**doc, "upvotes": upvotes, "downvotes": downvotes, "voters": voters}
    updated["trust_score"] = calc_trust_score(updated)

    await db.crimes.update_one(
        {"_id": ObjectId(crime_id)},
        {"$set": {"upvotes": upvotes, "downvotes": downvotes, "voters": voters, "trust_score": updated["trust_score"]}},
    )
    updated["_id"] = doc["_id"]
    return doc_to_out(updated, uid)
