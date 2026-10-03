from fastapi import FastAPI

app = FastAPI(
    title="Traumverse API",
    description="Knowledge-to-experience learning platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "alive",
        "project": "Traumverse",
        "version": "0.1.0",
    }