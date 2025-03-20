import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AutoDeploy API",
    description="API for AutoDeploy",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/health")
async def health_check():
    return {"online": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
