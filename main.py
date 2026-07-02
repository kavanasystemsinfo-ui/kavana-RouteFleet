from fastapi import FastAPI

app = FastAPI(title="Kavana Logistic", description="Optimización de rutas de reparto")

@app.get("/")
async def root():
    return {"message": "Kavana Logistic API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
