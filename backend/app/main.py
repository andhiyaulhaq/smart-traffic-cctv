from fastapi import FastAPI

app = FastAPI(title="Smart Traffic CCTV API")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running!"}
