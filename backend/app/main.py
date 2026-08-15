from fastapi import FastAPI

app = FastAPI(title="Filing Cabinet API")


@app.get("/health")
def health_check():
    return {"status": "ok"}