from fastapi import FastAPI

app = FastAPI(
    title="Sweet Shop API",
    description="API for managing a sweet shop inventory and sales.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sweet Shop API"}