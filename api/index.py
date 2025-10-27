import httpx
import json
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="HS OTP Proxy", version="1.0")

# === CONFIG ===
TARGET_URL = "https://damp-resonance-12e3.ilyasbhai869.workers.dev/"

@app.options("/{path:path}")
async def options_handler():
    return {"status": "ok"}

@app.post("/")
@app.get("/")
async def proxy(request: Request, number: str = None):
    # --- Read input ---
    try:
        if request.method == "POST":
            body = await request.body()
            data = json.loads(body.decode("utf-8") or "{}")
        else:
            data = {}
    except Exception:
        data = {}

    # --- Support GET ?number= ---
    if not data and number:
        data = {"number": number}

    # --- Validate payload ---
    if not data or "number" not in data or not data["number"]:
        raise HTTPException(
            status_code=400,
            detail="Please provide a number via POST JSON or ?number= in GET"
        )

    # --- Forward to target Cloudflare Worker ---
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            response = await client.post(TARGET_URL, headers=headers, json=data)
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Target server timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request: {str(e)}")


@app.get("/ping")
async def ping():
    return {"success": True, "message": "HS OTP Proxy running perfectly"}
