import httpx
import time
import hashlib
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="HS OTP Proxy", version="1.0")

# === CONFIG ===
TARGET = "https://damp-resonance-12e3.ilyasbhai869.workers.dev/"
TIMEOUT = 15


@app.get("/")
@app.post("/")
async def proxy(request: Request, number: str = None):
    # CORS
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    }

    # Handle OPTIONS preflight
    if request.method == "OPTIONS":
        return {"success": True, "message": "CORS preflight ok"}

    data = {}
    try:
        if request.method == "POST":
            data = await request.json()
        elif request.method == "GET":
            if number:
                data["number"] = number
    except Exception:
        pass

    # --- Validate ---
    number = data.get("number")
    if not number:
        return {
            "success": False,
            "message": "Please provide a number via POST JSON or ?number= in GET",
        }

    # Clean digits
    number = "".join(ch for ch in number if ch.isdigit())

    # --- Unique Request ID ---
    request_key = hashlib.md5(f"{number}{time.time()}".encode()).hexdigest()

    payload = {"number": number}

    # --- Send to Cloudflare Worker ---
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
            resp = await client.post(
                TARGET,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request: {str(e)}"
        )


@app.get("/ping")
async def ping():
    return {"success": True, "message": "HS OTP Proxy running perfectly"}