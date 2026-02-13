from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import Base, engine
from app.routes import auth, datasets

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dataset Hub",
    description="A Hugging Face-like dataset platform",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(datasets.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Dataset Hub API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
