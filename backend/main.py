# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080", # Or wherever your pywebview app might run (if serving locally)
    "file://", # For pywebview loading local HTML files
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/data")
async def get_data():
    print("Backend accessed!")
    return {"message": "Hello from the FastAPI backend!"}

if __name__ == "__main__":
    import uvicorn
    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 