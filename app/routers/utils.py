import requests
from fastapi import APIRouter

router = APIRouter(tags=["Utils"])

@router.get("/ipinfo")
def ipinfo():
    try:
        r = requests.get("https://ipapi.co/json/")
        return r.json()
    except Exception as e:
        return {"error": str(e)}
